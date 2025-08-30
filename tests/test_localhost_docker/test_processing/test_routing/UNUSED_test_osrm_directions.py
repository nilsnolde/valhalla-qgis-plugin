from qgis.core import (
    QgsProcessingContext,
    QgsProcessingException,
    QgsProcessingFeedback,
)
from qvalhalla.processing.routing.osrm.directions import OSRMDirections

from ....utilities import get_qgis_app
from ...test_processing.processing_base import ProcessingBase

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()


class TestOSRMDirections(ProcessingBase):
    def test_single_point(self):
        params = {"INPUT_LAYER_1": self.layer_1}
        alg = OSRMDirections()
        feats, _ = self.run_routing_algorithm(alg, params)

        self.assertEqual(len(feats), 1)

    def test_avoid_polygon(self):
        params = {
            "INPUT_LAYER_1": self.layer_1,
            "INPUT_AVOID_POLYGONS": self.avoid_polygon_layer,
        }
        alg = OSRMDirections()
        feats, _ = self.run_routing_algorithm(alg, params)
        self.assertEqual(len(feats), 1)

    def test_multi_point(self):
        params = {"INPUT_LAYER_1": self.layer_mp}
        alg = OSRMDirections()
        feats, _ = self.run_routing_algorithm(alg, params)

        self.assertEqual(len(feats), 2)

    def test_two_layers_row_by_row(self):
        params = {
            "INPUT_LAYER_1": self.layer_1,
            "INPUT_LAYER_2": self.layer_2,
            "INPUT_FIELD_1": "ID",
            "INPUT_FIELD_2": "ID",
            "INPUT_MERGE_STRATEGY": 0,
        }
        alg = OSRMDirections()
        feats, _ = self.run_routing_algorithm(alg, params)

        self.assertEqual(len(feats), 3)

    def test_two_layers_all_by_all(self):
        params = {
            "INPUT_LAYER_1": self.layer_1,
            "INPUT_LAYER_2": self.layer_2,
            "INPUT_MERGE_STRATEGY": 1,
        }
        alg = OSRMDirections()
        feats, _ = self.run_routing_algorithm(alg, params)

        self.assertEqual(len(feats), 9)

    def test_two_layers_fail(self):
        """Tests whether specifying only one field with the row-by-row strategy raises an exception."""
        params = {
            "INPUT_LAYER_1": self.layer_1,
            "INPUT_LAYER_2": self.layer_2,
            "INPUT_FIELD_1": "ID",
            "INPUT_MERGE_STRATEGY": 0,
        }

        alg = OSRMDirections()
        alg.initAlgorithm({})
        ctx = QgsProcessingContext()
        feedback = QgsProcessingFeedback()
        alg.prepareAlgorithm(params, ctx, feedback)
        with self.assertRaises(QgsProcessingException):
            alg.processAlgorithm(params, ctx, feedback)
