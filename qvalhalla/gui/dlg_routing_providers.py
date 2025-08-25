# -*- coding: utf-8 -*-

from dataclasses import dataclass

from qgis.gui import QgsCollapsibleGroupBox
from qgis.PyQt.QtWidgets import (
    QDialog,
    QGridLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QVBoxLayout,
)

from ..core.settings import ProviderSetting, ValhallaSettings
from ..global_definitions import RouterType
from ..gui.compiled.dlg_routing_providers_ui import Ui_RoutingProviders


@dataclass
class ProvUiProps:
    URL_TEXT: str
    KEY_TEXT: str
    PARAM_TEXT: str

    def __init__(self, provider: ProviderSetting):
        self.URL_TEXT = f"{provider.name}_{provider.url}"
        self.KEY_TEXT = f"{provider.name}_{provider.auth_key}"
        self.PARAM_TEXT = f"{provider.name}_{provider.auth_param}"


class ProviderDialog(QDialog, Ui_RoutingProviders):
    """Builds provider config dialog."""

    def __init__(self, parent=None):
        """
        :param parent: Parent window for modality.
        :type parent: QDialog
        """
        QDialog.__init__(self, parent)
        self.provider_layout: QVBoxLayout
        self.setupUi(self)

        for provider in ValhallaSettings().get_providers(RouterType.VALHALLA):
            self._add_collapsible_box(provider)

        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.provider_add.clicked.connect(self._add_provider)
        self.provider_remove.clicked.connect(self._remove_provider)

        self._collapse_boxes()

    def accept(self):
        """When the OK Button is clicked, we update the internal settings."""
        collapsible_boxes = self.findChildren(QgsCollapsibleGroupBox)
        current_providers = ValhallaSettings().pop_providers(RouterType.VALHALLA)
        for idx, box in enumerate(collapsible_boxes):
            current_provider = current_providers[idx]
            ui_props = ProvUiProps(current_provider)
            current_provider.auth_key = box.findChild(QLineEdit, ui_props.KEY_TEXT).text()
            current_provider.url = box.findChild(QLineEdit, ui_props.URL_TEXT).text()
            ValhallaSettings().set_provider(RouterType.VALHALLA, current_provider)

        self.close()

    def _add_provider(self):
        """Adds an empty provider box to be filled out by the user."""
        # Show quick user input dialog
        name, ok = QInputDialog.getText(
            self, "New Valhalla provider", "Enter a recognizable name for the provider"
        )
        if ok:
            new_setting = ProviderSetting(name, "https://", "", "access_key")
            self._add_collapsible_box(new_setting)
            ValhallaSettings().set_provider(RouterType.VALHALLA, new_setting)

        self._collapse_boxes()

    def _remove_provider(self):
        """Remove list of providers from list."""

        providers = [prov.name for prov in ValhallaSettings().get_providers(RouterType.VALHALLA)]

        prov_name, ok = QInputDialog.getItem(
            self,
            "Remove Valhalla provider",
            "Choose provider to remove",
            providers,
            0,
            False,
        )
        if ok:
            box_remove = self.findChild(QgsCollapsibleGroupBox, prov_name)
            print(box_remove.objectName())
            self.provider_layout.removeWidget(box_remove)

            ValhallaSettings().remove_provider(RouterType.VALHALLA, prov_name)
            box_remove.deleteLater()

    def _collapse_boxes(self):
        """Collapse all QgsCollapsibleGroupBoxes."""
        collapsible_boxes = self.findChildren(QgsCollapsibleGroupBox)
        for box in collapsible_boxes:
            box.setCollapsed(True)

    def _add_collapsible_box(
        self,
        provider: ProviderSetting,
    ):
        """
        Adds a provider box to the vertical layout and the settings.

        :param provider: provider
        """

        box = QgsCollapsibleGroupBox()
        box.setObjectName(provider.name)
        box.setTitle(provider.name)

        grid_layout = QGridLayout(box)
        ui_props = ProvUiProps(provider)

        base_url_label = QLabel(box)
        base_url_label.setObjectName("base_url_label")
        base_url_label.setText("Base URL")
        grid_layout.addWidget(base_url_label, 0, 0, 1, 5)

        base_url_text = QLineEdit(box)
        base_url_text.setObjectName(ui_props.URL_TEXT)
        base_url_text.setText(provider.url)
        grid_layout.addWidget(base_url_text, 1, 0, 1, 5)

        key_label = QLabel(box)
        key_label.setText("API Key")
        grid_layout.addWidget(key_label, 2, 0, 1, 5)

        key_text = QLineEdit(box)
        key_text.setObjectName(ui_props.KEY_TEXT)
        key_text.setText(provider.auth_key)
        grid_layout.addWidget(key_text, 3, 0, 1, 3)

        key_label = QLabel(box)
        key_label.setText("Param")
        grid_layout.addWidget(key_label, 3, 3, 1, 1)

        param_text = QLineEdit(box)
        param_text.setObjectName(ui_props.PARAM_TEXT)
        param_text.setText(provider.auth_param)
        grid_layout.addWidget(param_text, 3, 4, 1, 1)

        box.setSaveCollapsedState(False)
        self.provider_layout.addWidget(box)
