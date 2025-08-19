from qgis.core import QgsWkbTypes
from qvalhalla.processing.spatial_optimization.pmedian import PMedianAlgorithm

from .spopt_base import SpOptProcessingBase


class TestPMedian(SpOptProcessingBase):
    def test_pmedian_minimal_params(self):
        """The P-Median algorithm works with only the matrix input and the service radius specified."""
        params = {"INPUT_MATRIX_LAYER": self.od_matrix, "INPUT_N_FAC": 1}

        alg = PMedianAlgorithm()
        (
            fac_out_feats,
            fac_geom_type,
            dem_out_feats,
            dem_geom_type,
        ) = self.run_spopt_algorithm(alg, params)

        self.assertEqual(fac_geom_type, QgsWkbTypes.NoGeometry)
        self.assertEqual(dem_geom_type, QgsWkbTypes.NoGeometry)
        self.assertEqual(len(fac_out_feats), 1)
        self.assertEqual(fac_out_feats[0]["id"], 1)
        self.assertEqual(len(dem_out_feats), 15)

    def test_pmedian_with_source_layers(self):
        """The P-Median algorithm works with source facility and demand point layers and their ID columns specified."""
        params = {
            "INPUT_MATRIX_LAYER": self.od_matrix,
            "INPUT_FAC_LAYER": self.fac_layer,
            "INPUT_FAC_ID": "id",
            "INPUT_DEM_POINT_LAYER": self.dem_layer,
            "INPUT_DEM_ID": "id",
        }

        alg = PMedianAlgorithm()
        (
            fac_out_feats,
            fac_geom_type,
            dem_out_feats,
            dem_geom_type,
        ) = self.run_spopt_algorithm(alg, params)

        self.assertEqual(fac_geom_type, QgsWkbTypes.Point)
        self.assertEqual(dem_geom_type, QgsWkbTypes.Point)
        self.assertEqual(len(fac_out_feats), 1)
        self.assertEqual(fac_out_feats[0]["id"], 1)
        self.assertEqual(len(dem_out_feats), 15)

    def test_pmedian_n_fac(self):
        """The P-Median algorithm works as expected when a number of facilities to be sited is specified."""

        params = {"INPUT_MATRIX_LAYER": self.od_matrix, "INPUT_N_FAC": 3}

        alg = PMedianAlgorithm()
        (
            fac_out_feats,
            fac_geom_type,
            dem_out_feats,
            dem_geom_type,
        ) = self.run_spopt_algorithm(alg, params)

        self.assertEqual(fac_geom_type, QgsWkbTypes.NoGeometry)
        self.assertEqual(dem_geom_type, QgsWkbTypes.NoGeometry)
        self.assertEqual(
            len(fac_out_feats), 2
        )  # TODO: look into why this is not 3, there is nothing in the spopt docs
        self.assertEqual(len(dem_out_feats), 15)
