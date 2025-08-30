import socket
import unittest
from pathlib import Path
from shutil import copy, move
from urllib.parse import urlparse

from tests.utilities import get_qgis_app

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

from qvalhalla.core.settings import ValhallaSettings
from qvalhalla.utils.resource_utils import get_settings_dir

URL = "http://localhost:8002"

TEST_DIR = Path(__file__).parent.resolve()

SETTINGS_PATH = get_settings_dir().joinpath("settings.ini")
TEMP_SETTINGS_PATH = get_settings_dir().joinpath("settings_temp.ini")


def is_localhost_runing() -> bool:
    parsed_url = urlparse(URL)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
            sock.connect((parsed_url.hostname, parsed_url.port))
        except Exception:
            return False

        return True


def is_pyvalhalla_installed() -> bool:
    is_installed = False
    try:
        import valhalla  # noqa: F401

        is_installed = True
    except ModuleNotFoundError:
        pass

    return is_installed


class LocalhostDockerTestCase(unittest.TestCase):
    """
    Expects localhost via Docker, i.e. localhost not run via plugin.

    This is the standard for most tests which are not testing the local service setup.
    """

    @classmethod
    def setUpClass(cls) -> None:
        if not is_localhost_runing():
            raise ConnectionRefusedError(
                f"An external Valhalla service needs to be running on {URL} for {cls.__name__} to work"
            )
        if is_pyvalhalla_installed():
            raise ImportError(f"pyvalhalla-weekly can'be be installed for {cls.__name__} to work")

        if SETTINGS_PATH.exists():
            copy(SETTINGS_PATH, TEMP_SETTINGS_PATH)

        return super().setUpClass()

    @classmethod
    def tearDownClass(cls) -> None:
        if TEMP_SETTINGS_PATH.exists():
            move(TEMP_SETTINGS_PATH, SETTINGS_PATH)

        return super().tearDownClass()


class LocalhostPluginTestCase(unittest.TestCase):
    """
    Expects localhost to be run via the plugin.

    This is only used to test the local service setup in the main UI.
    """

    @classmethod
    def setUpClass(cls) -> None:
        if is_localhost_runing():
            raise ConnectionError(
                f"An external Valhalla service can't be running on {URL} for {cls.__name__} to work"
            )
        if not is_pyvalhalla_installed():
            raise ImportError(f"pyvalhalla-weekly needs to be installed for {cls.__name__} to work")

        if SETTINGS_PATH.exists():
            copy(SETTINGS_PATH, TEMP_SETTINGS_PATH)

        import valhalla

        ValhallaSettings().set_binary_dir(Path(valhalla.__file__).parent.joinpath("bin"))

        return super().setUpClass()

    @classmethod
    def tearDownClass(cls) -> None:
        if TEMP_SETTINGS_PATH.exists():
            move(TEMP_SETTINGS_PATH, SETTINGS_PATH)

        return super().tearDownClass()


# not used yet

# class NoLocalhostTestCase(unittest.TestCase):
#     """
#     Expects no localhost to be run.

#     This is only used to test the local service setup in the main UI.
#     """

#     @classmethod
#     def setUpClass(cls) -> None:
#         # no localhost via Docker or otherwise
#         if is_localhost_runing():
#             raise ConnectionError(f"An external Valhalla service can't be running on {URL} for {cls.__name__} to work")
#         if is_pyvalhalla_installed():
#             raise ImportError(f"pyvalhalla-weekly can'be be installed for {cls.__name__} to work")

#         if SETTINGS_PATH.exists():
#             copy(SETTINGS_PATH, TEMP_SETTINGS_PATH)

#         return super().setUpClass()

#     @classmethod
#     def tearDownClass(cls) -> None:
#         if TEMP_SETTINGS_PATH.exists():
#             move(TEMP_SETTINGS_PATH, SETTINGS_PATH)

#         return super().tearDownClass()
