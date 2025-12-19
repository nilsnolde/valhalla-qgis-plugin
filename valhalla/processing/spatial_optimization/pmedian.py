from valhalla.global_definitions import SpOptTypes
from valhalla.processing.spatial_optimization.base_algorithm import (
    SPOPTBaseAlgorithm,
)


class PMedianAlgorithm(SPOPTBaseAlgorithm):
    NAME = "pmedian"

    def __init__(self):
        super(PMedianAlgorithm, self).__init__(problem_type=SpOptTypes.PMEDIAN)

    def displayName(self):
        return "P-Median Problem"
