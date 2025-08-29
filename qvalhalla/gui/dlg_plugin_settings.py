from functools import partial
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Optional

from packaging.version import parse as Version
from qgis.core import Qgis
from qgis.gui import QgisInterface, QgsFileWidget
from qgis.PyQt.QtCore import QRect, QSize, Qt
from qgis.PyQt.QtWidgets import QDialog, QLabel, QTableWidgetItem, QToolButton, QWidget

from ..core.settings import ValhallaSettings
from ..exceptions import ValhallaCmdError
from ..global_definitions import PYPI_PKGS, Dialogs, PyPiState
from ..utils.resource_utils import (
    check_local_lib_version,
    get_default_valhalla_binary_dir,
    get_icon,
    get_pypi_lib_version,
    install_pypi,
)
from .compiled.dlg_plugin_settings_ui import Ui_PluginSettingsDialog
from .gui_utils import add_msg_bar
from .widgets.widget_graphs import GraphWidget

iface: QgisInterface


class PluginSettingsDialog(QDialog, Ui_PluginSettingsDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setupDepsTable()
        # add the graph list after the binary file picker
        self.main_layout.insertWidget(1, GraphWidget(self))
        # add a status bar last, so it's coming first in the layout
        self.status_bar = add_msg_bar(self.main_layout)

        self.ui_btn_default_binary_path.setIcon(get_icon(":images/themes/default/mIconPythonFile.svg"))
        btn_size = self.ui_binary_path.height()
        self.ui_btn_default_binary_path.setFixedSize(btn_size, btn_size)
        self.ui_btn_default_binary_path.setIconSize(QSize(btn_size - 2, btn_size - 2))
        self.ui_binary_path.setFilePath(str(ValhallaSettings().get_binary_dir()))

        # connections
        self.ui_btn_default_binary_path.clicked.connect(self._on_default_binary_path)
        self.ui_binary_path: QgsFileWidget
        self.ui_binary_path.fileChanged.connect(self._on_binary_path_change)

    def _on_binary_path_change(self, path: str):
        ValhallaSettings().set_binary_dir(Path(path))

    def _on_default_binary_path(self):
        default_path = get_default_valhalla_binary_dir()
        if not default_path:
            self.status_bar.pushMessage("pyvalhalla-weekly not installed", Qgis.Critical, 3)
            return
        ValhallaSettings().set_binary_dir(default_path)
        self.ui_binary_path.setFilePath(str(default_path))

    def setupDepsTable(self):
        """Set up deps table"""
        self.ui_deps_table.clear()
        self.ui_deps_table.setRowCount(len(PYPI_PKGS))
        self.ui_deps_table.setHorizontalHeaderLabels(["Package", "Installed", "Available", "Action"])
        for row_id, pkg in enumerate(PYPI_PKGS):
            # get the versions and the currently installed state
            try:
                current_version = Version(version(pkg.pypi_name))
            except PackageNotFoundError:
                current_version = Version("0.0.0")
            pypi_version = get_pypi_lib_version(pkg)
            if pypi_version.base_version == "0.0.0":
                self.status_bar.pushMessage(f"Couldn't find PyPI package {pkg.pypi_name} online.")
            installed_state = check_local_lib_version(pkg, pypi_version)
            if installed_state == PyPiState.NOT_INSTALLED:
                icon = ":images/themes/default/pluginNew.svg"
                tooltip = f"Install {pkg.pypi_name}"
            elif installed_state == PyPiState.UPGRADEABLE:
                icon = ":images/themes/default/pluginUpgrade.svg"
                tooltip = f"Upgrade {pkg.pypi_name} to {pypi_version.public}"
            else:
                icon = ":images/themes/default/algorithms/mAlgorithmCheckGeometry.svg"
                tooltip = f"{pkg.pypi_name} is at the latest version"

            # add a URL linked label
            url_label = QLabel(f'<a href="{pkg.url}">{pkg.pypi_name}</a>')
            url_label.setTextFormat(Qt.RichText)
            url_label.setTextInteractionFlags(Qt.TextBrowserInteraction)
            url_label.setOpenExternalLinks(True)
            self.ui_deps_table.setCellWidget(row_id, 0, url_label)
            version_item = QTableWidgetItem(current_version.public)
            version_item.setToolTip(current_version.public)
            self.ui_deps_table.setItem(row_id, 1, version_item)
            available_item = QTableWidgetItem(pypi_version.public)
            available_item.setToolTip(pypi_version.public)
            self.ui_deps_table.setItem(row_id, 2, available_item)

            # add a tool button for the download
            btn = QToolButton()
            btn.rect = QRect(10, 10, 10, 10)
            btn.setIcon(get_icon(icon))
            btn.setEnabled(installed_state != PyPiState.UP_TO_DATE)
            btn.setToolTip(tooltip)
            f = partial(self._on_pypi_install, f"{pkg.pypi_name}=={pypi_version.public}")
            btn.clicked.connect(f)
            self.ui_deps_table.setCellWidget(row_id, 3, btn)

        self.ui_deps_table.resizeColumnToContents(3)

    def _on_pypi_install(self, pypi_pkg: str):
        """Install the package from PyPI"""
        try:
            install_pypi([pypi_pkg])
        except ValhallaCmdError as e:
            self.status_bar.pushMessage(f"Couldn't install the dependencies:\n{e}", Qgis.Critical, 0)
            return

        self.status_bar.pushMessage(f"Successfully installed/upgraded package: {pypi_pkg}")
        # update the table with the new info
        self.setupDepsTable()

    def on_settings_change(self, new_text, widget: Optional[QWidget] = ""):
        attr = widget.objectName() if widget else self.sender().objectName()
        ValhallaSettings().set(Dialogs.SETTINGS, attr, str(new_text))
