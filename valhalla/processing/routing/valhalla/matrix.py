from typing import Union

from ....global_definitions import RouterProfile, RouterType
from ...routing.matrix_base import MatrixBase


class ValhallaMatrix(MatrixBase):
    def __init__(self, profile: Union[RouterProfile, str]):
        super(ValhallaMatrix, self).__init__(provider=RouterType.VALHALLA, profile=profile)
