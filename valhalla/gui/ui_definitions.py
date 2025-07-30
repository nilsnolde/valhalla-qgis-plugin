from enum import Enum, unique


@unique
class PluginSettingsDlgElems(str, Enum):
    # we append the user-defined name to these
    VALHALLA_HTTP_URL = "ui_valhalla_http_url"
    VALHALLA_HTTP_PARAM = "ui_valhalla_http_param"
    VALHALLA_HTTP_SECRET = "ui_valhalla_http_secret"
    # OSRM_HTTP_URL_PED = "ui_osrm_http_url_ped"
    # OSRM_HTTP_URL_BIKE = "ui_osrm_http_url_bike"
    # OSRM_HTTP_URL_CAR = "ui_osrm_http_url_car"
    # OSRM_HTTP_PARAM = "ui_osrm_http_param"
    # OSRM_HTTP_SECRET = "ui_osrm_http_secret"
    # SHOP_HTTP_URL = "ui_shop_http_url"
    # ACCOUNT_AUTH = "ui_account_auth"
    DEBUG = "debug"


@unique
class RouterWidgetElems(str, Enum):
    PROV_COMBO = "ui_cmb_prov"
    PROV_OPT = "ui_btn_prov_options"
    PED = "ui_btn_ped"
    BIKE = "ui_btn_bike"
    CAR = "ui_btn_car"
    TRUCK = "ui_btn_truck"
    MBIKE = "ui_btn_mbike"
