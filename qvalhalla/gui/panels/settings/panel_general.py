from functools import partial
from importlib.metadata import PackageNotFoundError, version

from packaging.version import parse as Version
from qgis.core import Qgis
from qgis.gui import QgisInterface
from qgis.PyQt.QtCore import QRect, Qt
from qgis.PyQt.QtWidgets import QLabel, QTableWidgetItem, QToolButton

from ....exceptions import ValhallaCmdError
from ....global_definitions import PYPI_PKGS, Dialogs, PyPiState
from ....gui.panels.settings.panel_base import PanelBase
from ....utils.resource_utils import (
    check_local_lib_version,
    get_icon,
    get_pypi_lib_version,
    install_pypi,
)
from ...ui_definitions import PluginSettingsDlgElems

iface: QgisInterface

PACKAGE_NA = "-"


class PanelGeneral(PanelBase):
    SETTINGS_TYPE = Dialogs.SETTINGS
    RECOVER = [
        # PluginSettingsDlgElems.ACCOUNT_AUTH,
        # PluginSettingsDlgElems.SHOP_HTTP_URL,
        PluginSettingsDlgElems.DEBUG,
    ]

    def setup_panel(self):
        """Set up deps table"""
        self.dlg.ui_deps_table.clear()
        self.dlg.ui_deps_table.setRowCount(len(PYPI_PKGS))
        self.dlg.ui_deps_table.setHorizontalHeaderLabels(["Package", "Installed", "Available", "Action"])
        for row_id, pkg in enumerate(PYPI_PKGS):
            # get the versions and the currently installed state
            try:
                current_version = Version(version(pkg.pypi_name))
            except PackageNotFoundError:
                current_version = Version("0.0.0")
            pypi_version = get_pypi_lib_version(pkg)
            if pypi_version.base_version == "0.0.0":
                self.dlg.status_bar.pushMessage(f"Couldn't find PyPI package {pkg.pypi_name} online.")
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
            self.dlg.ui_deps_table.setCellWidget(row_id, 0, url_label)
            version_item = QTableWidgetItem(current_version.public)
            version_item.setToolTip(current_version.public)
            self.dlg.ui_deps_table.setItem(row_id, 1, version_item)
            available_item = QTableWidgetItem(pypi_version.public)
            available_item.setToolTip(pypi_version.public)
            self.dlg.ui_deps_table.setItem(row_id, 2, available_item)

            # add a tool button for the download
            btn = QToolButton()
            btn.rect = QRect(10, 10, 10, 10)
            btn.setIcon(get_icon(icon))
            btn.setEnabled(installed_state != PyPiState.UP_TO_DATE)
            btn.setToolTip(tooltip)
            f = partial(self._on_pypi_install, f"{pkg.pypi_name}=={pypi_version.public}")
            btn.clicked.connect(f)
            self.dlg.ui_deps_table.setCellWidget(row_id, 3, btn)

        self.dlg.ui_deps_table.resizeColumnToContents(3)
        # self.dlg.ui_deps_table.horizontalHeader().setStretchLastSection(True)

    def _on_pypi_install(self, pypi_pkg: str):
        """Install the package from PyPI"""
        try:
            install_pypi([pypi_pkg])
        except ValhallaCmdError as e:
            self.dlg.status_bar.pushMessage(f"Couldn't install the dependencies:\n{e}", Qgis.Critical, 0)
            return

        self.dlg.status_bar.pushMessage(f"Successfully installed/upgraded package: {pypi_pkg}")
        # update the table with the new info
        self.setup_panel()
