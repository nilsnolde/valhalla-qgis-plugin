from qgis.core import QgsProcessingException, QgsWkbTypes

from valhalla.processing.spatial_optimization.mclp import MCLPAlgorithm

from .UNUSED_spopt_base import SpOptProcessingBase


class TestMCLP(SpOptProcessingBase):
    def test_mclp_minimal_params(self):
        """Tests the MCLP algorithm with only the matrix input and the service radius specified."""
        params = {"INPUT_MATRIX_LAYER": self.od_matrix, "INPUT_SERVICE_RADIUS": 100}

        alg = MCLPAlgorithm()
        (
            fac_out_feats,
            fac_geom_type,
            dem_out_feats,
            dem_geom_type,
        ) = self.run_spopt_algorithm(alg, params)

        self.assertEqual(fac_geom_type, QgsWkbTypes.NoGeometry)
        self.assertEqual(dem_geom_type, QgsWkbTypes.NoGeometry)
        self.assertEqual(len(fac_out_feats), 1)
        self.assertEqual(len(dem_out_feats), 3)

    def test_mclp_weights(self):
        """The weight field affects the outcome of the MCLP algorithm."""

        params = {
            "INPUT_MATRIX_LAYER": self.od_matrix,
            "INPUT_SERVICE_RADIUS": 500,
            "INPUT_FAC_LAYER": self.fac_layer,
            "INPUT_FAC_ID": "id",
            "INPUT_DEM_POINT_LAYER": self.dem_layer,
            "INPUT_DEM_ID": "id",
            "INPUT_N_FAC": 1,
        }

        alg = MCLPAlgorithm()
        (
            fac_out_feats,
            fac_geom_type,
            dem_out_feats,
            dem_geom_type,
        ) = self.run_spopt_algorithm(alg, params)

        self.assertEqual(len(fac_out_feats), 1)
        self.assertEqual(len(dem_out_feats), 12)

        params = {
            "INPUT_MATRIX_LAYER": self.od_matrix,
            "INPUT_SERVICE_RADIUS": 500,
            "INPUT_FAC_LAYER": self.fac_layer,
            "INPUT_FAC_ID": "id",
            "INPUT_DEM_POINT_LAYER": self.dem_layer,
            "INPUT_DEM_ID": "id",
            "INPUT_DEM_WEIGHTS": "weights",
            "INPUT_N_FAC": 1,
        }

        alg = MCLPAlgorithm()
        (
            fac_out_feats_weights,
            fac_geom_type_weights,
            dem_out_feats_weights,
            dem_geom_type_weights,
        ) = self.run_spopt_algorithm(alg, params)

        self.assertEqual(len(fac_out_feats_weights), 1)
        self.assertEqual(len(dem_out_feats_weights), 4)

        # the input weights should be transferred to the output features
        self.assertEqual([f["weight"] for f in dem_out_feats_weights], [1, 1, 15, 1])

    def test_mclp_n_fac(self):
        """The number of facilities parameter affects the outcome of the MCLP algorithm."""

        params = {
            "INPUT_MATRIX_LAYER": self.od_matrix,
            "INPUT_SERVICE_RADIUS": 500,
            "INPUT_FAC_LAYER": self.fac_layer,
            "INPUT_FAC_ID": "id",
            "INPUT_DEM_POINT_LAYER": self.dem_layer,
            "INPUT_DEM_ID": "id",
            "INPUT_N_FAC": 1,
        }

        alg = MCLPAlgorithm()
        (
            fac_out_feats,
            fac_geom_type,
            dem_out_feats,
            dem_geom_type,
        ) = self.run_spopt_algorithm(alg, params)

        self.assertEqual(len(fac_out_feats), 1)
        self.assertEqual(len(dem_out_feats), 12)

        params = {
            "INPUT_MATRIX_LAYER": self.od_matrix,
            "INPUT_SERVICE_RADIUS": 500,
            "INPUT_FAC_LAYER": self.fac_layer,
            "INPUT_FAC_ID": "id",
            "INPUT_DEM_POINT_LAYER": self.dem_layer,
            "INPUT_DEM_ID": "id",
            "INPUT_N_FAC": 3,
        }

        alg = MCLPAlgorithm()
        (
            fac_out_feats_3_fac,
            _,
            dem_out_feats_3_fac,
            __,
        ) = self.run_spopt_algorithm(alg, params)

        self.assertEqual(len(fac_out_feats_3_fac), 3)
        self.assertEqual(len(dem_out_feats_3_fac), 21)

    def test_mclp_too_many_facilities(self):
        """Specifying more facilities to be sited than available facilities raises a processing exception."""
        params = {
            "INPUT_MATRIX_LAYER": self.od_matrix,
            "INPUT_SERVICE_RADIUS": 500,
            "INPUT_FAC_LAYER": self.fac_layer,
            "INPUT_FAC_ID": "id",
            "INPUT_DEM_POINT_LAYER": self.dem_layer,
            "INPUT_DEM_ID": "id",
            "INPUT_N_FAC": 4,
        }

        alg = MCLPAlgorithm()
        with self.assertRaises(QgsProcessingException):
            self.run_spopt_algorithm(alg, params)

    def test_mclp_weights_predefined(self):
        """If predefined facilities are specified on top of weights for the MCLP algorithm, it changes the result."""
        params = {
            "INPUT_MATRIX_LAYER": self.od_matrix,
            "INPUT_SERVICE_RADIUS": 600,
            "INPUT_FAC_LAYER": self.fac_layer,
            "INPUT_FAC_ID": "id",
            "INPUT_DEM_POINT_LAYER": self.dem_layer,
            "INPUT_DEM_ID": "id",
            "INPUT_DEM_WEIGHTS": "weights",
            "INPUT_N_FAC": 1,
        }

        alg = MCLPAlgorithm()
        (
            fac_out_feats,
            fac_geom_type,
            dem_out_feats,
            dem_geom_type,
        ) = self.run_spopt_algorithm(alg, params)

        self.assertEqual(len(fac_out_feats), 1)
        self.assertEqual(fac_out_feats[0]["id"], 2)

        self.assertEqual(len(dem_out_feats), 5)

        params = {
            "INPUT_MATRIX_LAYER": self.od_matrix,
            "INPUT_SERVICE_RADIUS": 600,
            "INPUT_FAC_LAYER": self.fac_layer,
            "INPUT_FAC_ID": "id",
            "INPUT_PREDEFINED_FAC_FIELD": "predefined",
            "INPUT_DEM_POINT_LAYER": self.dem_layer,
            "INPUT_DEM_ID": "id",
            "INPUT_N_FAC": 1,
        }

        alg = MCLPAlgorithm()
        (
            fac_out_feats_predef,
            _,
            dem_out_feats_3_fac_predef,
            __,
        ) = self.run_spopt_algorithm(alg, params)

        self.assertEqual(len(fac_out_feats_predef), 1)
        self.assertEqual(fac_out_feats_predef[0]["id"], 3)
        self.assertEqual(len(dem_out_feats_3_fac_predef), 8)
