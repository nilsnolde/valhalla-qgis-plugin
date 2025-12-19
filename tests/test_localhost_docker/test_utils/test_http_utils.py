from valhalla.utils.http_utils import get_status_response

from ... import URL, LocalhostDockerTestCase


class TestHTTPUtils(LocalhostDockerTestCase):
    def test_verbose_status_success(self):
        res = get_status_response(URL, True)
        self.assertIsNotNone(res.get("bbox"))
        self.assertIsNotNone(res.get("version"))
