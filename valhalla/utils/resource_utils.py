import bz2
import importlib
import json
import platform
import shlex
import shutil
import subprocess
from enum import Enum
from pathlib import Path
from typing import Iterable

from packaging.version import Version
from packaging.version import parse as parse_version
from qgis.core import QgsApplication, QgsNetworkAccessManager, QgsNetworkReplyContent
from qgis.PyQt.QtCore import QUrl
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtNetwork import QNetworkReply, QNetworkRequest

from .. import PLUGIN_NAME, RESOURCE_PATH
from ..exceptions import ValhallaCmdError
from ..global_definitions import PYTHON_EXE, PyPiPkg, PyPiState, RouterType
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


# def normalize_pkgs(
#     server_pkgs: dict, user_pkgs: dict, router: RouterType
# ) -> List[PkgDetails]:
#     """
#     Builds the final package list for each router and adds a "purchased" flag

#     :param server_pkgs: The available list from the server: this will be modified right here!
#     :param user_pkgs: The pkg list the user purchased
#     :param router: The router type
#     """
#     server_pkgs = server_pkgs[router.value]
#     user_pkgs = user_pkgs[router.value]

#     pkg_details: List[PkgDetails] = list()

#     user_pkg_names = [pkg["name"] for pkg in user_pkgs]
#     for pkg in server_pkgs:
#         is_purchased = True if pkg["name"] in user_pkg_names else False
#         pkg_fp = get_local_pkg_path(pkg["filename"], router)
#         local_fp = str(pkg_fp) if pkg_fp.exists() else ""

#         pkg_details.append(
#             PkgDetails(**pkg, is_purchased=is_purchased, local_fp=local_fp)
#         )

#     return pkg_details


def get_local_pkg_path(filename: str, router: RouterType) -> Path:
    """
    Get the full path to the local package. Also create the router
    directory if it doesn't exist yet.

    :param filename: The package's filename as .bz2
    :param router: the router type
    :return: the absolute path of the local package
    """
    router_dir = get_settings_dir().joinpath(router.value)
    router_dir.mkdir(exist_ok=True, parents=True)

    filename = filename[:-4] if filename.endswith(".bz2") else filename

    return router_dir.joinpath(filename).resolve()


def decompress_pkg(fp: Path):
    """
    Decompresses the BZ2 compressed file to the same directory.

    :param fp: the filepath with .bz2 extension
    """
    uncompressed_fp = fp.parent.joinpath(fp.stem)
    with bz2.BZ2File(fp) as fr, open(uncompressed_fp, "wb") as fw:
        shutil.copyfileobj(fr, fw)

    fp.unlink()


def check_local_lib_version(pypi_pkg: PyPiPkg, available_version: Version) -> PyPiState:
    """
    Checks the currently installed version of a package (if any).

    :param pypi_pkg: the package object to check
    :param available_version: the version we expect
    :returns: the package's installed state
    """
    try:
        spec = importlib.util.find_spec(pypi_pkg.import_name)
        if not spec:
            return PyPiState.NOT_INSTALLED
        current_version = importlib.metadata.version(pypi_pkg.pypi_name)
        if parse_version(current_version) < available_version:
            return PyPiState.UPGRADEABLE
    except importlib.metadata.PackageNotFoundError:
        return PyPiState.NOT_INSTALLED

    return PyPiState.UP_TO_DATE


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


def install_pypi(pkgs: Iterable[str]):
    """
    Installs/upgrade packages from PyPI.

    :param python_exe: the full path to the python executable
    :param pkgs: the list of PyPI packages to be installed/upgraded.
    :raises ValhallaCmdError: when exit code other than 0
    """
    use_shell = False
    if platform.system() == "Windows":
        c = f'"{PYTHON_EXE}"'
        use_shell = True
    else:
        c = f"{PYTHON_EXE}"
    c += f" -m pip install --break-system-packages {' '.join(pkgs)}"
    exec_cmd(c, use_shell)
    importlib.invalidate_caches()


def exec_cmd(cmd: str, shell: bool) -> subprocess.CompletedProcess:
    """
    Executes a command and returns the Process.

    :param cmd: the full command to be executed
    :param shell: whether to execute the command through the shell
    :raises ValhallaCmdError: when exit code is other than 0
    """
    try:
        return subprocess.run(shlex.split(cmd), check=True, capture_output=True, shell=shell)
    except subprocess.CalledProcessError as e:
        raise ValhallaCmdError(e.stderr.decode("utf-8").splitlines())


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


def get_settings_dir() -> Path:
    """
    Returns the permanent directory for this plugin and creates the graph
    directories if not already done.

    :returns: the permanent directory for this plugin.
    """
    d = (
        Path(QgsApplication.qgisSettingsDirPath())
        .joinpath(PLUGIN_NAME.replace(" ", "_").lower())
        .resolve()
    )
    for e in RouterType:
        dd = d.joinpath(e.lower())
        dd.mkdir(exist_ok=True, parents=True)

    return d


def get_graph_dir(provider: RouterType):
    """
    Returns the path to the graph directory of the passed provider
    """
    return Path(get_settings_dir().joinpath(provider.lower()))
