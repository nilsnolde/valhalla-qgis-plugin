from time import sleep
from unittest import skip

from qgis.core import QgsProject, QgsVectorLayer, QgsWkbTypes
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtTest import QTest

from tests.utilities import get_first_feature_geometry, get_qgis_app

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

# from network_analyst.gui.dlg_spopt import SpoptDialog
from tests import HTTPTestCase
from tests.constants import WAYPOINTS_4326


from valhalla.gui.dlg_routing import RoutingDialog

# from network_analyst import BASE_DIR
# from network_analyst.utils.resource_utils import get_settings_dir
# from network_analyst.global_definitions import RouterMethod, RouterType, FieldNames


class TestHttpRouting(HTTPTestCase):
    def setUp(self) -> None:
        super(TestHttpRouting, self).setUp()

        self.dlg = RoutingDialog(IFACE.mainWindow(), IFACE)
        self.dlg.open()
        # set localhost instead of FOSSGIS
        self.dlg.router_widget.ui_cmb_prov.setCurrentIndex(1)
        for ix, _ in enumerate(WAYPOINTS_4326[:-1]):
            self.dlg.waypoints_widget.ui_table.insertRow(ix)
            self.dlg.waypoints_widget._add_row_to_table(ix, *list(reversed(WAYPOINTS_4326[ix])))

    def tearDown(self) -> None:
        QgsProject.instance().removeAllMapLayers()

    def hit_execute(self):
        QTest.mouseClick(self.dlg.execute_btn, Qt.LeftButton)
        sleep(0.2)  # give some time for the response to be handled

    def test_valhalla_http_directions_via(self):
        # add the third waypoint to the table
        self.dlg.waypoints_widget.ui_table.insertRow(2)
        self.dlg.waypoints_widget._add_row_to_table(2, *list(reversed(WAYPOINTS_4326[2])))
        self.hit_execute()
        self.assertEqual(len(list(QgsProject.instance().mapLayers())), 1)
        layer: QgsVectorLayer = list(QgsProject.instance().mapLayers().values())[0]
        self.assertEqual(layer.featureCount(), 1)
        self.assertTrue(
            layer.geometryType() == QgsWkbTypes.LineGeometry,
            msg=f"Directions layer has unexpected Geometry Type {layer.geometryType()}",
        )

    def test_valhalla_http_isochrones(self):
        self.dlg.menu_widget.setCurrentRow(1)
        self.dlg.ui_isochrone_intervals.setText("20,40")
        self.hit_execute()
        layers = list(QgsProject.instance().mapLayers().values())
        layer: QgsVectorLayer = layers[0]
        self.assertEqual(len(layers), 1)
        self.assertTrue(
            layer.geometryType() == QgsWkbTypes.PolygonGeometry,
            msg=f"Isochrone layer has unexpected Geometry Type {layer.geometryType()}",
        )
        self.assertEqual(layer.featureCount(), 4)

    def test_valhalla_http_matrix(self):
        self.dlg.menu_widget.setCurrentRow(2)
        self.hit_execute()
        layers = list(QgsProject.instance().mapLayers().values())
        layer: QgsVectorLayer = layers[0]
        self.assertEqual(len(layers), 1)
        self.assertTrue(
            layer.geometryType() == QgsWkbTypes.NullGeometry,
            msg=f"Matrix layer has unexpected Geometry Type {layer.geometryType()}",
        )

    def test_valhalla_http_expansion(self):
        self.dlg.menu_widget.setCurrentRow(3)
        self.dlg.ui_expansion_intervals.setText("500")
        self.hit_execute()
        layers = list(QgsProject.instance().mapLayers().values())
        layer: QgsVectorLayer = layers[0]
        self.assertEqual(len(layers), 1)
        self.assertTrue(
            layer.geometryType() == QgsWkbTypes.LineGeometry,
            msg=f"Expansion layer has unexpected Geometry Type {layer.geometryType()}",
        )
        self.assertGreater(
            layer.featureCount(), 30
        )  # some arbitrary value, actual count should be higher

    def test_valhalla_car_costing_options(self):
        """Runs directions with and without costing options, compares result differences."""
        QTest.mouseClick(
            self.dlg.router_widget.ui_btn_bike,
            Qt.LeftButton,
        )
        self.hit_execute()
        layer_no_costing: QgsVectorLayer = list(QgsProject.instance().mapLayers().values())[0]
        layer_no_costing.setName("no_costing")  # rename the layer so we can distinguish them

        # now change a costing option that produces a different result and repeat
        self.dlg.routing_params_widget.settings_valhalla_bike.use_roads.setValue(0.0)
        self.hit_execute()

        self.assertEqual(len(QgsProject.instance().mapLayers()), 2)

        layer_with_costing: QgsVectorLayer = [
            f for f in list(QgsProject.instance().mapLayers().values()) if f.name() != "no_costing"
        ][0]
        layer_with_costing.setName("with_costing")

        # compare GeoJSON strings of the two geometries
        geom_no_costing = get_first_feature_geometry(layer_no_costing)
        geom_costing = get_first_feature_geometry(layer_with_costing)
        self.assertNotAlmostEqual(geom_no_costing.length(), geom_costing.length(), places=2)

        # tests the reset button: new directions geometry should be almost equal to the first one
        QTest.mouseClick(
            self.dlg.routing_params_widget.ui_reset_settings,
            Qt.LeftButton,
        )
        self.hit_execute()
        layer_with_reset_costing = [
            f
            for f in list(QgsProject.instance().mapLayers().values())
            if f.name() not in ("no_costing", "with_costing")
        ][0]

        geom_reset_costing = get_first_feature_geometry(layer_with_reset_costing)

        # testing for equality would not be very robust here
        self.assertLess(
            abs(geom_no_costing.length() - geom_reset_costing.length()),
            0.000001,
        )

    @skip
    def test_osrm_http_directions_via(self):
        # add the 3rd coordinate
        self.dlg.waypoints_widget.ui_table.insertRow(2)
        self.dlg.waypoints_widget._add_row_to_table(2, *list(reversed(WAYPOINTS_4326[2])))
        # set provider to OSRM http
        self.dlg.router_widget.ui_cmb_prov.setCurrentIndex(1)

        self.hit_execute()
        self.assertEqual(len(list(QgsProject.instance().mapLayers())), 1)
        layer: QgsVectorLayer = list(QgsProject.instance().mapLayers().values())[0]
        self.assertEqual(layer.featureCount(), 1)
        self.assertTrue(
            layer.geometryType() == QgsWkbTypes.LineGeometry,
            msg=f"Directions layer has unexpected Geometry Type {layer.geometryType()}",
        )

    @skip
    def test_osrm_http_matrix(self):
        # set provider to OSRM http
        self.dlg.router_widget.ui_cmb_prov.setCurrentIndex(1)
        self.dlg.menu_widget.setCurrentRow(2)

        self.hit_execute()
        layers = list(QgsProject.instance().mapLayers().values())
        layer: QgsVectorLayer = layers[0]
        self.assertEqual(len(layers), 1)
        self.assertTrue(
            layer.geometryType() == QgsWkbTypes.NullGeometry,
            msg=f"Matrix layer has unexpected Geometry Type {layer.geometryType()}",
        )


# class TestBindings(unittest.TestCase):
#     def setUp(self) -> None:
#         # copy the graphs if necessary
#         for router, fname in GRAPHS:
#             out_fp = get_settings_dir().joinpath(router, fname)
#             if not out_fp.exists():
#                 shutil.copy2(BASE_DIR.parent.joinpath("tests", "data", fname), out_fp)

#         self.dlg = RoutingDialog(IFACE.mainWindow(), IFACE)
#         self.dlg.open()

#         self.dlg.router_widget.ui_cmb_prov.setCurrentIndex(2)
#         self.assertEqual(self.dlg.router_widget.provider, RouterType.VALHALLA)
#         self.assertEqual(self.dlg.router_widget.method, RouterMethod.LOCAL)

#         # add first two points
#         for ix, wp in enumerate(WAYPOINTS_4326[:-1]):
#             self.dlg.waypoints_widget.ui_table.insertRow(ix)
#             self.dlg.waypoints_widget._add_row_to_table(ix, *list(reversed(wp)))

#     def tearDown(self) -> None:
#         QgsProject.instance().removeAllMapLayers()

#     def hit_execute(self):
#         QTest.mouseClick(self.dlg.execute_btn, Qt.LeftButton)
#         sleep(0.1)  # give some time for the response to be handled

#     def test_valhalla_bindings_directions_via(self):
#         # add the third waypoint to the table
#         self.dlg.waypoints_widget._add_row_to_table(2, *list(reversed(WAYPOINTS_4326[2])))
#         self.hit_execute()

#         self.assertEqual(len(list(QgsProject.instance().mapLayers())), 1)
#         layer: QgsVectorLayer = list(QgsProject.instance().mapLayers().values())[0]
#         self.assertEqual(layer.featureCount(), 1)
#         self.assertTrue(
#             layer.geometryType() == QgsWkbTypes.LineGeometry,
#             msg=f"Directions layer has unexpected Geometry Type {layer.geometryType()}",
#         )

#     def test_valhalla_bindings_isochrones(self):
#         self.dlg.menu_widget.setCurrentRow(1)
#         self.dlg.ui_isochrone_intervals.setText("20,40")

#         self.hit_execute()

#         layers = list(QgsProject.instance().mapLayers().values())
#         layer: QgsVectorLayer = layers[0]
#         self.assertEqual(len(layers), 1)
#         self.assertTrue(
#             layer.geometryType() == QgsWkbTypes.PolygonGeometry,
#             msg=f"Isochrone layer has unexpected Geometry Type {layer.geometryType()}",
#         )
#         self.assertEqual(layer.featureCount(), 4)

#     def test_valhalla_bindings_matrix(self):
#         self.dlg.menu_widget.setCurrentRow(2)
#         self.hit_execute()

#         layers = list(QgsProject.instance().mapLayers().values())
#         layer: QgsVectorLayer = layers[0]
#         self.assertEqual(len(layers), 1)
#         self.assertTrue(
#             layer.geometryType() == QgsWkbTypes.NullGeometry,
#             msg=f"Matrix layer has unexpected Geometry Type {layer.geometryType()}",
#         )

#     def test_valhalla_bindings_expansion(self):
#         self.dlg.menu_widget.setCurrentRow(3)
#         self.dlg.ui_expansion_intervals.setText("500")
#         self.hit_execute()

#         layers = list(QgsProject.instance().mapLayers().values())
#         layer: QgsVectorLayer = layers[0]
#         self.assertEqual(len(layers), 1)
#         self.assertTrue(
#             layer.geometryType() == QgsWkbTypes.LineGeometry,
#             msg=f"Expansion layer has unexpected Geometry Type {layer.geometryType()}",
#         )
#         self.assertGreater(
#             layer.featureCount(), 60
#         )  # some arbitrary value, actual count should be higher


# class TestSpOpt(unittest.TestCase):
#     def setUp(self) -> None:
#         # copy the graphs if necessary
#         for router, fname in GRAPHS:
#             out_fp = get_settings_dir().joinpath(router, fname)
#             if not out_fp.exists():
#                 shutil.copy2(BASE_DIR.parent.joinpath("tests", "data", fname), out_fp)

#         self.fac_layer = QgsVectorLayer(
#             str(TEST_DIR / "data" / "facilities.geojson"), "facilities", "ogr"
#         )
#         self.dem_layer = QgsVectorLayer(
#             str(TEST_DIR / "data" / "demand_points.geojson"), "demand_points", "ogr"
#         )
#         QgsProject.instance().addMapLayer(self.fac_layer)
#         QgsProject.instance().addMapLayer(self.dem_layer)
#         self.dlg = SpoptDialog(IFACE.mainWindow(), IFACE)
#         self.dlg.open()

#     def tearDown(self) -> None:
#         QgsProject.instance().removeAllMapLayers()

#     def hit_execute(self):
#         QTest.mouseClick(self.dlg.execute_btn, Qt.LeftButton)
#         sleep(0.1)  # give some time for the response to be handled

#     def test_lscp_ped_http(self):
#         self.dlg.menu_widget.setCurrentRow(0)
#         self.dlg.ui_fac_layer.setLayer(self.fac_layer)
#         self.dlg.ui_fac_id_field.setLayer(self.fac_layer)
#         self.dlg.ui_fac_id_field.setField("id")

#         self.dlg.ui_dem_point_layer.setLayer(self.dem_layer)
#         self.dlg.ui_dem_point_id_field.setLayer(self.dem_layer)

#         self.dlg.ui_lscp_service_radius.setValue(1000)
#         self.dlg.ui_return_matrix.setChecked(True)

#         self.hit_execute()
#         layers: List[QgsVectorLayer] = list(QgsProject.instance().mapLayers().values())
#         self.assertEqual(len(layers), 5)
#         dem_layer = [layer for layer in layers if layer.name() == "Demand points"][0]
#         fac_layer = [layer for layer in layers if layer.name() == "Selected facilities"][0]
#         matrix_layer = [layer for layer in layers if layer.name() == "valhalla_matrix_pedestrian"][0]

#         self.assertEqual(fac_layer.featureCount(), 1)
#         self.assertEqual([f[FieldNames.ID] for f in fac_layer.getFeatures()][0], 3)
#         self.assertEqual(dem_layer.featureCount(), 15)
#         self.assertEqual([f[FieldNames.FACILITY_ID] for f in dem_layer.getFeatures()], [3] * 15)
#         self.assertEqual(matrix_layer.featureCount(), 45)

#     def test_lscp_ped_local(self):
#         # TODO: this might break if a user has graph packages installed that alphabetically appear before andorra
#         self.dlg.router_widget.ui_cmb_prov.setCurrentIndex(2)
#         self.dlg.menu_widget.setCurrentRow(0)
#         self.dlg.ui_fac_layer.setLayer(self.fac_layer)
#         self.dlg.ui_fac_id_field.setLayer(self.fac_layer)
#         self.dlg.ui_fac_id_field.setField("id")

#         self.dlg.ui_dem_point_layer.setLayer(self.dem_layer)
#         self.dlg.ui_dem_point_id_field.setLayer(self.dem_layer)

#         self.dlg.ui_lscp_service_radius.setValue(1000)
#         self.dlg.ui_return_matrix.setChecked(True)

#         self.hit_execute()
#         layers: List[QgsVectorLayer] = list(QgsProject.instance().mapLayers().values())
#         self.assertEqual(len(layers), 5)
#         dem_layer = [layer for layer in layers if layer.name() == "Demand points"][0]
#         fac_layer = [layer for layer in layers if layer.name() == "Selected facilities"][0]
#         matrix_layer = [layer for layer in layers if layer.name() == "valhalla_matrix_pedestrian"][0]

#         self.assertEqual(fac_layer.featureCount(), 1)
#         self.assertEqual([f[FieldNames.ID] for f in fac_layer.getFeatures()][0], 3)
#         self.assertEqual(dem_layer.featureCount(), 15)
#         self.assertEqual([f[FieldNames.FACILITY_ID] for f in dem_layer.getFeatures()], [3] * 15)
#         self.assertEqual(matrix_layer.featureCount(), 45)

#     def test_mclp_bike_http(self):

#         self.dlg.menu_widget.setCurrentRow(1)
#         QTest.mouseClick(
#             self.dlg.router_widget.ui_btn_bike,
#             Qt.LeftButton,
#         )
#         self.dlg.ui_fac_layer.setLayer(self.fac_layer)
#         self.dlg.ui_fac_id_field.setLayer(self.fac_layer)
#         self.dlg.ui_fac_id_field.setField("id")

#         self.dlg.ui_dem_point_layer.setLayer(self.dem_layer)
#         self.dlg.ui_dem_point_id_field.setLayer(self.dem_layer)

#         self.dlg.ui_mclp_service_radius.setValue(1000)
#         self.dlg.ui_mclp_n_fac.setValue(1)
#         self.dlg.ui_return_matrix.setChecked(True)

#         self.hit_execute()

#         layers: List[QgsVectorLayer] = list(QgsProject.instance().mapLayers().values())
#         self.assertEqual(len(layers), 5)
#         dem_layer = [layer for layer in layers if layer.name() == "Demand points"][0]
#         fac_layer = [layer for layer in layers if layer.name() == "Selected facilities"][0]
#         matrix_layer = [layer for layer in layers if layer.name() == "valhalla_matrix_bicycle"][0]

#         self.assertEqual(fac_layer.featureCount(), 1)
#         self.assertEqual([f[FieldNames.ID] for f in fac_layer.getFeatures()][0], 2)
#         self.assertEqual(dem_layer.featureCount(), 15)
#         self.assertEqual([f[FieldNames.FACILITY_ID] for f in dem_layer.getFeatures()], [2] * 15)
#         self.assertEqual(matrix_layer.featureCount(), 45)

#     def test_pcenter_car_http(self):
#         self.dlg.menu_widget.setCurrentRow(2)
#         QTest.mouseClick(
#             self.dlg.router_widget.ui_btn_car,
#             Qt.LeftButton,
#         )
#         self.dlg.ui_fac_layer.setLayer(self.fac_layer)
#         self.dlg.ui_fac_id_field.setLayer(self.fac_layer)
#         self.dlg.ui_fac_id_field.setField("id")

#         self.dlg.ui_dem_point_layer.setLayer(self.dem_layer)
#         self.dlg.ui_dem_point_id_field.setLayer(self.dem_layer)

#         self.dlg.ui_pcenter_n_fac.setValue(1)
#         self.dlg.ui_return_matrix.setChecked(True)

#         self.hit_execute()

#         layers: List[QgsVectorLayer] = list(QgsProject.instance().mapLayers().values())
#         self.assertEqual(len(layers), 5)
#         dem_layer = [layer for layer in layers if layer.name() == "Demand points"][0]
#         fac_layer = [layer for layer in layers if layer.name() == "Selected facilities"][0]
#         matrix_layer = [layer for layer in layers if layer.name() == "valhalla_matrix_auto"][0]

#         self.assertEqual(fac_layer.featureCount(), 1)
#         self.assertEqual([f[FieldNames.ID] for f in fac_layer.getFeatures()][0], 1)
#         self.assertEqual(dem_layer.featureCount(), 15)
#         self.assertEqual([f[FieldNames.FACILITY_ID] for f in dem_layer.getFeatures()], [1] * 15)
#         self.assertEqual(matrix_layer.featureCount(), 45)

#     def test_pmedian_car_http(self):
#         self.dlg.menu_widget.setCurrentRow(3)
#         QTest.mouseClick(
#             self.dlg.router_widget.ui_btn_car,
#             Qt.LeftButton,
#         )
#         self.dlg.ui_fac_layer.setLayer(self.fac_layer)
#         self.dlg.ui_fac_id_field.setLayer(self.fac_layer)
#         self.dlg.ui_fac_id_field.setField("id")

#         self.dlg.ui_dem_point_layer.setLayer(self.dem_layer)
#         self.dlg.ui_dem_point_id_field.setLayer(self.dem_layer)

#         self.dlg.ui_pcenter_n_fac.setValue(1)
#         self.dlg.ui_return_matrix.setChecked(True)

#         self.hit_execute()

#         layers: List[QgsVectorLayer] = list(QgsProject.instance().mapLayers().values())
#         self.assertEqual(len(layers), 5)
#         dem_layer = [layer for layer in layers if layer.name() == "Demand points"][0]
#         fac_layer = [layer for layer in layers if layer.name() == "Selected facilities"][0]
#         matrix_layer = [layer for layer in layers if layer.name() == "valhalla_matrix_auto"][0]

#         self.assertEqual(fac_layer.featureCount(), 1)
#         self.assertEqual([f[FieldNames.ID] for f in fac_layer.getFeatures()][0], 1)
#         self.assertEqual(dem_layer.featureCount(), 15)
#         self.assertEqual([f[FieldNames.FACILITY_ID] for f in dem_layer.getFeatures()], [1] * 15)
#         self.assertEqual(matrix_layer.featureCount(), 45)

#     def test_pmedian_weights_car_http(self):
#         self.dlg.menu_widget.setCurrentRow(3)
#         QTest.mouseClick(
#             self.dlg.router_widget.ui_btn_car,
#             Qt.LeftButton,
#         )
#         self.dlg.ui_fac_layer.setLayer(self.fac_layer)
#         self.dlg.ui_fac_id_field.setLayer(self.fac_layer)
#         self.dlg.ui_fac_id_field.setField("id")

#         self.dlg.ui_dem_point_layer.setLayer(self.dem_layer)
#         self.dlg.ui_dem_point_id_field.setLayer(self.dem_layer)
#         self.dlg.ui_pmedian_weights.setLayer(self.dem_layer)
#         self.dlg.ui_pmedian_weights.setField("weights")

#         self.dlg.ui_pcenter_n_fac.setValue(1)
#         self.dlg.ui_return_matrix.setChecked(True)

#         self.hit_execute()

#         layers: List[QgsVectorLayer] = list(QgsProject.instance().mapLayers().values())
#         self.assertEqual(len(layers), 5)
#         dem_layer = [layer for layer in layers if layer.name() == "Demand points"][0]
#         fac_layer = [layer for layer in layers if layer.name() == "Selected facilities"][0]
#         matrix_layer = [layer for layer in layers if layer.name() == "valhalla_matrix_auto"][0]

#         self.assertEqual(fac_layer.featureCount(), 1)
#         self.assertEqual([f[FieldNames.ID] for f in fac_layer.getFeatures()][0], 2)
#         self.assertEqual(dem_layer.featureCount(), 15)
#         self.assertEqual([f[FieldNames.FACILITY_ID] for f in dem_layer.getFeatures()], [2] * 15)
#         self.assertEqual(matrix_layer.featureCount(), 45)
