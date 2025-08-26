from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, List, Optional, Union

from qgis.core import QgsSettings
from qgis.PyQt.QtCore import QSettings

from ..global_definitions import Dialogs, RouterType
from ..gui.ui_definitions import PluginSettingsDlgElems
from ..utils.misc_utils import str_to_bool
from ..utils.resource_utils import get_settings_dir

DEFAULTS = {
    PluginSettingsDlgElems.VALHALLA_HTTP_URL: "https://valhalla1.openstreetmap.de",
    PluginSettingsDlgElems.VALHALLA_HTTP_PARAM: "access_token",
    PluginSettingsDlgElems.DEBUG: "False"
    # PluginSettingsDlgElems.SHOP_HTTP_URL: "http://localhost:8080",
}

PROFILE_TO_OSRM_URL = {
    # RouterProfile.PED: PluginSettingsDlgElems.OSRM_HTTP_URL_PED,
    # RouterProfile.BIKE: PluginSettingsDlgElems.OSRM_HTTP_URL_BIKE,
    # RouterProfile.CAR: PluginSettingsDlgElems.OSRM_HTTP_URL_CAR,
}

IGNORE_PYPI = "ignore_pypi"
PLUGIN_VERSION = "plugin_version"


@dataclass
class ProviderSetting:
    name: str
    url: str
    auth_key: str
    auth_param: str


DEFAULT_PROVIDERS = [
    ProviderSetting("FOSSGIS", "https://valhalla1.openstreetmap.de", "", "access_key"),  # auth_key
    ProviderSetting("localhost", "http://localhost:8002", "", ""),  # auth_key
]

DEFAULT_GRAPH_DIR: Path = get_settings_dir().joinpath("graph_dir")


class ValhallaSettings(QgsSettings):
    def __init__(self):
        super().__init__(
            str(get_settings_dir().joinpath("settings.ini")),
            QSettings.IniFormat,
        )

    def get(self, group: Dialogs, key: Union[str, Enum]):
        """
        Returns the value of a setting.
        """
        self.beginGroup(group.value, QgsSettings.Section.Plugins)

        value = self.value(key.value if isinstance(key, Enum) else key)
        if not value and DEFAULTS.get(key):
            value = DEFAULTS[key]

        self.endGroup()

        return value

    def set(self, group: Dialogs, key: Union[str, Enum], value: Any):
        """
        Set a settings value.
        """
        self.beginGroup(group.value, QgsSettings.Section.Plugins)

        self.setValue(key.value if isinstance(key, Enum) else key, value)

        self.endGroup()

    # don't override super().remove()
    def remove_(self, group: Dialogs, key: Any):
        self.beginGroup(group.value, QgsSettings.Section.Plugins)

        self.remove(key)

        self.endGroup()

    def is_debug(self) -> bool:
        """Lets us know if we're in debug mode"""

        return str_to_bool(self.get(Dialogs.SETTINGS, "debug"))

    def get_providers(
        self,
        router: RouterType,
    ) -> List[ProviderSetting]:
        """Returns all providers"""
        return self.get(Dialogs.PROVIDERS, router.lower()) or list()

    def set_provider(self, router: RouterType, provider: ProviderSetting):
        existing = self.get_providers(router)
        existing.append(provider)
        self.set(Dialogs.PROVIDERS, router.lower(), existing)

    def remove_provider(self, router: RouterType, provider_name: str):
        current = self.get_providers(router)
        new = list(filter(lambda x: x.name != provider_name, current))
        self.set(Dialogs.PROVIDERS, router.lower(), new)

    def pop_providers(self, router: RouterType) -> List[ProviderSetting]:
        current = self.get_providers(router)
        self.remove_(Dialogs.PROVIDERS, router.lower())

        return current

    def get_graph_dir(self) -> Optional[Path]:
        """
        Returns the path to the graph directory from the settings.
        """
        graph_dir = self.get(Dialogs.SETTINGS, "graph_dir")
        return Path(graph_dir) if graph_dir else None

    def set_graph_dir(self, graph_dir: Path | str):
        """
        Sets the path to the graph directory from the settings.
        """
        self.set(
            Dialogs.SETTINGS,
            "graph_dir",
            str(graph_dir.resolve()) if isinstance(graph_dir, Path) else graph_dir,
        )

    def get_binary_dir(self) -> Optional[Path]:
        """
        Returns the path to the Valhalla binaries.
        """
        binary_dir = self.get(Dialogs.SETTINGS, "binary_dir")
        return Path(binary_dir) if binary_dir else None

    def set_binary_dir(self, binary_dir: Path | str):
        """
        Returns the path to the Valhalla binaries.
        """
        self.set(
            Dialogs.SETTINGS,
            "binary_dir",
            str(binary_dir.resolve()) if isinstance(binary_dir, Path) else binary_dir,
        )
