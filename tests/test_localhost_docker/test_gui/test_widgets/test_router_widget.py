from qgis.core import QgsCoordinateReferenceSystem, QgsRectangle
from qgis.gui import QgsMapCanvas
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtTest import QTest

from .... import LocalhostDockerTestCase
from ....utilities import get_qgis_app

CANVAS: QgsMapCanvas
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

from qvalhalla.gui.dock_routing import RoutingDockWidget
from qvalhalla.gui.widgets.costing_settings.widget_settings_valhalla_mbike import (
    ValhallaSettingsMbikeWidget,
)
from qvalhalla.gui.widgets.costing_settings.widget_settings_valhalla_pedestrian import (
    ValhallaSettingsPedestrianWidget,
)


class TestRouterWidget(LocalhostDockerTestCase):
    def setUp(self) -> None:
        super(TestRouterWidget, self).setUp()
        # Berlin
        CANVAS.setExtent(QgsRectangle(1478686, 6885333, 1500732, 6903232))
        CANVAS.setDestinationCrs(QgsCoordinateReferenceSystem.fromEpsgId(3857))

        self.dlg = RoutingDockWidget(IFACE)

    def test_provider_change(self):
        """
        Tests whether UI elements are successfully
        disabled/enabled for specific provider/endpoint combinations.
        """

        # Valhalla – Routing
        self.dlg.menu_widget.setCurrentRow(0)
        self.assertTrue(self.dlg.waypoints_widget.isEnabled())
        self.assertTrue(self.dlg.ui_valhalla_directions_params.isEnabled())
        self.assertTrue(self.dlg.execute_btn.isEnabled())

        # Valhalla – Isochrones
        self.dlg.menu_widget.setCurrentRow(1)
        self.assertTrue(self.dlg.waypoints_widget.isEnabled())
        self.assertTrue(self.dlg.ui_valhalla_isochrones_params.isEnabled())
        self.assertTrue(self.dlg.execute_btn.isEnabled())

        # Valhalla – Matrix
        self.dlg.menu_widget.setCurrentRow(2)
        self.assertTrue(self.dlg.waypoints_widget.isEnabled())
        self.assertTrue(self.dlg.ui_valhalla_matrix_params.isEnabled())
        self.assertTrue(self.dlg.execute_btn.isEnabled())

        # Valhalla – Expansion
        self.dlg.menu_widget.setCurrentRow(3)
        self.assertTrue(self.dlg.waypoints_widget.isEnabled())
        self.assertTrue(self.dlg.ui_valhalla_expansion_params.isEnabled())
        self.assertTrue(self.dlg.execute_btn.isEnabled())

    def test_profile_change(self):
        # starts off with pedestrian
        self.assertIsInstance(
            self.dlg.routing_params_widget.ui_settings_stacked.currentWidget(),
            ValhallaSettingsPedestrianWidget,
        )

        # Valhalla - motorbike
        QTest.mouseClick(self.dlg.router_widget.ui_btn_mbike, Qt.LeftButton)
        self.assertIsInstance(
            self.dlg.routing_params_widget.ui_settings_stacked.currentWidget(),
            ValhallaSettingsMbikeWidget,
        )
