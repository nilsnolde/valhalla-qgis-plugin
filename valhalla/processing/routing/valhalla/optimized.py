from typing import Union

from ....global_definitions import RouterEndpoint, RouterProfile, RouterType
from ..directions_base import DirectionsBase


class ValhallaOptimizedDirectionsBase(DirectionsBase):
    def __init__(self, profile: Union[RouterProfile, str]):
        super(DirectionsBase, self).__init__(
            provider=RouterType.VALHALLA, endpoint=RouterEndpoint.TSP, profile=profile
        )


class ValhallaOptimizedDirectionsCar(ValhallaOptimizedDirectionsBase):
    def __init__(self):
        super(ValhallaOptimizedDirectionsCar, self).__init__(profile=RouterProfile.CAR)


class ValhallaOptimizedDirectionsTruck(ValhallaOptimizedDirectionsBase):
    def __init__(self):
        super(ValhallaOptimizedDirectionsTruck, self).__init__(profile=RouterProfile.TRUCK)


class ValhallaOptimizedDirectionsMotorcycle(ValhallaOptimizedDirectionsBase):
    def __init__(self):
        super(ValhallaOptimizedDirectionsMotorcycle, self).__init__(profile=RouterProfile.MBIKE)


class ValhallaOptimizedDirectionsPedestrian(ValhallaOptimizedDirectionsBase):
    def __init__(self):
        super(ValhallaOptimizedDirectionsPedestrian, self).__init__(profile=RouterProfile.PED)


class ValhallaOptimizedDirectionsBicycle(ValhallaOptimizedDirectionsBase):
    def __init__(self):
        super(ValhallaOptimizedDirectionsBicycle, self).__init__(profile=RouterProfile.BIKE)
