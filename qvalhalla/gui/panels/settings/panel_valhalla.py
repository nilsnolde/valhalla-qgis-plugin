from ....global_definitions import RouterType
from ...ui_definitions import PluginSettingsDlgElems
from .panel_router_base import PanelRouterBase


class PanelValhalla(PanelRouterBase):
    RECOVER = [
        PluginSettingsDlgElems.VALHALLA_HTTP_URL,
        PluginSettingsDlgElems.VALHALLA_HTTP_PARAM,
        PluginSettingsDlgElems.VALHALLA_HTTP_SECRET,
    ]
    ROUTER = RouterType.VALHALLA
