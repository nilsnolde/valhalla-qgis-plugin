from qgis.PyQt.QtCore import QVariant

from ...utilities import get_qgis_app
from ..processing_base import ProcessingBase

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

from valhalla.global_definitions import FieldNames, RouterProfile
from valhalla.processing.routing.valhalla.matrix import ValhallaMatrix


class TestValhallaMatrix(ProcessingBase):
    def test_matrix_basic(self):
        params = {
            "INPUT_LAYER_1": self.layer_1,
            "INPUT_LAYER_2": self.layer_2,
            "INPUT_FIELD_1": "ID",
            "INPUT_FIELD_2": "ID_str",
        }
        alg = ValhallaMatrix(profile=RouterProfile.PED)
        feats, _ = self.run_routing_algorithm(alg, params)
        self.assertEqual(len(feats), 9)
        self.assertEqual(feats[0].fields().field(FieldNames.SOURCE).type(), QVariant.Int)
        self.assertEqual(feats[0].fields().field(FieldNames.TARGET).type(), QVariant.String)

    # def test_matrix_bindings(self):
    #     """Valhalla matrix processing algorithm returns features with correct fields using bindings."""
    #     params = {
    #         "INPUT_METHOD": RouterMethod.LOCAL,
    #         "INPUT_PACKAGE": "andorra_tiles.tar",
    #         "INPUT_LAYER_1": self.layer_1,
    #         "INPUT_LAYER_2": self.layer_2,
    #         "INPUT_FIELD_1": "ID",
    #         "INPUT_FIELD_2": "ID_str",
    #     }
    #     alg = ValhallaMatrix(profile=RouterProfile.PED)
    #     feats, _ = self.run_routing_algorithm(alg, params)
    #     self.assertEqual(len(feats), 9)
    #     self.assertEqual(feats[0].fields().field(FieldNames.SOURCE).type(), QVariant.Int)
    #     self.assertEqual(feats[0].fields().field(FieldNames.TARGET).type(), QVariant.String)
