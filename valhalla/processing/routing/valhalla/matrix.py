from typing import Union

from ....global_definitions import RouterProfile, RouterType
from ...routing.matrix_base import MatrixBase


class ValhallaMatrixBase(MatrixBase):
    def __init__(self, profile: Union[RouterProfile, str]):
        super(ValhallaMatrixBase, self).__init__(provider=RouterType.VALHALLA, profile=profile)


class ValhallaMatrixCar(ValhallaMatrixBase):
    def __init__(self):
        super(ValhallaMatrixCar, self).__init__(profile=RouterProfile.CAR)


class ValhallaMatrixTruck(ValhallaMatrixBase):
    def __init__(self):
        super(ValhallaMatrixTruck, self).__init__(profile=RouterProfile.TRUCK)


class ValhallaMatrixMotorcycle(ValhallaMatrixBase):
    def __init__(self):
        super(ValhallaMatrixMotorcycle, self).__init__(profile=RouterProfile.MBIKE)


class ValhallaMatrixPedestrian(ValhallaMatrixBase):
    def __init__(self):
        super(ValhallaMatrixPedestrian, self).__init__(profile=RouterProfile.PED)


class ValhallaMatrixBicycle(ValhallaMatrixBase):
    def __init__(self):
        super(ValhallaMatrixBicycle, self).__init__(profile=RouterProfile.BIKE)
