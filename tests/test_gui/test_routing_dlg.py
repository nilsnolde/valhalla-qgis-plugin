import unittest

from qgis.core import QgsVectorLayer
from tests.constants import WAYPOINTS_4326
from tests.utilities import get_qgis_app

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

from qvalhalla.global_definitions import DEFAULT_LAYER_FIELDS, RouterEndpoint
from qvalhalla.gui.dock_routing import RoutingDockWidget


class TestResultsFactory(unittest.TestCase):
    """Tests basic functionality of ResultsFactory class."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.dlg = RoutingDockWidget(IFACE)

        # set localhost instead of FOSSGIS
        cls.dlg.router_widget.ui_cmb_prov.setCurrentIndex(1)

        cls.iso_layer: QgsVectorLayer = cls.dlg._get_output_layer(
            RouterEndpoint.ISOCHRONES,
            locations=WAYPOINTS_4326,
            params={"intervals": [20], "polygons": True},
        )
        cls.route_layer: QgsVectorLayer = cls.dlg._get_output_layer(
            RouterEndpoint.DIRECTIONS,
            locations=WAYPOINTS_4326[:2],
            params={},
        )
        cls.matrix_layer: QgsVectorLayer = cls.dlg._get_output_layer(
            RouterEndpoint.MATRIX,
            locations=WAYPOINTS_4326,
            params={},
        )

    def test_layer_name(self):
        self.assertEqual(
            self.iso_layer.name(),
            "Valhalla Isochrones Pedestrian",
        )

        self.assertEqual(
            self.matrix_layer.name(),
            "Valhalla Matrix Pedestrian",
        )

    def test_layer_fields(self):
        iso_fields = [f for f in self.iso_layer.fields()]
        self.assertEqual(iso_fields, list(DEFAULT_LAYER_FIELDS[RouterEndpoint.ISOCHRONES]))

        matrix_fields = [f for f in self.matrix_layer.fields()]
        self.assertEqual(matrix_fields, list(DEFAULT_LAYER_FIELDS[RouterEndpoint.MATRIX]))

    def test_provider_change(self):
        """
        Tests whether UI elements are successfully
        disabled/enabled for specific provider/endpoint combinations.
        """

        # # OSRM – Isochrones
        # self.dlg.router_widget.ui_cmb_prov.setCurrentIndex(1)
        # self.dlg.menu_widget.setCurrentRow(1)

        # self.assertFalse(self.dlg.waypoints_widget.isEnabled())
        # self.assertFalse(self.dlg.ui_valhalla_isochrones_params.isEnabled())
        # self.assertFalse(self.dlg.ui_valhalla_expansion_params.isEnabled())
        # self.assertFalse(self.dlg.execute_btn.isEnabled())

        # # OSRM – Matrix
        # self.dlg.menu_widget.setCurrentRow(2)
        # self.assertTrue(self.dlg.execute_btn.isEnabled())

        # # OSRM – Expansion
        # self.dlg.menu_widget.setCurrentRow(3)

        # self.assertFalse(self.dlg.waypoints_widget.isEnabled())
        # self.assertFalse(self.dlg.ui_valhalla_isochrones_params.isEnabled())
        # self.assertFalse(self.dlg.ui_valhalla_expansion_params.isEnabled())
        # self.assertFalse(self.dlg.execute_btn.isEnabled())

        # Valhalla – Expansion
        self.dlg.router_widget.ui_cmb_prov.setCurrentIndex(0)
        self.assertTrue(self.dlg.waypoints_widget.isEnabled())
        self.assertTrue(self.dlg.ui_valhalla_expansion_params.isEnabled())
        self.assertTrue(self.dlg.execute_btn.isEnabled())

        # Valhalla – Isochrones
        self.dlg.menu_widget.setCurrentRow(1)
        self.assertTrue(self.dlg.waypoints_widget.isEnabled())
        self.assertTrue(self.dlg.ui_valhalla_isochrones_params.isEnabled())
        self.assertTrue(self.dlg.execute_btn.isEnabled())
