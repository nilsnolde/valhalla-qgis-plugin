from valhalla.global_definitions import SpOptTypes
from valhalla.processing.spatial_optimization.base_algorithm import (
    SPOPTBaseAlgorithm,
)


class MCLPAlgorithm(SPOPTBaseAlgorithm):
    NAME = "mclp"

    def __init__(self):
        super(MCLPAlgorithm, self).__init__(problem_type=SpOptTypes.MCLP)

    def displayName(self):
        return "Maximal Coverage Location Problem"
