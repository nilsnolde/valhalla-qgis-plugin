import unittest

from qgis.core import QgsCoordinateReferenceSystem, QgsCoordinateTransform, QgsPointXY
from qvalhalla.utils.geom_utils import point_to_wgs84

from ...constants import WAYPOINTS_3857, WAYPOINTS_4326


class TestGeomUtils(unittest.TestCase):
    def test_point_to_wgs84_forward(self):
        crs = QgsCoordinateReferenceSystem.fromEpsgId(3857)
        exp = WAYPOINTS_4326
        for idx, pt in enumerate(WAYPOINTS_3857):
            proj_pt = point_to_wgs84(QgsPointXY(*pt), crs)
            self.assertAlmostEqual(proj_pt.x(), exp[idx][0], 5)
            self.assertAlmostEqual(proj_pt.y(), exp[idx][1], 5)

    def test_point_to_wgs84_backward(self):
        crs = QgsCoordinateReferenceSystem.fromEpsgId(3857)
        exp = WAYPOINTS_3857
        for idx, pt in enumerate(WAYPOINTS_4326):
            proj_pt = point_to_wgs84(QgsPointXY(*pt), crs, QgsCoordinateTransform.ReverseTransform)
            self.assertEqual(round(proj_pt.x(), 1), exp[idx][0])
            self.assertEqual(round(proj_pt.y(), 1), exp[idx][1])
