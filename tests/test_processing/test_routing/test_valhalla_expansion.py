from tests.test_processing.processing_base import ProcessingBase
from tests.utilities import get_qgis_app

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

from qvalhalla.global_definitions import RouterProfile
from qvalhalla.processing.routing.valhalla.expansion import ValhallaExpansion


class TestValhallaExpansion(ProcessingBase):
    def test_expansion_basic(self):
        """Valhalla expansion processing algorithm returns features with http method."""
        params = {"INPUT_LAYER_1": self.layer_1, "INPUT_INTERVALS": "50, 100"}
        alg = ValhallaExpansion(profile=RouterProfile.CAR)
        feats, progress_changed_vals = self.run_routing_algorithm(alg, params)

        self.assertGreater(len(feats), 50)
        self.assertEqual(progress_changed_vals, [33, 66, 100])

    # def test_expansion_bindings(self):
    #     """Valhalla expansion processing algorithm returns features with bindings method."""
    #     params = {
    #         "INPUT_METHOD": RouterMethod.LOCAL,
    #         "INPUT_PACKAGE": "andorra_tiles.tar",
    #         "INPUT_LAYER_1": self.layer_1,
    #         "INPUT_INTERVALS": "50, 100",
    #     }
    #     alg = ValhallaExpansion(profile=RouterProfile.CAR)
    #     feats, progress_changed_vals = self.run_routing_algorithm(alg, params)

    #     self.assertGreater(len(feats), 50)
    #     self.assertEqual(progress_changed_vals, [33, 66, 100])
