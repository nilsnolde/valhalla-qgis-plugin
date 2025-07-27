from typing import Union

from ....global_definitions import RouterProfile, RouterType
from ....processing.routing.directions_base import DirectionsBase


class ValhallaDirections(DirectionsBase):
    def __init__(self, profile: Union[RouterProfile, str]):
        super(ValhallaDirections, self).__init__(
            provider=RouterType.VALHALLA, profile=RouterProfile(profile)
        )
