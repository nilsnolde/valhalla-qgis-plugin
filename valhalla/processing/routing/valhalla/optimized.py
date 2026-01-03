from typing import Union

from ....global_definitions import RouterEndpoint, RouterProfile, RouterType
from ..directions_base import DirectionsBase


class ValhallaOptimizedDirections(DirectionsBase):
    def __init__(self, profile: Union[RouterProfile, str]):
        super(DirectionsBase, self).__init__(
            provider=RouterType.VALHALLA, endpoint=RouterEndpoint.TSP, profile=RouterProfile(profile)
        )
