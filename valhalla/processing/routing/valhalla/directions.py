from ....global_definitions import RouterProfile, RouterType
from ..directions_base import DirectionsBase


class ValhallaDirectionsCar(DirectionsBase):
    def __init__(self):
        super(ValhallaDirectionsCar, self).__init__(
            provider=RouterType.VALHALLA, profile=RouterProfile.CAR
        )


class ValhallaDirectionsTruck(DirectionsBase):
    def __init__(self):
        super(ValhallaDirectionsTruck, self).__init__(
            provider=RouterType.VALHALLA, profile=RouterProfile.TRUCK
        )


class ValhallaDirectionsMotorcycle(DirectionsBase):
    def __init__(self):
        super(ValhallaDirectionsMotorcycle, self).__init__(
            provider=RouterType.VALHALLA, profile=RouterProfile.MBIKE
        )


class ValhallaDirectionsPedestrian(DirectionsBase):
    def __init__(self):
        super(ValhallaDirectionsPedestrian, self).__init__(
            provider=RouterType.VALHALLA, profile=RouterProfile.PED
        )


class ValhallaDirectionsBicycle(DirectionsBase):
    def __init__(self):
        super(ValhallaDirectionsBicycle, self).__init__(
            provider=RouterType.VALHALLA, profile=RouterProfile.BIKE
        )
