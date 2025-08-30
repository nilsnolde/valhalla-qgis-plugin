from typing import List

from qgis.gui import QgsCollapsibleGroupBox
from qgis.PyQt.QtWidgets import QLineEdit
from qvalhalla.core.settings import ProviderSetting, ValhallaSettings
from qvalhalla.global_definitions import RouterType
from qvalhalla.gui.dlg_routing_providers import ProviderDialog, ProvUiProps

from ... import LocalhostDockerTestCase


class TestProviderDialog(LocalhostDockerTestCase):
    def test_init(self):
        dlg = ProviderDialog()
        collapsible_boxes = dlg.findChildren(QgsCollapsibleGroupBox)
        self.assertEqual(len(collapsible_boxes), 2)

        providers: List[ProviderSetting] = ValhallaSettings().get_providers(RouterType.VALHALLA)
        for idx, box in enumerate(collapsible_boxes):
            prov = providers[idx]
            self.assertTrue(box.isCollapsed())
            self.assertEqual(box.title(), prov.name)

        dlg.close()

    def test_change_provider(self):
        dlg = ProviderDialog()

        localhost_box = dlg.findChildren(QgsCollapsibleGroupBox)[1]
        old_prov = ValhallaSettings().get_providers(RouterType.VALHALLA)[1]
        ui_props = ProvUiProps(old_prov)
        localhost_box.findChild(QLineEdit, ui_props.URL_TEXT).setText("https://test.com")

        # only after clicking "OK" should it update the settings with the new URL
        dlg.accept()

        new_prov = ValhallaSettings().get_providers(RouterType.VALHALLA)[1]
        self.assertEqual(new_prov.url, "https://test.com")

        # cleanup
        ValhallaSettings().remove_provider(RouterType.VALHALLA, new_prov.name)
        ValhallaSettings().set_provider(RouterType.VALHALLA, old_prov)
        self.assertEqual(ValhallaSettings().get_providers(RouterType.VALHALLA)[1].url, old_prov.url)
