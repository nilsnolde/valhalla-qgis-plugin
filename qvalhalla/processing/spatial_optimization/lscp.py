from qvalhalla.global_definitions import SpOptTypes
from qvalhalla.processing.spatial_optimization.base_algorithm import (
    SPOPTBaseAlgorithm,
)


class LSCPAlgorithm(SPOPTBaseAlgorithm):
    NAME = "lscp"

    def __init__(self):
        super(LSCPAlgorithm, self).__init__(problem_type=SpOptTypes.LSCP)

    def displayName(self):
        return "Location Set Covering Problem"
