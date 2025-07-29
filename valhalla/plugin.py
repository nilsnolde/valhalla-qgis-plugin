from typing import List, Optional

from qgis.PyQt.QtWidgets import QMessageBox
from qgis.PyQt.QtCore import Qt
from qgis.core import Qgis, QgsApplication
from qgis.gui import QgisInterface, QgsMessageBar
from qgis.PyQt.QtWidgets import QAction, QMenu, QToolBar

from . import PLUGIN_NAME, __version__
from .core.settings import IGNORE_PYPI, PLUGIN_VERSION, ValhallaSettings
from .exceptions import ValhallaCmdError
from .global_definitions import PYPI_PKGS, Dialogs, PyPiState
from .gui.dlg_plugin_settings import PluginSettingsDialog
from .gui.dock_routing import RoutingDockWidget
from .gui.dlg_spopt import SpoptDialog
from .processing.provider import ValhallaProvider
from .utils.misc_utils import str_to_bool
from .utils.resource_utils import check_local_lib_version, get_icon, get_pypi_lib_version, install_pypi


class ValhallaPlugin:
    def __init__(self, iface: QgisInterface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface

        self.provider = ValhallaProvider()

        self.na_toolbar: Optional[QToolBar] = None
        self.menu: Optional[QMenu] = None
        self.actions: List[QAction] = list() # type: ignore

        self.routing_dock: Optional[RoutingDockWidget] = None
        self.settings_dlg: Optional[PluginSettingsDialog] = None
        self.optimization_dlg: Optional[SpoptDialog] = None

    def add_action(self, icon, title, callback):
        action = QAction(icon, title, self.iface.mainWindow())
        action.triggered.connect(callback)
        self.menu.addAction(action)
        self.na_toolbar.addAction(action)

        self.actions.append(action)

    def initGui(self):
        """Init the user interface."""
        # Add the toolbar
        self.na_toolbar = self.iface.mainWindow().findChild(QToolBar, PLUGIN_NAME)
        if not self.na_toolbar:
            self.na_toolbar = self.iface.addToolBar(PLUGIN_NAME)
            self.na_toolbar.setObjectName(PLUGIN_NAME.replace(" ", "_").lower())

        # Setup menu
        self.menu = QMenu(PLUGIN_NAME)
        valhalla_icon = get_icon("valhalla_logo.svg")
        self.menu.setIcon(valhalla_icon)

        for title, callback, icon in (
            ("Routing Functions", self.open_routing_dlg, valhalla_icon),
            # NOTE, the below code still exists, but it's non-functional since we never came up with a graph store
            ("Settings", self.open_settings_dlg, get_icon("settings_logo.svg")),
            # ('Optimization Functions', self.open_optimization_dlg, ":images/themes/default/mActionCalculateField.svg")
        ):
            self.add_action(icon, title, callback)

        self.iface.vectorMenu().addMenu(self.menu)

        # add processing provider
        QgsApplication.processingRegistry().addProvider(self.provider)

        # try a dock widget
        self.routing_dock = RoutingDockWidget(self.iface)
        self.iface.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.routing_dock)

    def unload(self):
        """Unload the user interface."""
        for action in self.actions:
            self.iface.vectorMenu().removeAction(action)
            self.na_toolbar.removeAction(action)

        if self.provider:
            QgsApplication.processingRegistry().removeProvider(self.provider)

        self.iface.removeDockWidget(self.routing_dock)

    def open_routing_dlg(self):
        """Create and open the version dialog."""
        self.routing_dock.setVisible(not self.routing_dock.isVisible())

    def open_settings_dlg(self):
        """Create and open the settings dialog."""
        if not self.settings_dlg:
            self.settings_dlg = PluginSettingsDialog(self.iface.mainWindow())
            # self._check_libs(self.settings_dlg.status_bar)
        self.settings_dlg.open()

    def open_optimization_dlg(self):
        """Create and open the optimization dialog."""
        if not self.optimization_dlg:
            self.optimization_dlg = SpoptDialog(self.iface.mainWindow(), self.iface)
        self.optimization_dlg.open()

    def _check_libs(self, status_bar: QgsMessageBar):
        """
        Checks for local versions if they're installed and leaves it to the user to
        choose an action. Also checks for available upgrades.
        """
        missing: List[str] = list()
        upgradeable: List[str] = list()
        for lib in PYPI_PKGS:
            available_version = get_pypi_lib_version(lib)
            lib_name = f"{lib.pypi_name}=={available_version.public}"

            state = check_local_lib_version(lib, available_version)
            if state == PyPiState.NOT_INSTALLED:
                missing.append(lib_name)
            elif state == PyPiState.UPGRADEABLE:
                upgradeable.append(lib_name)

        # never mind if there's nothing to do
        if not missing and not upgradeable:
            return

        def success_notice(p):
            nonlocal status_bar
            status_bar.pushMessage(
                "Successfully installed/upgraded packages:\n{}".format("\n".join(set(p))),
                Qgis.Success,
                8,
            )

        # decide if we show a warning or not
        show_warn = not str_to_bool(
            ValhallaSettings().get(Dialogs.SETTINGS, IGNORE_PYPI)
        ) or __version__ != ValhallaSettings().get(Dialogs.SETTINGS, PLUGIN_VERSION)

        try:
            # first install in case the user didn't choose 'Ignore' before once
            if missing and show_warn:
                msg_box = QMessageBox(self.iface.mainWindow())
                msg_box.setIcon(QMessageBox.Critical)
                msg_box.setText("Optional packages can be installed:\n{}".format("\n".join(missing)))
                msg_box.setInformativeText(
                    "Do you want us to install these to take advantage of fully local analysis?"
                )
                install_btn = msg_box.addButton("Yes", QMessageBox.YesRole)
                no_btn = msg_box.addButton(QMessageBox.No)
                ignore_btn = msg_box.addButton("Ignore forever", QMessageBox.RejectRole)

                msg_box.exec()

                # don't return yet at all here, we still might to have to upgrade stuff
                if msg_box.clickedButton() == install_btn:
                    # need to do this so the UI is refreshed before it freezes
                    QgsApplication.processEvents()
                    install_pypi(missing)
                    success_notice(missing)
                elif msg_box.clickedButton() == ignore_btn:
                    ValhallaSettings().set(Dialogs.SETTINGS, IGNORE_PYPI, "True")
                    ValhallaSettings().set(Dialogs.SETTINGS, PLUGIN_VERSION, __version__)

            if upgradeable:
                ret = QMessageBox.warning(
                    self.iface.mainWindow(),
                    "Valhalla dependency upgrades",
                    "Following dependencies should be upgraded now:\n{}".format("\n".join(upgradeable)),
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.Yes,
                )
                if ret == QMessageBox.No:
                    return

                install_pypi(upgradeable)
                success_notice(upgradeable)
        except ValhallaCmdError as e:
            status_bar.pushMessage(
                f"Couldn't install the dependencies:\n{e}",
                Qgis.Critical,
                0,  # don't auto-close after timeout
            )
            return
