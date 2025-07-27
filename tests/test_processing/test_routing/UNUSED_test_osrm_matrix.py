from tests.test_processing.processing_base import ProcessingBase
from tests.utilities import get_qgis_app

from valhalla.processing.routing.osrm.matrix import OSRMMatrix

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()


class TestOSRMMatrix(ProcessingBase):
    def test_matrix_basic(self):
        params = {
            "INPUT_LAYER_1": self.layer_1,
            "INPUT_LAYER_2": self.layer_2,
            "INPUT_FIELD_1": "ID",
            "INPUT_FIELD_2": "ID",
        }
        alg = OSRMMatrix()
        feats, _ = self.run_routing_algorithm(alg, params)
        self.assertEqual(len(feats), 9)
