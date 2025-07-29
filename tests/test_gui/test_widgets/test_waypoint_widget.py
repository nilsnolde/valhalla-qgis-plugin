import json
from tempfile import NamedTemporaryFile
from time import sleep
from urllib.parse import unquote, urlencode

from qgis.core import (
    QgsAnnotationLayer,
    QgsCoordinateReferenceSystem,
    QgsFeature,
    QgsLayerTreeNode,
    QgsPoint,
    QgsPointXY,
    QgsProject,
    QgsRectangle,
    QgsVectorLayer,
)
from qgis.gui import QgsMapCanvas, QgsMapMouseEvent
from qgis.PyQt.QtCore import QEvent, QPoint, Qt, QTimer
from qgis.PyQt.QtTest import QTest
from qgis.PyQt.QtWidgets import QApplication, QDialogButtonBox

from ... import HTTPTestCase
from ...constants import WAYPOINTS_3857, WAYPOINTS_4326
from ...utilities import assertQueryStringEqual, get_qgis_app

CANVAS: QgsMapCanvas
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

from valhalla.global_definitions import RouterType
from valhalla.gui.dlg_from_json import FromValhallaJsonDialog
from valhalla.gui.dlg_from_lyr import FromLayerDialog
from valhalla.gui.dlg_from_osrm_url import FromOsrmUrlDialog
from valhalla.gui.dock_routing import RoutingDockWidget


class TestWaypointsWidget(HTTPTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        # Berlin
        CANVAS.setExtent(QgsRectangle(1478686, 6885333, 1500732, 6903232))
        CANVAS.setDestinationCrs(QgsCoordinateReferenceSystem.fromEpsgId(3857))

        cls.dlg = RoutingDockWidget(IFACE)

    def tearDown(self) -> None:
        self.dlg.waypoints_widget._handle_clear_locations()
        QgsProject.instance().removeAllMapLayers()

    def add_waypoints(self, points):
        """adds waypoints to the table"""
        # click the add button which should hide the dialog
        QTest.mouseClick(self.dlg.waypoints_widget.ui_btn_add_pt, Qt.LeftButton)
        self.assertTrue(self.dlg.isVisible())
        sleep(0.2)

        # add 3 points in Berlin
        for pt in points:
            self.dlg.waypoints_widget.point_tool.canvasClicked.emit(QgsPointXY(*pt), Qt.LeftButton)
            sleep(0.1)

        # finish collecting points with double click
        double_click = QgsMapMouseEvent(
            CANVAS,
            QEvent.MouseButtonDblClick,
            QPoint(0, 0),  # Relative to the canvas' dimensions
            Qt.LeftButton,
        )
        self.dlg.waypoints_widget.point_tool.canvasDoubleClickEvent(double_click)
        self.assertTrue(self.dlg.isVisible())

    def test_get_valhalla_locations(self):
        table = self.dlg.waypoints_widget.ui_table
        self.dlg.setVisible(True)

        radiuses = [0, 100, 1000]
        extra_params = [
            {
                "preferred_side": "same",
                "rank_candidates": True,
                "heading": 120,
                "display_lat": 5.32,
            },
            {
                "preferred_side": "opposite",
                "rank_candidates": False,
                "heading": 10,
                "display_lat": 3.51,
            },
            {
                "preferred_side": "whatever",
                "rank_candidates": True,
                "heading": 12,
                "display_lat": 3.12,
            },
        ]

        # add the points to the table
        for row_id, pt in enumerate(WAYPOINTS_4326):
            table.insertRow(row_id)
            self.dlg.waypoints_widget._add_row_to_table(
                row_id,
                pt[1],
                pt[0],
                radiuses[row_id],
                unquote(urlencode(extra_params[row_id])),
            )

        for idx, loc in enumerate(self.dlg.waypoints_widget.get_locations(RouterType.VALHALLA)):
            expected = {
                "lon": WAYPOINTS_4326[idx][0],
                "lat": WAYPOINTS_4326[idx][1],
                **extra_params[idx],
            }
            if radiuses[idx]:
                expected["radius"] = radiuses[idx]
            self.assertDictEqual(expected, loc._make_waypoint())

    def test_add_waypoints(self):
        table = self.dlg.waypoints_widget.ui_table
        self.dlg.setVisible(True)
        self.add_waypoints(WAYPOINTS_3857)

        # we have 3 coordinates in there and they're properly projected from 3857 to 4326
        self.assertEqual(table.rowCount(), 3)
        for row_id in range(table.rowCount()):
            self.assertAlmostEqual(float(table.item(row_id, 0).text()), WAYPOINTS_4326[row_id][1], 5)
            self.assertAlmostEqual(float(table.item(row_id, 1).text()), WAYPOINTS_4326[row_id][0], 5)

    def test_remove_waypoints(self):
        table = self.dlg.waypoints_widget.ui_table
        self.dlg.setVisible(True)
        self.add_waypoints(WAYPOINTS_3857)

        # select the first point and remove it
        table.selectRow(0)
        QTest.mouseClick(self.dlg.waypoints_widget.ui_btn_rm_pt, Qt.LeftButton)
        self.assertEqual(table.rowCount(), 2)

        # make sure it's the actually the first one that was removed
        first_pt = [float(table.item(0, 0).text()), float(table.item(0, 1).text())]
        self.assertAlmostEqual(first_pt[0], WAYPOINTS_4326[1][1], 5)
        self.assertAlmostEqual(first_pt[1], WAYPOINTS_4326[1][0], 5)

    def test_clear_all_waypoints(self):
        table = self.dlg.waypoints_widget.ui_table
        self.dlg.setVisible(True)
        self.add_waypoints(WAYPOINTS_3857)

        self.assertEqual(table.rowCount(), 3)
        QTest.mouseClick(self.dlg.waypoints_widget.ui_btn_rm_all, Qt.LeftButton)
        self.assertEqual(table.rowCount(), 0)

    def test_move_item_up(self):
        table = self.dlg.waypoints_widget.ui_table
        self.dlg.setVisible(True)
        self.add_waypoints(WAYPOINTS_3857)

        # remember the old configuration before moving rows
        old_first = table.item(0, 0)
        old_second = table.item(1, 0)

        table.selectRow(1)
        QTest.mouseClick(self.dlg.waypoints_widget.ui_btn_up, Qt.LeftButton)

        self.assertEqual(old_first, table.item(1, 0))
        self.assertEqual(old_second, table.item(0, 0))

    def test_move_item_down(self):
        table = self.dlg.waypoints_widget.ui_table
        self.dlg.setVisible(True)
        self.add_waypoints(WAYPOINTS_3857)

        # remember the old configuration before moving rows
        old_first = table.item(1, 0)
        old_second = table.item(2, 0)

        table.selectRow(1)
        QTest.mouseClick(self.dlg.waypoints_widget.ui_btn_down, Qt.LeftButton)

        self.assertEqual(old_first, table.item(2, 0))
        self.assertEqual(old_second, table.item(1, 0))

    def test_from_layer(self):
        self.dlg.setVisible(True)
        # First add a point layer
        pt_lyr = QgsVectorLayer("Point?crs=EPSG:3857", "single_point", "memory")
        for point in WAYPOINTS_3857:
            feat = QgsFeature()
            feat.setGeometry(QgsPoint(*point))
            pt_lyr.dataProvider().addFeature(feat)
        QgsProject.instance().addMapLayer(pt_lyr)

        # function to set the right layer
        def handle_exec():
            dlg: FromLayerDialog = QApplication.activeWindow()
            self.assertIsInstance(dlg, FromLayerDialog)
            # the layer we added will automatically be chosen
            QTest.mouseClick(dlg.buttonBox.button(QDialogButtonBox.Ok), Qt.LeftButton)

        # then press the button and set the right layer when it's open
        QTimer.singleShot(100, handle_exec)
        self.dlg.waypoints_widget._handle_from_layer()

        # test we got 3 points and they were properly transformed to 4326
        table = self.dlg.waypoints_widget.ui_table
        self.assertEqual(table.rowCount(), 3)
        for row_id in range(table.rowCount()):
            self.assertAlmostEqual(float(table.item(row_id, 0).text()), WAYPOINTS_4326[row_id][1], 5)
            self.assertAlmostEqual(float(table.item(row_id, 1).text()), WAYPOINTS_4326[row_id][0], 5)

    def test_from_valhalla_json(self):
        self.dlg.setVisible(True)

        extra_params = {
            "preferred_side": "same",
            "rank_candidates": True,
            "heading": 120,
            "display_lat": 5.32,
        }

        # mock up the JSON we'll inject into the dialog
        # keep one example of each extra data type
        locs_json = list()
        for pt in WAYPOINTS_4326:
            locs_json.append({"lon": pt[0], "lat": pt[1], "radius": 10, **extra_params})

        # function to set the right layer
        def handle_exec():
            dlg: FromValhallaJsonDialog = QApplication.activeWindow()
            self.assertIsInstance(dlg, FromValhallaJsonDialog)
            dlg.json_field.setText(json.dumps(locs_json))
            QTest.mouseClick(dlg.buttonBox.button(QDialogButtonBox.Ok), Qt.LeftButton)

        # then press the button and set the right layer when it's open
        QTimer.singleShot(100, handle_exec)
        self.dlg.waypoints_widget._handle_from_valhalla_json()

        # test we got 3 points and they were properly transformed to 4326
        table = self.dlg.waypoints_widget.ui_table
        self.assertEqual(self.dlg.waypoints_widget.ui_table.rowCount(), 3)
        for row_id in range(table.rowCount()):
            self.assertAlmostEqual(float(table.item(row_id, 0).text()), WAYPOINTS_4326[row_id][1], 5)
            self.assertAlmostEqual(float(table.item(row_id, 1).text()), WAYPOINTS_4326[row_id][0], 5)
            self.assertEqual(int(table.cellWidget(row_id, 2).value()), 10)
            assertQueryStringEqual(table.item(row_id, 3).text(), unquote(urlencode(extra_params)))

    def test_from_osrm_url(self):
        self.dlg.setVisible(True)

        radiuses = ("100", "0", "100")
        bearings = ("1,2", "3,5", "10,5")

        query_params = {"bearings": ";".join(bearings), "radiuses": ";".join(radiuses)}
        locations = list()
        for pt in WAYPOINTS_4326:
            locations.append(f"{pt[0]},{pt[1]}")
        locations_str = ";".join(locations)

        url = (
            f"https://routing.openstreetmap.de/routed-bike/route/v1/driving/"
            f"{locations_str}?"
            f"{urlencode(query_params)}"
        )

        # function to set the right layer
        def handle_exec():
            dlg: FromOsrmUrlDialog = QApplication.activeWindow()
            self.assertIsInstance(dlg, FromOsrmUrlDialog)
            dlg.ui_url.setText(url)
            QTest.mouseClick(dlg.buttonBox.button(QDialogButtonBox.Ok), Qt.LeftButton)

        # then press the button and set the right layer when it's open
        QTimer.singleShot(100, handle_exec)
        self.dlg.waypoints_widget._handle_from_osrm_url()

        # test we got 3 points and they were properly transformed to 4326
        table = self.dlg.waypoints_widget.ui_table
        self.assertEqual(self.dlg.waypoints_widget.ui_table.rowCount(), 3)
        for row_id in range(table.rowCount()):
            self.assertAlmostEqual(float(table.item(row_id, 0).text()), WAYPOINTS_4326[row_id][1], 5)
            self.assertAlmostEqual(float(table.item(row_id, 1).text()), WAYPOINTS_4326[row_id][0], 5)
            self.assertEqual(int(table.cellWidget(row_id, 2).value()), int(radiuses[row_id]))
            assertQueryStringEqual(table.item(row_id, 3).text(), f"heading={bearings[row_id]}")

    def test_waypoints_layer(self):
        self.dlg.setVisible(True)
        self.add_waypoints(WAYPOINTS_4326)

        ann_lyr: QgsAnnotationLayer = QgsProject.instance().mapLayersByName(
            self.dlg.waypoints_widget.ANN_NAME
        )[0]
        items = ann_lyr.items()
        self.assertEqual(len(items), 3)

    def test_waypoints_layer_visibility(self):
        self.dlg.setVisible(True)
        self.assertEqual(len(QgsProject.instance().mapLayers()), 0)
        self.add_waypoints(WAYPOINTS_4326)

        # test if the visibility signal fires
        points_node: QgsLayerTreeNode = (
            QgsProject.instance().layerTreeRoot().findLayer(self.dlg.waypoints_widget.points_lyr_id)
        )

        points_node.setItemVisibilityChecked(True)
        self.assertTrue(self.dlg.waypoints_widget.ui_btn_show_point_lyr.isChecked())

        points_node.setItemVisibilityChecked(False)
        self.assertFalse(self.dlg.waypoints_widget.ui_btn_show_point_lyr.isChecked())

        points_node.setItemVisibilityChecked(True)
        self.assertTrue(self.dlg.waypoints_widget.ui_btn_show_point_lyr.isChecked())

        # then check the other way around: hit the button and check visibility
        QTest.mouseClick(self.dlg.waypoints_widget.ui_btn_show_point_lyr, Qt.LeftButton)
        self.assertFalse(points_node.isVisible())
        QTest.mouseClick(self.dlg.waypoints_widget.ui_btn_show_point_lyr, Qt.LeftButton)
        self.assertTrue(points_node.isVisible())

    def test_waypoints_table_preserves_itself(self):
        # first add some points to the project's annotation layer
        self.dlg.setVisible(True)

        with NamedTemporaryFile(suffix=".qgz") as p1, NamedTemporaryFile(suffix=".qgz") as p2:
            # first write a project with 3 coords, clear the table, then write a project with 2 coords
            # write to project with all waypoints intact
            self.add_waypoints(WAYPOINTS_4326)
            self.assertEqual(self.dlg.waypoints_widget.ui_table.rowCount(), 3)
            QgsProject.instance().write(p1.name)

            self.dlg.waypoints_widget._handle_clear_locations()

            self.add_waypoints(WAYPOINTS_3857[:2])
            self.assertEqual(self.dlg.waypoints_widget.ui_table.rowCount(), 2)
            QgsProject.instance().write(p2.name)

            # now open one after the other and check that the table was updated accordingly
            QgsProject.instance().read(p1.name)
            self.assertEqual(self.dlg.waypoints_widget.ui_table.rowCount(), 3)

            QgsProject.instance().read(p2.name)
            self.assertEqual(self.dlg.waypoints_widget.ui_table.rowCount(), 2)
