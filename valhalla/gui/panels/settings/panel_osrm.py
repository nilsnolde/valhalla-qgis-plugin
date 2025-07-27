from ....global_definitions import RouterType
from .panel_router_base import PanelRouterBase


class PanelOsrm(PanelRouterBase):
    RECOVER = [
        # PluginSettingsDlgElems.OSRM_HTTP_URL_PED,
        # PluginSettingsDlgElems.OSRM_HTTP_URL_BIKE,
        # PluginSettingsDlgElems.OSRM_HTTP_URL_CAR,
        # PluginSettingsDlgElems.OSRM_HTTP_SECRET,
    ]
    ROUTER = RouterType.OSRM
