from valhalla.global_definitions import RouterType
from valhalla.processing.routing.directions_base import DirectionsBase


class OSRMDirections(DirectionsBase):
    def __init__(self):
        super(OSRMDirections, self).__init__(
            provider=RouterType.OSRM,
        )
