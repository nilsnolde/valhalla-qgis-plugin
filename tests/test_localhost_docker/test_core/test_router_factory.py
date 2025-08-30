from qvalhalla.core.router_factory import RouterFactory
from qvalhalla.global_definitions import (
    RouterEndpoint,
    RouterMethod,
    RouterProfile,
    RouterType,
)
from qvalhalla.third_party.routingpy.routingpy.direction import Direction

from ... import LocalhostDockerTestCase
from ...constants import WAYPOINTS_4326


class TestRouterFactory(LocalhostDockerTestCase):
    """Test interface to routingpy."""

    def test_router_factory_valhalla_http_directions(self):
        factory = RouterFactory(
            RouterType.VALHALLA,
            RouterMethod.REMOTE,
            RouterProfile.PED,
            url="http://localhost:8002",
        )
        direction: Direction = factory.request(
            RouterEndpoint.DIRECTIONS,
            locations=[[x, y] for x, y in WAYPOINTS_4326],
        )
        self.assertIsInstance(direction, Direction)

        self.assertGreater(len(direction.geometry), 0)
