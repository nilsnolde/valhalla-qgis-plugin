from qgis.core import QgsWkbTypes
from qvalhalla.processing.spatial_optimization.pcenter import PCenterAlgorithm

from .UNUSED_spopt_base import SpOptProcessingBase


class TestPCenter(SpOptProcessingBase):
    def test_pcenter_minimal_params(self):
        """The P-Center algorithm works with only the matrix input and the service radius specified."""
        params = {"INPUT_MATRIX_LAYER": self.od_matrix, "INPUT_N_FAC": 1}

        alg = PCenterAlgorithm()
        (
            fac_out_feats,
            fac_geom_type,
            dem_out_feats,
            dem_geom_type,
        ) = self.run_spopt_algorithm(alg, params)

        self.assertEqual(fac_geom_type, QgsWkbTypes.NoGeometry)
        self.assertEqual(dem_geom_type, QgsWkbTypes.NoGeometry)
        self.assertEqual(len(fac_out_feats), 1)
        self.assertEqual(len(dem_out_feats), 15)

    def test_pcenter_with_source_layers(self):
        """The P-Center algorithm works with source facility and demand point layers and their ID columns specified."""
        params = {
            "INPUT_MATRIX_LAYER": self.od_matrix,
            "INPUT_FAC_LAYER": self.fac_layer,
            "INPUT_FAC_ID": "id",
            "INPUT_DEM_POINT_LAYER": self.dem_layer,
            "INPUT_DEM_ID": "id",
        }

        alg = PCenterAlgorithm()
        (
            fac_out_feats,
            fac_geom_type,
            dem_out_feats,
            dem_geom_type,
        ) = self.run_spopt_algorithm(alg, params)

        self.assertEqual(fac_geom_type, QgsWkbTypes.Point)
        self.assertEqual(dem_geom_type, QgsWkbTypes.Point)
        self.assertEqual(len(fac_out_feats), 1)
        self.assertEqual(len(dem_out_feats), 15)

    def test_pcenter_n_fac(self):
        """The P-Center algorithm works as expected when a number of facilities to be sited is specified."""

        params = {"INPUT_MATRIX_LAYER": self.od_matrix, "INPUT_N_FAC": 3}

        alg = PCenterAlgorithm()
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

    def test_pcenter_draw_lines(self):
        """The P-Center algorithm draws connecting lines."""

        alg = PCenterAlgorithm()
        params = {
            alg.IN_MATRIX_SOURCE: self.od_matrix,
            alg.IN_FAC_SOURCE: self.fac_layer,
            alg.IN_FAC_ID: "id",
            alg.IN_DEM_SOURCE: self.dem_layer,
            alg.IN_DEM_ID: "id",
            alg.IN_LINES: True,
        }

        (
            fac_out_feats,
            fac_geom_type,
            dem_out_feats,
            dem_geom_type,
        ) = self.run_spopt_algorithm(alg, params)

        self.assertEqual(fac_geom_type, QgsWkbTypes.Point)
        self.assertEqual(dem_geom_type, QgsWkbTypes.LineString)
        self.assertEqual(len(fac_out_feats), 1)
        self.assertEqual(len(dem_out_feats), 15)

    def test_pcenter_draw_lines_utm(self):
        """The P-Center algorithm draws connecting lines from UTM layers."""

        alg = PCenterAlgorithm()
        params = {
            alg.IN_MATRIX_SOURCE: self.od_matrix,
            alg.IN_FAC_SOURCE: self.fac_layer_utm,
            alg.IN_FAC_ID: "id",
            alg.IN_DEM_SOURCE: self.dem_layer_utm,
            alg.IN_DEM_ID: "id",
            alg.IN_LINES: True,
        }

        (
            fac_out_feats,
            fac_geom_type,
            dem_out_feats,
            dem_geom_type,
        ) = self.run_spopt_algorithm(alg, params)

        self.assertEqual(fac_geom_type, QgsWkbTypes.Point)
        self.assertEqual(dem_geom_type, QgsWkbTypes.LineString)
        self.assertEqual(len(fac_out_feats), 1)
        self.assertEqual(len(dem_out_feats), 15)

        # check if coordinate is in ballpark of UTM coordinate (meters)
        self.assertGreater(dem_out_feats[0].geometry().asPolyline()[0].x(), 800000)
