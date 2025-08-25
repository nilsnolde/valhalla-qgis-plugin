import platform
from collections import namedtuple
from enum import Enum
from pathlib import Path
from typing import Dict, Tuple

from qgis.core import QgsField
from qgis.PyQt.QtCore import QVariant

from .gui.widgets.costing_settings.widget_settings_valhalla_bike import (
    ValhallaSettingsBikeWidget,
)
from .gui.widgets.costing_settings.widget_settings_valhalla_car import (
    ValhallaSettingsCarWidget,
)
from .gui.widgets.costing_settings.widget_settings_valhalla_mbike import (
    ValhallaSettingsMbikeWidget,
)
from .gui.widgets.costing_settings.widget_settings_valhalla_pedestrian import (
    ValhallaSettingsPedestrianWidget,
)
from .gui.widgets.costing_settings.widget_settings_valhalla_truck import (
    ValhallaSettingsTruckWidget,
)
from .utils.misc_utils import IndexableStrEnum


class Dialogs(Enum):
    ROUTER_WIDGET = "valhalla_router_widget"
    WAYPOINT_WIDGET = "valhalla_waypoint_widget"
    ROUTER_OPTS = "valhalla_router_options"
    COST_OPTS = "valhalla_costing_options"
    ROUTING = "valhalla_routing"
    SETTINGS = "valhalla_settings"
    PROVIDERS = "valhalla_providers"


class RouterType(str, Enum):
    VALHALLA = "valhalla"
    OSRM = "osrm"


class RouterMethod(IndexableStrEnum):
    REMOTE = "remote"
    LOCAL = "local"


# values are governed by routingpy
class RouterEndpoint(IndexableStrEnum):  # TODO: look for case where this can replace code
    DIRECTIONS = "directions"
    ISOCHRONES = "isochrones"
    MATRIX = "matrix"
    EXPANSION = "expansion"


class RouterProfile(str, Enum):
    PED = "pedestrian"
    BIKE = "bicycle"
    CAR = "auto"
    MBIKE = "motorcycle"
    TRUCK = "truck"


class RoutingMetric(IndexableStrEnum):
    FASTEST = "fastest"
    SHORTEST = "shortest"


class FieldNames(str, Enum):
    ID = "id"
    LOCATION_ID = "location_id"  # expansion endpoint
    FACILITY_ID = "facility_id"
    SOURCE = "source"
    TARGET = "target"
    PROVIDER = "provider"
    PROFILE = "profile"
    METRIC = "metric"
    DURATION = "duration"
    DISTANCE = "distance"
    CONTOUR = "contour"
    OPTIONS = "options"
    WEIGHT = "weight"
    PREDEFINED = "predefined"


DEFAULT_LAYER_FIELDS: Dict[RouterEndpoint, Tuple[QgsField, ...]] = {
    RouterEndpoint.ISOCHRONES: (
        QgsField(FieldNames.PROVIDER, QVariant.String),
        QgsField(FieldNames.PROFILE, QVariant.String),
        QgsField(FieldNames.METRIC, QVariant.String),
        QgsField(FieldNames.CONTOUR, QVariant.Int),
        QgsField(FieldNames.OPTIONS, QVariant.String),
    ),
    RouterEndpoint.DIRECTIONS: (
        QgsField(FieldNames.PROVIDER, QVariant.String),
        QgsField(FieldNames.PROFILE, QVariant.String),
        QgsField(FieldNames.DURATION, QVariant.Double),
        QgsField(FieldNames.DISTANCE, QVariant.Double),
        QgsField(FieldNames.OPTIONS, QVariant.String),
    ),
    RouterEndpoint.MATRIX: (
        QgsField(FieldNames.PROVIDER, QVariant.String),
        QgsField(FieldNames.PROFILE, QVariant.String),
        QgsField(FieldNames.SOURCE, QVariant.Int),
        QgsField(FieldNames.TARGET, QVariant.Int),
        QgsField(FieldNames.DURATION, QVariant.Double),
        QgsField(FieldNames.DISTANCE, QVariant.Double),
        QgsField(FieldNames.OPTIONS, QVariant.String),
    ),
    RouterEndpoint.EXPANSION: (
        QgsField(FieldNames.PROVIDER, QVariant.String),
        QgsField(FieldNames.PROFILE, QVariant.String),
        QgsField(FieldNames.METRIC, QVariant.String),
        QgsField(FieldNames.DURATION, QVariant.Double),
        QgsField(FieldNames.DISTANCE, QVariant.Double),
        QgsField(FieldNames.OPTIONS, QVariant.String),
    ),
}


SETTINGS_WIDGETS_MAP = {
    RouterProfile.PED: {
        "widget": ValhallaSettingsPedestrianWidget,
        "ui_name": "settings_valhalla_pedestrian",
    },
    RouterProfile.BIKE: {
        "widget": ValhallaSettingsBikeWidget,
        "ui_name": "settings_valhalla_bike",
    },
    RouterProfile.CAR: {
        "widget": ValhallaSettingsCarWidget,
        "ui_name": "settings_valhalla_car",
    },
    RouterProfile.TRUCK: {
        "widget": ValhallaSettingsTruckWidget,
        "ui_name": "settings_valhalla_mbike",
    },
    RouterProfile.MBIKE: {
        "widget": ValhallaSettingsMbikeWidget,
        "ui_name": "settings_valhalla_truck",
    },
}

# determine the python executable path from a random std lib
if platform.system() == "Linux":
    PYTHON_EXE = "python3"
elif platform.system() == "Windows":
    PYTHON_EXE = Path(platform.__file__).parent.parent.joinpath("python.exe").resolve()
else:
    PYTHON_EXE = Path(platform.__file__).parent.parent.joinpath("python").resolve()


PyPiPkg = namedtuple("PyPiPkg", ("import_name", "pypi_name", "url"))
PYPI_PKGS = (
    PyPiPkg("valhalla", "pyvalhalla-weekly", "https://pypi.org/project/pyvalhalla-weekly/"),
    # PyPiPkg("vroom", "pyvroom", "https://github.com/VROOM-Project/pyvroom"),
    # PyPiPkg("spopt", "spopt", "https://github.com/pysal/spopt"),
)


class PyPiState(Enum):
    NOT_INSTALLED = 0
    UPGRADEABLE = 1
    UP_TO_DATE = 2


class SpOptTypes(str, Enum):
    LSCP = "lscp"
    MCLP = "mclp"
    PCENTER = "pcenter"
    PMEDIAN = "pmedian"
