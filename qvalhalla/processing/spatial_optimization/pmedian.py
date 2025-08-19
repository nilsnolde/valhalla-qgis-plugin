from qvalhalla.global_definitions import SpOptTypes
from qvalhalla.processing.spatial_optimization.base_algorithm import (
    SPOPTBaseAlgorithm,
)


class PMedianAlgorithm(SPOPTBaseAlgorithm):
    NAME = "pmedian"

    def __init__(self):
        super(PMedianAlgorithm, self).__init__(problem_type=SpOptTypes.PMEDIAN)

    def displayName(self):
        return "P-Median Problem"
