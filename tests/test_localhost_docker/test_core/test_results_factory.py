from qgis.core import QgsWkbTypes

from ... import LocalhostDockerTestCase
from ...utilities import get_qgis_app

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

from qvalhalla.core.results_factory import ResultsFactory
from qvalhalla.global_definitions import (
    RouterEndpoint,
    RouterMethod,
    RouterProfile,
    RouterType,
)


class TestResultsFactory(LocalhostDockerTestCase):
    """Tests basic functionality of ResultsFactory class."""

    def test_geom_type(self):
        self.assertEqual(
            ResultsFactory.geom_type(RouterEndpoint.DIRECTIONS),
            QgsWkbTypes.LineString,
        )
        self.assertEqual(
            ResultsFactory.geom_type(RouterEndpoint.ISOCHRONES),
            QgsWkbTypes.Polygon,
        )
        self.assertEqual(
            ResultsFactory.geom_type(RouterEndpoint.MATRIX),
            QgsWkbTypes.NoGeometry,
        )
        self.assertEqual(
            ResultsFactory.geom_type(RouterEndpoint.EXPANSION),
            QgsWkbTypes.LineString,
        )

    def test_url_input(self):
        """Checks if the url stays constant when provided manually."""
        url = "http://foo.bar"
        factory_with_url = ResultsFactory(
            RouterType.VALHALLA, RouterMethod.REMOTE, RouterProfile.CAR, url=url
        )
        factory_with_url.profile = RouterProfile.BIKE

        self.assertTrue(factory_with_url.url, url)
