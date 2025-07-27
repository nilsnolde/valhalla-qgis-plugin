from qgis.core import QgsVectorLayer

from ... import TEST_DIR
from ..processing_base import ProcessingBase


class SpOptProcessingBase(ProcessingBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.fac_layer = QgsVectorLayer(
            str(TEST_DIR / "data" / "facilities.geojson"), "facilities", "ogr"
        )

        cls.fac_layer_utm = QgsVectorLayer(
            str(TEST_DIR / "data" / "facilities_utm.geojson"), "facilities_utm", "ogr"
        )

        cls.dem_layer = QgsVectorLayer(
            str(TEST_DIR / "data" / "demand_points.geojson"), "demand_points", "ogr"
        )

        cls.dem_layer_utm = QgsVectorLayer(
            str(TEST_DIR / "data" / "demand_points_utm.geojson"),
            "demand_points_utm",
            "ogr",
        )

        cls.od_matrix = QgsVectorLayer(str(TEST_DIR / "data" / "matrix.geojson"), "matrix", "ogr")
