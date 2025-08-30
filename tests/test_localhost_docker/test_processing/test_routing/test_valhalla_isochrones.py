from ....utilities import get_qgis_app
from ..processing_base import ProcessingBase

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

from qvalhalla.global_definitions import RouterProfile
from qvalhalla.processing.routing.valhalla.isochrones import ValhallaIsochrones


class TestValhallaIsochrones(ProcessingBase):
    def test_isochrones_basic(self):
        """Valhalla isochrones processing algorithm returns features with HTTP method."""
        params = {
            "INPUT_LAYER_1": self.layer_1,
            "INPUT_INTERVALS": "50, 100",
        }
        params["INPUT_PROVIDER"] = 1
        alg = ValhallaIsochrones(profile=RouterProfile.CAR)
        feats, progress_changed_vals = self.run_routing_algorithm(alg, params)

        self.assertEqual(len(feats), 6)
        self.assertEqual(progress_changed_vals, [33, 66, 100])
