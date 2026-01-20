from qgis.core import QgsProcessingProvider
from qgis.PyQt.QtGui import QIcon

from .. import PLUGIN_NAME, __version__
from ..processing.routing.valhalla.elevation import ValhallaElevation
from ..processing.routing.valhalla.expansion import (
    ValhallaExpansionBicycle,
    ValhallaExpansionCar,
    ValhallaExpansionMotorcycle,
    ValhallaExpansionPedestrian,
    ValhallaExpansionTruck,
)
from ..processing.routing.valhalla.matrix import (
    ValhallaMatrixBicycle,
    ValhallaMatrixCar,
    ValhallaMatrixMotorcycle,
    ValhallaMatrixPedestrian,
    ValhallaMatrixTruck,
)
from ..processing.routing.valhalla.optimized import (
    ValhallaOptimizedDirectionsBicycle,
    ValhallaOptimizedDirectionsCar,
    ValhallaOptimizedDirectionsMotorcycle,
    ValhallaOptimizedDirectionsPedestrian,
    ValhallaOptimizedDirectionsTruck,
)

# from valhalla.processing.spatial_optimization.lscp import LSCPAlgorithm
# from valhalla.processing.spatial_optimization.mclp import MCLPAlgorithm
# from valhalla.processing.spatial_optimization.pcenter import PCenterAlgorithm
# from valhalla.processing.spatial_optimization.pmedian import PMedianAlgorithm
from ..utils.resource_utils import get_icon
from .routing.valhalla.directions import (
    ValhallaDirectionsBicycle,
    ValhallaDirectionsCar,
    ValhallaDirectionsMotorcycle,
    ValhallaDirectionsPedestrian,
    ValhallaDirectionsTruck,
)
from .routing.valhalla.isochrones import (
    ValhallaIsochroneBicycle,
    ValhallaIsochroneCar,
    ValhallaIsochroneMotorcycle,
    ValhallaIsochronePedestrian,
    ValhallaIsochroneTruck,
)
from .routing.valhalla.mapmatch import (
    ValhallaMapMatchBicycle,
    ValhallaMapMatchCar,
    ValhallaMapMatchMotorcycle,
    ValhallaMapMatchPedestrian,
    ValhallaMapMatchTruck,
)


class ValhallaProvider(QgsProcessingProvider):
    def __init__(self):
        QgsProcessingProvider.__init__(self)

        self.algorithm_list = [
            *[
                algo()
                for algo in (
                    ValhallaElevation,
                    ValhallaDirectionsCar,
                    ValhallaDirectionsTruck,
                    ValhallaDirectionsMotorcycle,
                    ValhallaDirectionsPedestrian,
                    ValhallaDirectionsBicycle,
                    ValhallaIsochroneCar,
                    ValhallaIsochroneTruck,
                    ValhallaIsochroneMotorcycle,
                    ValhallaIsochroneBicycle,
                    ValhallaIsochronePedestrian,
                    ValhallaExpansionCar,
                    ValhallaExpansionTruck,
                    ValhallaExpansionMotorcycle,
                    ValhallaExpansionBicycle,
                    ValhallaExpansionPedestrian,
                    ValhallaMatrixCar,
                    ValhallaMatrixTruck,
                    ValhallaMatrixMotorcycle,
                    ValhallaMatrixBicycle,
                    ValhallaMatrixPedestrian,
                    ValhallaOptimizedDirectionsCar,
                    ValhallaOptimizedDirectionsTruck,
                    ValhallaOptimizedDirectionsMotorcycle,
                    ValhallaOptimizedDirectionsPedestrian,
                    ValhallaOptimizedDirectionsBicycle,
                    ValhallaMapMatchCar,
                    ValhallaMapMatchTruck,
                    ValhallaMapMatchMotorcycle,
                    ValhallaMapMatchPedestrian,
                    ValhallaMapMatchBicycle,
                )
            ],
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
