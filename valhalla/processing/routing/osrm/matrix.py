from valhalla.global_definitions import RouterType
from valhalla.processing.routing.matrix_base import MatrixBase


class OSRMMatrix(MatrixBase):
    IN_2 = "INPUT_LAYER_2"
    IN_FIELD_2 = "INPUT_FIELD_2"

    def __init__(self):
        super(OSRMMatrix, self).__init__(
            provider=RouterType.OSRM,
        )
