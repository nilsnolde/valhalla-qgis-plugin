from dataclasses import dataclass
from enum import Enum
from typing import Any, List, Union

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

    def get_shop_url(self) -> str:
        """Simply returns the shop's base URL from the settings"""
        return self.get(Dialogs.SETTINGS, PluginSettingsDlgElems.SHOP_HTTP_URL)

    # def get_router_url(self, router: RouterType, profile: Optional[RouterProfile] = None) -> str:
    #     """Returns the router's URL."""
    #     t = (
    #         PROFILE_TO_OSRM_URL[profile]
    #         if router == RouterType.OSRM
    #         else PluginSettingsDlgElems.VALHALLA_HTTP_URL
    #     )
    #     return self.get(Dialogs.SETTINGS, t)

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
