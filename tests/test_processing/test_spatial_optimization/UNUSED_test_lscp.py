from qgis.core import QgsProcessingException, QgsWkbTypes

from valhalla.processing.spatial_optimization.lscp import LSCPAlgorithm

from ...utilities import get_qgis_app
from .spopt_base import SpOptProcessingBase

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()


class TestLSCP(SpOptProcessingBase):
    def test_lscp_minimal_params(self):
        """Tests the LSCP algorithm with only the matrix input and the service radius specified."""
        params = {"INPUT_MATRIX_LAYER": self.od_matrix, "INPUT_SERVICE_RADIUS": 600}
        alg = LSCPAlgorithm()
        (
            fac_out_feats,
            fac_geom_type,
            dem_out_feats,
            dem_geom_type,
        ) = self.run_spopt_algorithm(alg, params)
        self.assertEqual(len(fac_out_feats), 2)
        self.assertEqual(len(dem_out_feats), 18)

        self.assertEqual(fac_geom_type, QgsWkbTypes.NoGeometry)
        self.assertEqual(dem_geom_type, QgsWkbTypes.NoGeometry)

    def test_lscp_with_original_layers(self):
        """Tests the LSCP algorithm with facility and demand point inputs specified."""
        params = {
            "INPUT_MATRIX_LAYER": self.od_matrix,
            "INPUT_SERVICE_RADIUS": 600,
            "INPUT_FAC_LAYER": self.fac_layer,
            "INPUT_FAC_ID": "id",
            "INPUT_DEM_POINT_LAYER": self.dem_layer,
            "INPUT_DEM_ID": "id",
        }
        alg = LSCPAlgorithm()
        (
            fac_out_feats,
            fac_geom_type,
            dem_out_feats,
            dem_geom_type,
        ) = self.run_spopt_algorithm(alg, params)
        self.assertEqual(len(fac_out_feats), 2)
        self.assertEqual(len(dem_out_feats), 18)
        self.assertEqual(fac_geom_type, QgsWkbTypes.Point)
        self.assertEqual(dem_geom_type, QgsWkbTypes.Point)

    def test_lscp_with_predefined_facilities(self):
        """Tests the LSCP algorithm with predefined facilities."""
        params = {
            "INPUT_MATRIX_LAYER": self.od_matrix,
            "INPUT_SERVICE_RADIUS": 600,
            "INPUT_PREDEFINED_FAC_FIELD": "predefined",
            "INPUT_FAC_LAYER": self.fac_layer,
            "INPUT_FAC_ID": "id",
            "INPUT_DEM_POINT_LAYER": self.dem_layer,
            "INPUT_DEM_ID": "id",
        }
        alg = LSCPAlgorithm()
        (
            fac_out_feats,
            fac_geom_type,
            dem_out_feats,
            dem_geom_type,
        ) = self.run_spopt_algorithm(alg, params)
        self.assertEqual(len(fac_out_feats), 3)
        self.assertEqual(len(dem_out_feats), 26)
        self.assertEqual(fac_geom_type, QgsWkbTypes.Point)
        self.assertEqual(dem_geom_type, QgsWkbTypes.Point)

    def test_lscp_partial_joins(self):
        """Tests the LSCP algorithm with only the facilities or demand points layers specified, respectively."""
        params = {
            "INPUT_MATRIX_LAYER": self.od_matrix,
            "INPUT_SERVICE_RADIUS": 600,
            "INPUT_FAC_LAYER": self.fac_layer,
            "INPUT_FAC_ID": "id",
        }

        alg = LSCPAlgorithm()
        (
            fac_out_feats,
            fac_geom_type,
            dem_out_feats,
            dem_geom_type,
        ) = self.run_spopt_algorithm(alg, params)
        self.assertEqual(len(fac_out_feats), 2)
        self.assertEqual(len(dem_out_feats), 18)
        self.assertEqual(fac_geom_type, QgsWkbTypes.Point)
        self.assertEqual(dem_geom_type, QgsWkbTypes.NoGeometry)

        params = {
            "INPUT_MATRIX_LAYER": self.od_matrix,
            "INPUT_SERVICE_RADIUS": 600,
            "INPUT_DEM_POINT_LAYER": self.dem_layer,
            "INPUT_DEM_ID": "id",
        }

        alg = LSCPAlgorithm()
        (
            fac_out_feats,
            fac_geom_type,
            dem_out_feats,
            dem_geom_type,
        ) = self.run_spopt_algorithm(alg, params)
        self.assertEqual(len(fac_out_feats), 2)
        self.assertEqual(len(dem_out_feats), 18)
        self.assertEqual(fac_geom_type, QgsWkbTypes.NoGeometry)
        self.assertEqual(dem_geom_type, QgsWkbTypes.Point)

    def test_lscp_small_service_radius(self):
        """Tests the LSCP algorithm with a service radius too small to find a solution."""
        params = {
            "INPUT_MATRIX_LAYER": self.od_matrix,
            "INPUT_SERVICE_RADIUS": 100,
            "INPUT_DEM_POINT_LAYER": self.dem_layer,
            "INPUT_DEM_ID": "id",
        }

        alg = LSCPAlgorithm()
        with self.assertRaises(QgsProcessingException):
            self.run_spopt_algorithm(alg, params)
