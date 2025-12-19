import importlib.util
import json
import os
import platform
import shlex
import stat
import subprocess
import zipfile
from enum import Enum
from pathlib import Path
from shutil import rmtree
from tempfile import TemporaryDirectory
from typing import Optional

from packaging.version import Version
from packaging.version import parse as parse_version
from qgis.core import QgsNetworkAccessManager, QgsNetworkReplyContent
from qgis.PyQt.QtCore import QUrl
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtNetwork import QNetworkReply, QNetworkRequest

from .. import RESOURCE_PATH
from ..core.settings import ValhallaSettings, get_settings_dir
from ..exceptions import ValhallaCmdError
from ..global_definitions import PYTHON_EXE, PyPiPkg, PyPiState
from ..third_party.routingpy.routingpy import exceptions

PYPI_URL = "https://pypi.org/pypi/{pkg_name}/json"


class ResGroups(Enum):
    ICONS = "icons"
    UI = "ui"


def get_icon(filename: str) -> QIcon:
    """Returns a QIcon either from the theme or from resources"""
    return (
        QIcon(str(get_resource_path(ResGroups.ICONS.value, filename)))
        if not filename.startswith(":")
        else QIcon.fromTheme(filename)
    )


def get_resource_path(*args) -> Path:
    """All args are interpreted as string"""
    return RESOURCE_PATH.joinpath(*args)


def check_local_lib_version(available_version: Version) -> PyPiState:
    """
    Checks the currently installed version of the router binaries (if any).

    :param available_version: the version we expect (i.e. the current pypi version usually)
    :returns: the package's installed state
    """

    local_version = get_local_lib_version()
    if local_version is None:
        return PyPiState.NOT_INSTALLED
    if parse_version(local_version) < available_version:
        return PyPiState.UPGRADEABLE

    return PyPiState.UP_TO_DATE


def get_local_lib_version() -> Optional[str]:
    if not check_valhalla_installation():
        return None

    try:
        exe_path = ValhallaSettings().get_binary_dir().joinpath("valhalla_service")
        proc: subprocess.CompletedProcess = exec_cmd(f"{exe_path.absolute()} --version")
    except (ValhallaCmdError, subprocess.CalledProcessError):
        return None

    stdout = proc.stdout.split()
    if not len(stdout):
        return None

    # currently valhalla_service -v prints also the program name
    # see https://github.com/valhalla/valhalla/pull/5769/
    return stdout[1] if len(stdout) == 2 else stdout[0]


def get_pypi_lib_version(pypi_pkg: PyPiPkg) -> Version:
    nam = QgsNetworkAccessManager.instance()
    url = QUrl(PYPI_URL.format(pkg_name=pypi_pkg.pypi_name))
    req = QNetworkRequest(url)
    req.setHeader(
        QNetworkRequest.ContentTypeHeader,
        "application/json",
    )

    res: QgsNetworkReplyContent = nam.blockingGet(req)
    try:
        v = get_json_body(res)["info"]["version"]
    except exceptions.RouterError:
        v = "0.0.0"

    return Version(v)


def install_pyvalhalla(installed_state: PyPiState):
    """
    Installs/upgrade packages from PyPI.

    :param installed_state: decides if we want to do nothing, upgrade or install
    :raises ValhallaCmdError: when exit code other than 0
    """
    if installed_state == PyPiState.UP_TO_DATE:
        return

    bin_dir = get_default_valhalla_binary_dir()
    pyvalhalla_dir = bin_dir.parent.parent

    if installed_state == PyPiState.UPGRADEABLE:
        rmtree(pyvalhalla_dir)
        pyvalhalla_dir.mkdir(parents=True, exist_ok=False)

    # if we got here, we'll download the latest
    with TemporaryDirectory() as temp_dir:
        # download wheel to temp dir
        try:
            exec_cmd(f"{PYTHON_EXE} -m pip download --only-binary=:all: --dest {temp_dir} pyvalhalla")
        except subprocess.CalledProcessError as e:
            raise ValhallaCmdError(f"Couldnt install pyvalhalla: {e.stderr}")

        # unzip it to final dir
        wheel_path = Path(temp_dir, os.listdir(temp_dir)[0])
        with zipfile.ZipFile(wheel_path, "r") as zip:
            zip.extractall(pyvalhalla_dir)

        # set the execution bits
        for exe_path in bin_dir.iterdir():
            st = os.stat(exe_path)
            os.chmod(exe_path, st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def exec_cmd(cmd: str) -> subprocess.CompletedProcess:
    """
    Executes a command and returns the Process. stdout/stderr are strings.

    :param cmd: the full command to be executed
    :returns: the completed (success or failure) process instance
    """
    cmd_split = shlex.split(cmd)
    shell = False
    if platform.system() == "Windows":
        shell = True
        cmd_split[0] = f'"{cmd_split[0]}"'  # needs to be quoted, absolute path can contain spaces

    return subprocess.run(cmd_split, text=True, check=True, capture_output=True, shell=shell)


def get_json_body(response: QgsNetworkReplyContent) -> dict:
    """
    Parse the response and return the JSON body.

    :param response: The full response
    :raises routingpy.exceptions.Timeout: On server timeout
    :raises routingpy.exceptions.RouterError: If there's no HTTP status code
    :raises routingpy.exceptions.JSONParseError: If it's not a JSON response
    :raises routingpy.exceptions.OverQueryLimit: On 429 HTTP error
    :raises routingpy.exceptions.RouterApiError: On 400 - 499 HTTP error
    :raises routingpy.exceptions.RouterServerError: On > 500 HTTP error
    """

    error_code = response.error()

    if error_code == QNetworkReply.TimeoutError:
        raise exceptions.Timeout("Request timed out.")

    status_code = response.attribute(QNetworkRequest.HttpStatusCodeAttribute)
    if status_code is None:
        msg = f"{response.errorString()} for URL {response.request().url().toString()}"
        raise exceptions.RouterError(response.error(), msg)

    try:
        body = json.loads(bytes(response.content()) or "{}")
    except json.decoder.JSONDecodeError:
        raise exceptions.JSONParseError("Can't decode JSON response:{}".format(response.content()))

    if status_code == 429:
        raise exceptions.OverQueryLimit(status_code, body)
    elif 400 <= status_code < 500:
        raise exceptions.RouterApiError(status_code, body)
    elif 500 <= status_code:
        raise exceptions.RouterServerError(status_code, body)

    if status_code != 200:
        raise exceptions.RouterError(status_code, body)

    return body


def get_valhalla_config_path():
    return get_settings_dir().joinpath("valhalla.json")


def create_valhalla_config(force=False):
    config_path = get_valhalla_config_path()
    if config_path.exists() and not force:
        return

    # load the config builder from
    module_path = ValhallaSettings().get_binary_dir().parent.joinpath("valhalla_build_config.py")
    # try to find it in the binary dir directly (e.g. on unix source builds), else raise
    if not module_path.exists():
        module_path = ValhallaSettings().get_binary_dir().joinpath("valhalla_build_config.py")
        if not module_path.exists():
            raise ModuleNotFoundError("Can't find valhalla_build_config.py (provided by pyvalhalla)")

    spec = importlib.util.spec_from_file_location("valhalla_build_config", module_path)
    valhalla_build_config = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(valhalla_build_config)

    def _sanitize_config(dict_: dict = None) -> dict:
        """remove the "Optional" values from the config."""
        int_dict_ = dict_.copy()
        for k, v in int_dict_.items():
            if isinstance(v, valhalla_build_config.Optional):
                del dict_[k]
            elif isinstance(v, dict):
                _sanitize_config(v)

        return dict_

    # need to remove the items we store in each graph folder's 'id.json'
    config = _sanitize_config(valhalla_build_config.config)

    del config["mjolnir"]["tile_dir"]
    del config["mjolnir"]["tile_extract"]
    try:
        del config["mjolnir"]["tile_url"]
        del config["mjolnir"]["tile_url_user_pw"]
        del config["loki"]["use_connectivity"]
    except KeyError:
        pass

    # allow verbose status for bbox
    config["service_limits"]["status"]["allow_verbose"] = True

    with config_path.open("w") as f:
        json.dump(config, f, indent=2)


def check_valhalla_installation() -> bool:
    current_bin_dir = ValhallaSettings().get_binary_dir()

    if current_bin_dir is None:
        return False
    elif not current_bin_dir.exists():
        return False
    elif (
        valhalla_exe := current_bin_dir.joinpath(
            ("valhalla_service" if os.name != "nt" else "valhalla_service.exe")
        )
    ).exists():
        if not valhalla_exe.is_file():
            return False

        if os.name == "nt":
            pathext = os.environ.get("PATHEXT", "")
            return valhalla_exe.suffix.lower() in (ext.lower() for ext in pathext.split(";"))
        else:
            return os.access(valhalla_exe, os.X_OK)

    return False


def get_default_valhalla_binary_dir() -> Path:
    return get_settings_dir().joinpath("pyvalhalla", "valhalla", "bin")
