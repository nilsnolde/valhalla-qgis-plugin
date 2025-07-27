from tests import HTTPTestCase
from tests.constants import WAYPOINTS_4326

from valhalla.core.router_factory import RouterFactory
from valhalla.global_definitions import (
    RouterEndpoint,
    RouterMethod,
    RouterProfile,
    RouterType,
)
from valhalla.third_party.routingpy.routingpy.direction import Direction


class TestRouterFactory(HTTPTestCase):
    """Test interface to routingpy."""

    def test_router_factory_valhalla_http_directions(self):
        factory = RouterFactory(
            RouterType.VALHALLA,
            RouterMethod.REMOTE,
            RouterProfile.PED,
            url="https://valhalla1.openstreetmap.de",
        )
        direction: Direction = factory.request(
            RouterEndpoint.DIRECTIONS,
            locations=[[x, y] for x, y in WAYPOINTS_4326],
        )
        self.assertIsInstance(direction, Direction)

        self.assertGreater(len(direction.geometry), 0)
