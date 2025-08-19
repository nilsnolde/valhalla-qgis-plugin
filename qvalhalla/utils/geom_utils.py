from typing import List

from qgis.core import (
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
    QgsPointXY,
    QgsProject,
)

from ..third_party.routingpy.routingpy.utils import decode_polyline5

WGS84 = QgsCoordinateReferenceSystem.fromEpsgId(4326)


def point_to_wgs84(
    point: QgsPointXY,
    own_crs: QgsCoordinateReferenceSystem,
    direction: int = QgsCoordinateTransform.ForwardTransform,
) -> QgsPointXY:
    """
    Transforms the ``point`` to (``direction=ForwardTransform``) or from
    (``direction=ReverseTransform``) WGS84.
    """
    project = QgsProject.instance()
    out_point = point
    if own_crs != WGS84:
        xform = QgsCoordinateTransform(own_crs, WGS84, project)
        point_transform = xform.transform(point, direction)
        out_point = point_transform

    return out_point


def decode_polyline(encoded: str) -> List[QgsPointXY]:
    # TODO: change the order to lnglat: the uploader used the wrong order when encoding
    return [QgsPointXY(x, y) for x, y in decode_polyline5(encoded, order="latlng")]
