from qgis.core import QgsNetworkReplyContent
from qgis.PyQt.QtNetwork import QNetworkReply, QNetworkRequest

from valhalla.third_party.routingpy.routingpy import exceptions
from valhalla.utils.resource_utils import (
    check_valhalla_installation,
    create_valhalla_config,
    get_json_body,
    get_valhalla_config_path,
)

from ... import LocalhostDockerTestCase


class FakeReply(QNetworkReply):
    def __init__(self, status_code=200, error=QNetworkReply.NoError):
        super().__init__()
        self.setAttribute(QNetworkRequest.HttpStatusCodeAttribute, status_code)
        if error != QNetworkReply.NoError:
            self.setError(error, "")

    def abort(self):
        pass

    def readData(self, maxlength):
        pass


class TestResourceUtils(LocalhostDockerTestCase):
    def test_get_json_body(self):
        # timeout error
        res = QgsNetworkReplyContent(FakeReply(error=QNetworkReply.TimeoutError))
        with self.assertRaises(exceptions.Timeout):
            get_json_body(res)

        res = QgsNetworkReplyContent(FakeReply(status_code=None))
        with self.assertRaises(exceptions.RouterError):
            get_json_body(res)

        res = QgsNetworkReplyContent(FakeReply())
        res.setContent(b"bla")
        with self.assertRaises(exceptions.JSONParseError):
            get_json_body(res)

        res = QgsNetworkReplyContent(FakeReply(status_code=429))
        res.setContent(b"{}")
        with self.assertRaises(exceptions.OverQueryLimit):
            get_json_body(res)

        res = QgsNetworkReplyContent(FakeReply(status_code=499))
        res.setContent(b"{}")
        with self.assertRaises(exceptions.RouterApiError):
            get_json_body(res)

        res = QgsNetworkReplyContent(FakeReply(status_code=502))
        res.setContent(b"{}")
        with self.assertRaises(exceptions.RouterServerError):
            get_json_body(res)

        res = QgsNetworkReplyContent(FakeReply(status_code=399))
        res.setContent(b"{}")
        with self.assertRaises(exceptions.RouterError):
            get_json_body(res)

    def test_create_valhalla_config_failure(self):
        # first remove any existing config
        conf = get_valhalla_config_path()
        if conf.exists():
            conf.unlink()

        # then we shouldn't create one without the bindings
        with self.assertRaises(ModuleNotFoundError):
            create_valhalla_config(False)
        self.assertFalse(get_valhalla_config_path().exists())

        with self.assertRaises(ModuleNotFoundError):
            create_valhalla_config(True)
        self.assertFalse(get_valhalla_config_path().exists())

    def test_check_valhalla_installation_failure(self):
        self.assertFalse(check_valhalla_installation())
