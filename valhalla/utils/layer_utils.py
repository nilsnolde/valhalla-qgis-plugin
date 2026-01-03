import json
from typing import Dict, Optional, Union

from qgis.core import (
    QgsCategorizedSymbolRenderer,
    QgsColorRamp,
    QgsCoordinateReferenceSystem,
    QgsFeature,
    QgsFeatureRequest,
    QgsJsonExporter,
    QgsProcessingFeatureSource,
    QgsRendererCategory,
    QgsSingleSymbolRenderer,
    QgsStyle,
    QgsSymbol,
    QgsVectorLayer,
    QgsWkbTypes,
)

from ..global_definitions import RouterEndpoint
from .resource_utils import get_resource_path

COLOR_RAMP: QgsColorRamp = QgsStyle().defaultStyle().colorRamp("GnBu")

STYLE_FIELDS: Dict[RouterEndpoint, Optional[str]] = {
    RouterEndpoint.DIRECTIONS: "duration",
    RouterEndpoint.ISOCHRONES: "contour",
    RouterEndpoint.MATRIX: None,
    RouterEndpoint.EXPANSION: None,
}


class STYLES:
    COLORS = list(reversed([COLOR_RAMP.color(x * 0.1) for x in range(10)]))
    SINGLE_COLOR = COLOR_RAMP.color(1)
    LINE_WIDTH = 0.6
    POLYGON_OPACITY = 0.7


class Interpolator:
    """Class for mapping two iterables for consistent coloring of
    multiple isochrone/direction result features within one layer."""

    def __init__(self, left_iter, right_iter):
        self.left_min = 0
        self.right_min = 0
        self.left_span = len(left_iter) - 1
        self.right_span = len(right_iter) - 1
        try:
            self.scale_factor = float(self.right_span) / float(self.left_span)
        except ZeroDivisionError:
            self.scale_factor = self.right_span

    def interpolate(self, value):
        return min(
            max(self.right_span, self.left_span),
            int(self.right_min + (value - self.left_min) * self.scale_factor),
        )


def get_wgs_coords_from_feature(feature: QgsFeature, crs: QgsCoordinateReferenceSystem):
    exporter = QgsJsonExporter()
    exporter.setSourceCrs(crs)  # needed for automatic conversion to WGS84
    json_feature = json.loads(exporter.exportFeature(feature))
    return json_feature["geometry"]["coordinates"]


def get_wgs_coords_from_layer(
    layer: Union[QgsVectorLayer, QgsProcessingFeatureSource],
    order_by: Optional[str] = None,
) -> list:
    """
    Turns the input layer's geometries into lists of coordinates for use with Valhalla's
    locations, exclude_locations and exclude_polygons parameters. Handles point and polygon layers of single and multi
    type geometries.

    :param layer: A QgsVectorLayer or QgsProcessingFeatureSource
    :param order_by: A field name to order the layer's features by
    """
    if not layer.featureCount():
        return []

    # outer rings only for polygons
    is_poly = (
        layer.wkbType()
        in (  # yes, this is cumbersome, but QgsFeatureSource is missing .geometryType()
            QgsWkbTypes.Polygon,
            QgsWkbTypes.MultiPolygon,
            QgsWkbTypes.Polygon25D,
            QgsWkbTypes.PolygonM,
            QgsWkbTypes.PolygonZ,
            QgsWkbTypes.PolygonZM,
            QgsWkbTypes.MultiPolygon25D,
            QgsWkbTypes.MultiPolygonM,
            QgsWkbTypes.MultiPolygonZ,
            QgsWkbTypes.MultiPolygonZM,
        )
    )
    is_multi = QgsWkbTypes.isMultiType(layer.wkbType())
    coordinates = []

    exporter = QgsJsonExporter()
    crs = layer.dataProvider().sourceCrs() if isinstance(layer, QgsVectorLayer) else layer.sourceCrs()
    exporter.setSourceCrs(crs)  # needed for automatic conversion to WGS84

    order_by_clause = QgsFeatureRequest()

    if order_by:
        order_by_clause.addOrderBy(order_by)

    for feature in layer.getFeatures(order_by_clause):
        json_feature = json.loads(exporter.exportFeature(feature))
        coords = json_feature["geometry"]["coordinates"]

        if is_multi and is_poly:
            _ = [coordinates.append(coord[0]) for coord in coords]
        elif is_multi and not is_poly:
            _ = [coordinates.append(coord) for coord in coords]
        elif not is_multi and is_poly:
            coordinates.append(coords[0])
        elif not is_multi and not is_poly:
            coordinates.append(coords)

    return coordinates


def post_process_layer(layer: QgsVectorLayer, endpoint: RouterEndpoint) -> None:
    """
    Updates a directions/isochrones result layer's symbology to the predefined style.

    :param layer: the layer to be updated
    :param endpoint: the endpoint which was called
    """
    if endpoint == RouterEndpoint.MATRIX:
        return
    elif endpoint in (RouterEndpoint.DIRECTIONS, RouterEndpoint.TSP):
        layer.loadNamedStyle(str(get_resource_path("styles", "directions.qml")))
        return

    color_field = STYLE_FIELDS[endpoint]

    if color_field:
        field: int = layer.fields().lookupField(color_field)
        unique_values = sorted(layer.uniqueValues(field))

        if layer.wkbType() == QgsWkbTypes.Polygon:
            layer.setOpacity(STYLES.POLYGON_OPACITY)
        if color_field == "contour":
            unique_values = list(reversed(unique_values))

        interpolator = Interpolator(unique_values, STYLES.COLORS)
        categories = []

        for id_, unique_value in enumerate(unique_values):
            symbol = QgsSymbol.defaultSymbol(layer.geometryType())
            color = STYLES.COLORS[interpolator.interpolate(id_)]
            symbol.setColor(color)
            if layer.wkbType() == QgsWkbTypes.LineString:
                symbol.setWidth(STYLES.LINE_WIDTH)
            category = QgsRendererCategory(unique_value, symbol, str(unique_value))
            categories.append(category)

        renderer = QgsCategorizedSymbolRenderer(color_field, categories)
    else:  # some basic styling for Expansion
        symbol = QgsSymbol.defaultSymbol(layer.geometryType())
        symbol.setColor(STYLES.SINGLE_COLOR)
        symbol.setWidth(STYLES.LINE_WIDTH)
        renderer = QgsSingleSymbolRenderer(symbol)
    layer.setRenderer(renderer)
    layer.triggerRepaint()
