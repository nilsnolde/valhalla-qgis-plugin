from qgis.core import QgsWkbTypes

from ....utilities import get_qgis_app
from ...test_processing.processing_base import ProcessingBase

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

from valhalla.processing.routing.valhalla.elevation import ValhallaElevation


class TestValhallaHeight(ProcessingBase):
    def test_line_basic(self):
        params = {"INPUT_LAYER_1": self.layer_1}
        params["INPUT_PROVIDER"] = 1

        alg = ValhallaElevation()
        feats, _ = self.run_routing_algorithm(alg, params)

        self.assertEqual(len(feats), self.layer_1.featureCount())
        for feat in feats:
            QgsWkbTypes.hasZ(feat.geometry().wkbType())
