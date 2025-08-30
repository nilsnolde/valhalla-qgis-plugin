from qvalhalla.gui.dlg_about import AboutDialog
from qvalhalla.gui.dock_routing import RoutingDockWidget

from ...utilities import get_qgis_app

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

from ... import LocalhostDockerTestCase


class TestAboutDlg(LocalhostDockerTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.parent_dlg = RoutingDockWidget(IFACE)
        # set localhost instead of FOSSGIS
        cls.parent_dlg.router_widget.ui_cmb_prov.setCurrentIndex(1)

    def test_success(self):
        dlg = AboutDialog(self.parent_dlg)
        # make sure it starts with a x.y.z version string
        self.assertRegex(dlg.ui_valhalla_version_text.text(), r"^\d+(?:\.\d+){2}\b")
        # make sure the date time is valid too
        self.assertRegex(
            dlg.ui_data_age_text.text(),
            r"^\d{4}-\d{2}-\d{2}T(?:[01]\d|2[0-3]):[0-5]\d:[0-5]\d(?:\.\d+)? UTC$",
        )
