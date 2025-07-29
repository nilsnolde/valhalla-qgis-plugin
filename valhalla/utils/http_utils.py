import json

from qgis.core import QgsNetworkAccessManager
from qgis.PyQt.QtCore import QJsonDocument, QUrl
from qgis.PyQt.QtNetwork import QNetworkRequest

from ..utils.resource_utils import get_json_body


def get_status_response(base_url: str, verbose: bool = False) -> dict:
    """
    Returns the response for the /status endpoint, if any.

    :param base_url: the base URL, e.g. https://valhalla1.openstreetmap.de
    :param verbose: if a "verbose" /status request should be issued; note, this is resource intense
    """

    nam = QgsNetworkAccessManager.instance()

    url = QUrl(base_url + "/status")
    req = QNetworkRequest(url)
    req.setHeader(
        QNetworkRequest.ContentTypeHeader,
        "application/json",
    )
    req_method = nam.blockingGet
    req_args = {"request": req}
    if verbose:
        req_method = nam.blockingPost
        body = QJsonDocument.fromJson(json.dumps({"verbose": True}).encode())
        req_args.update({"data": body.toJson()})

    return get_json_body(req_method(**req_args))
