from tests.constants import WAYPOINTS_4326_MAP_MATCH

from ....utilities import get_qgis_app
from ...test_processing.processing_base import ProcessingBase

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

from valhalla.processing.routing.valhalla.mapmatch import ValhallaMapMatchCar


class TestValhallaTraceRoute(ProcessingBase):
    WAYPOINTS = WAYPOINTS_4326_MAP_MATCH

    def test_line_basic(self):
        params = {"INPUT_LAYER_1": self.layer_line}

        alg = ValhallaMapMatchCar()
        feats, _ = self.run_routing_algorithm(alg, params)

        self.assertEqual(len(feats), 1)
