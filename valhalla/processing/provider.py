from qgis.core import QgsProcessingProvider
from qgis.PyQt.QtGui import QIcon

from .. import PLUGIN_NAME, __version__
from ..global_definitions import RouterProfile
from ..processing.routing.valhalla.directions import ValhallaDirections
from ..processing.routing.valhalla.elevation import ValhallaElevation
from ..processing.routing.valhalla.expansion import ValhallaExpansion
from ..processing.routing.valhalla.isochrones import ValhallaIsochrones
from ..processing.routing.valhalla.matrix import ValhallaMatrix
from ..processing.routing.valhalla.optimized import ValhallaOptimizedDirections

# from valhalla.processing.spatial_optimization.lscp import LSCPAlgorithm
# from valhalla.processing.spatial_optimization.mclp import MCLPAlgorithm
# from valhalla.processing.spatial_optimization.pcenter import PCenterAlgorithm
# from valhalla.processing.spatial_optimization.pmedian import PMedianAlgorithm
from ..utils.resource_utils import get_icon


class ValhallaProvider(QgsProcessingProvider):
    def __init__(self):
        QgsProcessingProvider.__init__(self)

        self.algorithm_list = [
            *[
                algo(profile=profile)
                for profile in RouterProfile
                for algo in (
                    ValhallaDirections,
                    ValhallaIsochrones,
                    ValhallaMatrix,
                    ValhallaExpansion,
                    ValhallaOptimizedDirections,
                )
            ],
            ValhallaElevation(None)
            # *[
            #     OSRMMatrix(),
            #     OSRMDirections(),
            #     LSCPAlgorithm(),
            #     MCLPAlgorithm(),
            #     PCenterAlgorithm(),
            #     PMedianAlgorithm(),
            # ],
        ]

    def unload(self):
        """
        Unloads the provider. Any tear-down steps required by the provider
        should be implemented here.
        """
        pass

    def loadAlgorithms(self) -> None:
        for algorithm in self.algorithm_list:
            self.addAlgorithm(algorithm)

    def icon(self) -> QIcon:
        return get_icon("valhalla_logo.svg")

    def id(self):
        """
        Returns the unique provider id, used for identifying the provider. This
        string should be a unique, short, character only string, eg "qgis" or
        "gdal". This string should not be localised.
        """
        return PLUGIN_NAME.strip().lower().replace(" ", "_")

    def name(self):
        """
        Returns the provider name, which is used to describe the provider
        within the GUI.
        This string should be short (e.g. "Lastools") and localised.
        """
        return PLUGIN_NAME

    def longName(self):
        """
        Returns the a longer version of the provider name, which can include
        extra details such as version numbers. E.g. "Lastools LIDAR tools
        (version 2.2.1)". This string should be localised. The default
        implementation returns the same string as name().
        """
        return PLUGIN_NAME + " plugin v" + __version__
