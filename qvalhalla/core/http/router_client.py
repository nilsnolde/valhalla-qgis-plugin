import json

from qgis.core import Qgis, QgsNetworkAccessManager, QgsNetworkReplyContent
from qgis.PyQt.QtCore import QJsonDocument, QUrl
from qgis.PyQt.QtNetwork import QNetworkRequest

from ... import PLUGIN_NAME, __version__
from ...third_party.routingpy.routingpy import exceptions
from ...third_party.routingpy.routingpy.client_base import BaseClient
from ...utils.logger_utils import qgis_log
from ...utils.resource_utils import get_json_body
from ..settings import ValhallaSettings


class RouterClient(BaseClient):
    def __init__(
        self,
        base_url,
        user_agent=f"{PLUGIN_NAME.replace(' ', '_')}/v{__version__}",
        timeout=None,  # need to be included since invoked in routingpy with this signature
        retry_timeout=None,
        retry_over_query_limit=None,
        skip_api_error=False,
    ):

        super(RouterClient, self).__init__(
            base_url, user_agent=user_agent, skip_api_error=skip_api_error
        )
        self.nam = QgsNetworkAccessManager.instance()

    def _request(self, url, get_params={}, post_params=None, dry_run=None):
        authed_url = self._generate_auth_url(url, get_params)
        url_object = QUrl(self.base_url + authed_url)

        is_debug = ValhallaSettings().is_debug()

        requests_method = self.nam.blockingGet
        request = QNetworkRequest(url_object)
        request.setHeader(
            QNetworkRequest.ContentTypeHeader,
            "application/json",
        )

        request_args = {"request": request}
        if post_params:
            requests_method = self.nam.blockingPost
            body = QJsonDocument.fromJson(json.dumps(post_params).encode())
            request_args.update({"data": body.toJson()})
        response: QgsNetworkReplyContent = requests_method(**request_args)

        if is_debug:
            qgis_log(f"URL: {url_object.url()}\nParameters:\n{json.dumps(post_params or {}, indent=2)}")

        if response.rawHeader(b"Content-Type").data().decode() == "image/tiff":
            return bytes(response.content())
        else:
            try:
                result = get_json_body(response)
                return result
            # TODO: handle retriable request similar to the default routingpy client
            except exceptions.RouterApiError:
                if not self.skip_api_error:
                    raise
                elif is_debug:
                    qgis_log(
                        "Router {} returned an API error with "
                        "the following message:\n{}".format(self.__class__.__name__, response.content()),
                        Qgis.Warning,
                    )
                return
