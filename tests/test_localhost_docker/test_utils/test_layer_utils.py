from qgis.core import (
    QgsFeature,
    QgsLineString,
    QgsMultiPoint,
    QgsMultiPolygon,
    QgsPoint,
    QgsPolygon,
    QgsVectorLayer,
)

from ... import LocalhostDockerTestCase
from ...constants import WAYPOINTS_4326
from ...utilities import get_qgis_app

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

from qvalhalla.utils.layer_utils import get_wgs_coords_from_layer


class TestLayerUtils(LocalhostDockerTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        # create one layer for each case the function handles:
        # [single point, single polygon, multi point, multi polygon]
        cls.single_point_layer = QgsVectorLayer("Point?crs=EPSG:4326", "single_point", "memory")
        for point in WAYPOINTS_4326:
            feat = QgsFeature()
            feat.setGeometry(QgsPoint(*point))
            cls.single_point_layer.dataProvider().addFeature(feat)

        cls.single_polygon_layer = QgsVectorLayer("Polygon?crs=EPSG:4326", "single_poly", "memory")
        for polygon in [WAYPOINTS_4326] * 2:  # create multiple polygons from same coordinates
            feat = QgsFeature()
            feat.setGeometry(QgsPolygon(QgsLineString([QgsPoint(*coord) for coord in polygon])))
            cls.single_polygon_layer.dataProvider().addFeature(feat)

        cls.multi_point_layer = QgsVectorLayer("MultiPoint?crs=EPSG:4326", "multi_point", "memory")
        feat = QgsFeature()
        multipoint = QgsMultiPoint()
        points = [QgsPoint(*coord) for coord in WAYPOINTS_4326]
        _ = [multipoint.addGeometry(point) for point in points]
        feat.setGeometry(multipoint)
        cls.multi_point_layer.dataProvider().addFeature(feat)

        cls.multi_polygon_layer = QgsVectorLayer("MultiPolygon?crs=EPSG:4326", "multi_poly", "memory")
        feat = QgsFeature()
        polys = [
            QgsPolygon(QgsLineString([QgsPoint(*coord) for coord in polygon]))
            for polygon in [WAYPOINTS_4326] * 2
        ]  # create multiple polygons from same coordinates
        multipoly = QgsMultiPolygon()
        _ = [multipoly.addGeometry(poly) for poly in polys]

        feat.setGeometry(multipoly)
        cls.multi_polygon_layer.dataProvider().addFeature(feat)

    def test_get_avoid_locations(self) -> None:
        for layer in (
            self.single_point_layer,
            self.single_polygon_layer,
            self.multi_point_layer,
            self.multi_polygon_layer,
        ):
            is_poly = layer.name().split("_")[1] == "poly"

            avoid_coords = get_wgs_coords_from_layer(layer)
            if is_poly:
                self.assertEqual(
                    avoid_coords,
                    [[*WAYPOINTS_4326, WAYPOINTS_4326[0]]]
                    * 2,  # First coordinate is repeated for Polygons
                    msg=f"get_avoid_locations failed with layer {layer.name()}",
                )
            else:  # points
                self.assertEqual(
                    avoid_coords,
                    WAYPOINTS_4326,
                    msg=f"get_avoid_locations failed with layer {layer.name()}",
                )
