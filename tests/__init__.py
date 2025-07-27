import socket
import unittest
from pathlib import Path
from urllib.parse import urlparse

from tests.utilities import get_qgis_app

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

from valhalla.core.settings import ValhallaSettings
from valhalla.global_definitions import Dialogs, RouterType
from valhalla.gui.ui_definitions import PluginSettingsDlgElems

URLS = (
    (PluginSettingsDlgElems.VALHALLA_HTTP_URL, "http://localhost:8002"),
    # (PluginSettingsDlgElems.OSRM_HTTP_URL_CAR, "http://localhost:5000"),
    # (PluginSettingsDlgElems.OSRM_HTTP_URL_BIKE, "http://localhost:5000"),
    # (PluginSettingsDlgElems.OSRM_HTTP_URL_PED, "http://localhost:5000"),
)

TEST_DIR = Path(__file__).parent.resolve()


class HTTPTestCase(unittest.TestCase):
    """
    Sets the routers to localhost in setupClass and to previous value in tearDownClass
    """

    @classmethod
    def setUpClass(cls) -> None:
        # check if the docker containers are running
        cls.url_settings = dict()
        for setting, url in URLS:
            parsed_url = urlparse(url)
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                result = sock.connect_ex((parsed_url.hostname, parsed_url.port))
            if result:
                router = RouterType.VALHALLA if "valhalla" in setting.lower() else RouterType.OSRM
                raise ConnectionRefusedError(f"Router {router} can't connect on {url}")

        for setting, url in URLS:
            cls.url_settings[setting] = ValhallaSettings().get(Dialogs.SETTINGS, setting)
            ValhallaSettings().set(Dialogs.SETTINGS, setting, url)

    @classmethod
    def tearDownClass(cls) -> None:
        for setting, url in URLS:
            ValhallaSettings().set(Dialogs.SETTINGS, setting, cls.url_settings[setting])
