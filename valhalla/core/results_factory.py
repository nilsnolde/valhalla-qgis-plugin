import json
from typing import Iterator, List, Optional, Tuple, Union

from qgis.core import (
    QgsFeature,
    QgsFields,
    QgsGeometry,
    QgsJsonUtils,
    QgsLineString,
    QgsPoint,
    QgsPolygon,
    QgsWkbTypes,
)

from .. import global_definitions as gd
from ..global_definitions import DEFAULT_LAYER_FIELDS, FieldNames, RouterProfile
from ..third_party.routingpy.routingpy.direction import Direction
from ..third_party.routingpy.routingpy.expansion import Expansions
from ..third_party.routingpy.routingpy.isochrone import Isochrone, Isochrones
from ..third_party.routingpy.routingpy.matrix import Matrix
from ..third_party.routingpy.routingpy.optimized import OptimizedDirection
from .router_factory import RouterFactory


class ResultsFactory:
    def __init__(
        self,
        provider: gd.RouterType,
        method: gd.RouterMethod,
        profile: gd.RouterProfile,
        url: Optional[str] = None,
        pkg_path: str = "",
    ) -> None:
        """
        The factory class that passes requests to the RouterFactory and processes the resulting outputs.

        :param provider: One of RouterType
        :param method: One of RouterMethod
        :param profile: One of RouterProfile
        :param url:  If provided, takes precedence over the URL retrieved from the plugin settings.
        """
        self.provider = provider
        self.method = method
        self._profile = profile
        self.url = url
        self.router = RouterFactory(provider, method, profile, url, pkg_path)

    @property
    def profile(self) -> RouterProfile:
        return self._profile

    @profile.setter
    def profile(self, profile: RouterProfile):
        """Sets its own profile property as well as that of the router factory instance."""
        self._profile = profile
        self.router.profile = profile

    @staticmethod
    def geom_type(endpoint: gd.RouterEndpoint) -> QgsWkbTypes.Type:
        """
        Returns the current results' QGIS geom type enum.
        """
        if endpoint in (
            gd.RouterEndpoint.DIRECTIONS,
            gd.RouterEndpoint.EXPANSION,
            gd.RouterEndpoint.TSP,
        ):
            return QgsWkbTypes.LineString
        elif endpoint == gd.RouterEndpoint.ISOCHRONES:
            return QgsWkbTypes.Polygon
        elif endpoint == gd.RouterEndpoint.MATRIX:
            return QgsWkbTypes.NoGeometry

    # flake8: noqa: C901
    def get_results(
        self,
        endpoint: gd.RouterEndpoint,
        locations: List[Tuple[float, float]],
        params: dict,
        fields: Optional[QgsFields] = None,
    ) -> Iterator[QgsFeature] | Iterator[bytes]:
        """
        The main method to retrieve routing results that returns a feature iterator.

        :endpoint: one of RouterEndpoint
        :profile: one of RouterProfile
        :locations: locations as iterable of lng/lat coordinate tuples
        :params: additional parameter dictionary
        """
        if not fields:
            fields = QgsFields()
            for field in DEFAULT_LAYER_FIELDS[endpoint]:
                fields.append(field)

        if endpoint == gd.RouterEndpoint.DIRECTIONS:
            result = self.router.request(endpoint, locations, **params)
            yield next(self._process_direction_result(result, params, fields))  # is always one feature

        elif endpoint == gd.RouterEndpoint.ISOCHRONES:
            for loc in locations:
                result = self.router.request(endpoint, loc, **params)
                for feat in self._process_isochrone_result(result, params, fields):
                    yield feat

        elif endpoint == gd.RouterEndpoint.RASTER:
            for loc in locations:
                yield self.router.request(endpoint, loc, **params).image

        elif endpoint == gd.RouterEndpoint.MATRIX:
            result = self.router.request(endpoint, locations, **params)
            for feat in self._process_matrix_result(result, params, fields):
                yield feat

        elif endpoint == gd.RouterEndpoint.EXPANSION:
            for loc in locations:
                result = self.router.request(endpoint, loc, **params)
                for feat in self._process_expansion_result(result, params, fields):
                    yield feat

        elif endpoint == gd.RouterEndpoint.TSP:
            result = self.router.request(endpoint, locations, **params)
            yield next(self._process_direction_result(result, params, fields))

    def _process_direction_result(
        self, direction: Union[Direction | OptimizedDirection], params: dict, fields: QgsFields
    ):
        feature = QgsFeature()
        line = QgsLineString([QgsPoint(*coords) for coords in direction.geometry])
        feature.setGeometry(QgsGeometry(line))

        feature.setFields(fields)
        feature[FieldNames.PROVIDER] = self.provider.lower()
        feature[FieldNames.PROFILE] = self.profile.lower()
        feature[FieldNames.DURATION] = direction.duration
        feature[FieldNames.DISTANCE] = direction.distance
        feature[FieldNames.OPTIONS] = json.dumps(params)

        yield feature

    def _process_isochrone_result(self, isochrones: Isochrones, params: dict, fields: QgsFields):
        isochrone: Isochrone
        for isochrone in reversed(isochrones):
            if not len(isochrone.geometry):
                continue
            feat = QgsFeature()
            geom = QgsPolygon(QgsLineString([QgsPoint(*coords) for coords in isochrone.geometry[0]]))
            feat.setGeometry(QgsGeometry(geom))

            feat.setFields(fields)
            feat[FieldNames.PROVIDER] = self.provider.lower()
            feat[FieldNames.PROFILE] = self.profile.lower()
            feat[FieldNames.METRIC] = isochrone.interval_type
            feat[FieldNames.CONTOUR] = isochrone.interval
            feat[FieldNames.OPTIONS] = json.dumps(params)

            yield feat

    def _process_matrix_result(self, matrix: Matrix, params: dict, fields: QgsFields):
        for origin_idx in range(len(matrix.durations)):
            for dest_idx in range(len(matrix.durations[0])):
                time = matrix.durations[origin_idx][dest_idx]
                distance = matrix.distances[origin_idx][dest_idx]

                feat = QgsFeature()
                feat.setFields(fields)
                feat[FieldNames.PROVIDER] = self.provider.lower()
                feat[FieldNames.PROFILE] = self.profile.lower()
                feat[FieldNames.SOURCE] = origin_idx
                feat[FieldNames.TARGET] = dest_idx
                feat[FieldNames.DISTANCE] = distance
                feat[FieldNames.DURATION] = time
                feat[FieldNames.OPTIONS] = json.dumps(params)

                yield feat

    def _process_expansion_result(self, expansion: Expansions, params: dict, fields: QgsFields):
        for idx, gj_feat in enumerate(expansion.raw["features"]):
            feat = QgsFeature()
            feat.setFields(fields)
            geom = QgsLineString([QgsPoint(*coords) for coords in gj_feat["geometry"]["coordinates"]])
            feat.setGeometry(QgsGeometry(geom))
            feat[FieldNames.PROVIDER] = self.provider.lower()
            feat[FieldNames.PROFILE] = self.profile.lower()
            feat[FieldNames.METRIC] = expansion.interval_type
            feat[FieldNames.DURATION] = gj_feat["properties"]["duration"]
            feat[FieldNames.DISTANCE] = gj_feat["properties"]["distance"]
            feat[FieldNames.OPTIONS] = json.dumps(params)

            yield feat
