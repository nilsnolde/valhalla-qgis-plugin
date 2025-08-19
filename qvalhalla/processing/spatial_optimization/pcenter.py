from qvalhalla.global_definitions import SpOptTypes
from qvalhalla.processing.spatial_optimization.base_algorithm import (
    SPOPTBaseAlgorithm,
)


class PCenterAlgorithm(SPOPTBaseAlgorithm):
    NAME = "pcenter"

    def __init__(self):
        super(PCenterAlgorithm, self).__init__(problem_type=SpOptTypes.PCENTER)

    def displayName(self):
        return "P-Center Problem"
