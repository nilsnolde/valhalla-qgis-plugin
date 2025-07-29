import json
from collections import defaultdict
from enum import Enum, unique
from typing import DefaultDict, Generator, List, Optional, Tuple, Union
from urllib.parse import parse_qsl, urlparse

from qgis.core import (
    Qgis,
    QgsAnnotationLayer,
    QgsAnnotationMarkerItem,
    QgsCoordinateTransform,
    QgsFeature,
    QgsLayerTreeNode,
    QgsMarkerSymbol,
    QgsPoint,
    QgsPointXY,
    QgsProject,
    QgsSvgMarkerSymbolLayer,
    QgsUnitTypes,
)
from qgis.gui import QgisInterface, QgsMapTool, QgsSpinBox
from qgis.PyQt.QtCore import QPointF, QSize
from qgis.PyQt.QtWidgets import (
    QAbstractItemView,
    QAction,
    QApplication,
    QDialog,
    QHBoxLayout,
    QHeaderView,
    QLayout,
    QMenu,
    QSizePolicy,
    QSpacerItem,
    QTableWidget,
    QTableWidgetItem,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from ...global_definitions import RouterType
from ...gui.dlg_from_lyr import FromLayerDialog
from ...gui.maptools import PointTool
from ...third_party.routingpy.routingpy import Valhalla
from ...utils.geom_utils import point_to_wgs84
from ...utils.misc_utils import str_is_bool, str_is_float, str_to_bool
from ...utils.resource_utils import get_icon, get_resource_path
from ..dlg_from_json import FromValhallaJsonDialog
from ..dlg_from_osrm_url import FromOsrmUrlDialog


@unique
class WayPtWidgetElems(Enum):
    ADD_PT = "ui_btn_add_pt"
    DEL_PT = "ui_btn_rm_pt"
    DEL_ALL = "ui_btn_rm_all"
    FROM_LYR = "ui_btn_from_lyr"
    FROM_JSON = "ui_btn_from_valhalla_json"
    FROM_URL = "ui_btn_from_osrm_url"
    SHOW_POINTS = "ui_btn_points"
    MV_UP = "ui_btn_up"
    MV_DOWN = "ui_btn_down"
    TABLE = "ui_table"


BUTTONS = {
    WayPtWidgetElems.ADD_PT: (
        ":images/themes/default/mActionAdd.svg",
        "Add points from the canvas, double-click when finished",
    ),
    WayPtWidgetElems.DEL_PT: (
        ":images/themes/default/symbologyRemove.svg",
        "Remove selected points",
    ),
    WayPtWidgetElems.DEL_ALL: (
        ":images/themes/default/mActionRemove.svg",
        "Clear all points",
    ),
    WayPtWidgetElems.FROM_LYR: (
        ":images/themes/default/mActionAddLayer.svg",
        "Add points from a layer",
    ),
    WayPtWidgetElems.FROM_JSON: (
        ":images/themes/default/mActionAddHtml.svg",
        "Add points from a Valhalla locations JSON",
    ),
    WayPtWidgetElems.FROM_URL: (
        ":images/themes/default/mActionAddHtml.svg",
        "Add points from a OSRM URL",
    ),
    WayPtWidgetElems.MV_UP: (
        ":images/themes/default/mActionArrowUp.svg",
        "Move point up.",
    ),
    WayPtWidgetElems.MV_DOWN: (
        ":images/themes/default/mActionArrowDown.svg",
        "Move point down",
    ),
    WayPtWidgetElems.SHOW_POINTS: (
        ":images/themes/default/mActionCapturePoint.svg",
        "Show/hide waypoints",
    ),
}


def build_btn(layout: QLayout, btn_type: WayPtWidgetElems, checkable: bool = False) -> QToolButton:
    """Builds a button of configured type and adds it to the passed layout"""
    name = btn_type.value
    icon_path, tip = BUTTONS[btn_type]

    btn = QToolButton()
    btn.setCheckable(checkable)
    btn.setIcon(get_icon(icon_path))
    btn.setObjectName(name)
    btn.setIconSize(QSize(16, 16))
    btn.setToolTip(tip)

    layout.addWidget(btn)

    return btn


def extract_locations(  # noqa: C901
    router: RouterType, locations: Union[List[dict], str]
) -> Generator[Tuple[float, float, int, str], None, None]:
    """
    Extracts extra parameters being set on a OSRM URL or a Valhalla location JSON

    :param router: the router/provider type
    :param location: the whole valhalla location JSON or OSRM URL
    :returns: lat, lon, radius, extra_col
    :raises: ValueError
    """
    if router == RouterType.VALHALLA:
        for loc in locations:
            extra_col: List[str] = list()
            radius = 0
            for k, v in loc.items():
                if k in ("lat", "lon", "search_filter"):
                    continue
                elif k == "radius":
                    radius = v
                    continue
                extra_col.append(f"{k}={v}")

            yield loc["lat"], loc["lon"], radius, "&".join(extra_col)
    else:
        # OSRM needs to be parsed from the URL
        parsed_url = urlparse(locations)
        # filter the parameters to only location-relevant ones and split the values
        params = {
            k: [y for y in v.split(";")]
            for k, v in filter(lambda x: x[0] in ("bearings", "radiuses"), parse_qsl(parsed_url.query))
        }
        locs = (
            locations.split("/")[-1].split("?")[0].split(";")
        )  # urlparse gets confused here with OSRM's location stuff in the path
        radiuses: List[str] = params.get("radiuses", list())

        if not all([len(x) == len(locs) for x in params.values()]):
            raise ValueError("Query parameters are not consistent with the amount of locations")

        for idx, loc in enumerate(locs):
            extra_col: str = ""
            if params.get("bearings"):
                # for now, we convert this to valhalla params
                extra_col += f"heading={params['bearings'][idx]}"
            lon, lat = [float(x) for x in loc.split(",")]

            radius = 0
            if len(radiuses) > 0:
                if radiuses[idx].isnumeric():
                    radius = int(radiuses[idx])

            yield lat, lon, radius, extra_col


class WaypointsWidget(QWidget):
    ANN_NAME = "NA Waypoints"

    def __init__(
        self,
        parent_dlg: QWidget = None,
        iface: QgisInterface = None,
        color_markers: bool = True,
    ):
        """
        Represents the waypoint table widget. Needs to be added to the parent's layout
        widget by the caller.

        :param parent_dlg: Parent dialog
        :param iface: The QGIS interface
        :param color_markers: Whether origin/destination should show colored markers
        """
        super().__init__(parent_dlg)
        self.iface = iface
        self.parent_dlg = parent_dlg
        self.color_markers = color_markers

        self.point_tool = PointTool(self.iface.mapCanvas())
        self.last_maptool: Optional[QgsMapTool] = None

        self.setupUi()

        # keep a reference of the annotation layer and its ID
        self.points_lyr: Optional[QgsAnnotationLayer] = None
        self.points_lyr_id: Optional[str] = None

        # always look for an existing annotation layer before creating a new one
        self._handle_read_project()
        self.iface.projectRead.connect(self._handle_read_project)

    def get_locations(self, router: RouterType) -> List[Union[Tuple[float, float], Valhalla.Waypoint]]:
        """Convenience method for getting coordinate tuples of all table rows."""
        locations = list()
        # for Valhalla we have to build routingpy Valhalla.Waypoint objects
        if router == RouterType.VALHALLA:
            for row in range(self.ui_table.rowCount()):
                kwargs = dict()
                for k, v in parse_qsl(self.ui_table.item(row, 3).text()):
                    if v.isnumeric():
                        kwargs[k] = int(v)
                    elif str_is_bool(v):
                        kwargs[k] = str_to_bool(v)
                    elif str_is_float(v):
                        kwargs[k] = float(v)
                    else:  # it's a string
                        kwargs[k] = v
                radius = self.ui_table.cellWidget(row, 2).value()
                if radius > 0:
                    kwargs["radius"] = radius
                locations.append(
                    Valhalla.Waypoint(
                        [float(self.ui_table.item(row, x).text()) for x in (1, 0)],  # lon, lat
                        **kwargs,
                    )
                )
        else:
            for row in range(self.ui_table.rowCount()):
                locations.append([float(self.ui_table.item(row, x).text()) for x in (1, 0)])

        return locations

    def get_extra_params(self, router: RouterType) -> Union[DefaultDict, dict]:
        """Returns OSRM parameters that are stored in the locations table"""
        if router == RouterType.VALHALLA:
            return {}

        params = defaultdict(list)
        for row in range(self.ui_table.rowCount()):
            table_params = {
                k: v
                for k, v in filter(
                    lambda x: x[0] == "bearing",
                    parse_qsl(self.ui_table.item(row, 3).text()),
                )
            }
            params["bearings"].append(
                [int(x) for x in table_params.get("bearing", "360,180").split(",")]
            )
            params["radiuses"].append(
                self.ui_table.cellWidget(row, 2).value() or "unlimited"
            )  # avoid radius=0

        return params

    def _add_row_to_table(self, row: int, lat: float, lon: float, radius: int = 0, extra: str = ""):
        """
        Adds radiuses and bearings to the table's locations
        """
        radius_w = QgsSpinBox()
        radius_w.setMaximum(100000)
        radius_w.setValue(radius)
        self.ui_table.setItem(row, 0, QTableWidgetItem(str(round(lat, 6))))
        self.ui_table.setItem(row, 1, QTableWidgetItem(str(round(lon, 6))))
        self.ui_table.setCellWidget(row, 2, radius_w)
        extra_col = QTableWidgetItem(extra)
        extra_col.setToolTip(extra)
        self.ui_table.setItem(row, 3, extra_col)

    def _handle_from_layer(self):
        """Fires a dialog to choose a Point layer and populates the waypoints table with the features."""
        dlg = FromLayerDialog(self.parent_dlg)
        r = dlg.exec()

        if r == QDialog.Rejected or not dlg.layer or not dlg.layer.isValid():
            return

        feat: QgsFeature
        for feat in dlg.layer.getFeatures():
            pt: QgsPointXY = point_to_wgs84(feat.geometry().asPoint(), dlg.layer.crs())
            row_id = self.ui_table.rowCount()
            self.ui_table.insertRow(row_id)
            self._add_row_to_table(row_id, pt.y(), pt.x())

        self._reset_annotations()

    def _handle_from_osrm_url(self):
        """Fill the locations table by parsing a OSRM URL"""
        url_dlg = FromOsrmUrlDialog(self.parent_dlg)
        r = url_dlg.exec()
        if r != QDialog.Accepted:
            return

        try:
            row_count = self.ui_table.rowCount()
            for idx, loc_args in enumerate(extract_locations(RouterType.OSRM, url_dlg.ui_url.text())):
                row_id = idx + row_count
                self.ui_table.insertRow(row_id)
                self._add_row_to_table(row_id, *loc_args)
        except ValueError as e:
            self.parent_dlg.status_bar.pushMessage("OSRM Error", str(e), Qgis.Critical, 8)

    def _handle_from_valhalla_json(self):
        """Fill the locations table by parsing a Valhalla locations JSON"""
        json_dlg = FromValhallaJsonDialog(self.parent_dlg)
        r = json_dlg.exec()
        if r != QDialog.Accepted:
            return

        try:
            json_obj = json.loads(json_dlg.json_field.toPlainText())
            if not isinstance(json_obj, list):
                raise ValueError(
                    f"Passed JSON is not an array of Valhalla locations: {json_dlg.json_field.toPlainText()}"
                )
        except (json.JSONDecodeError, ValueError) as e:
            self.parent_dlg.status_bar.pushMessage("JSON Error", str(e), Qgis.Critical, 8)
            return

        row_count = self.ui_table.rowCount()
        for idx, loc_args in enumerate(extract_locations(RouterType.VALHALLA, json_obj)):
            row_id = idx + row_count
            self.ui_table.insertRow(row_id)
            self._add_row_to_table(row_id, *loc_args)

        self._reset_annotations()

    def _handle_clear_locations(self):
        """Clear the table and the annotations layer"""
        if QgsProject.instance().mapLayersByName(self.ANN_NAME):
            self.points_lyr.clear()
        for row_id in reversed(range(self.ui_table.rowCount())):
            self.ui_table.removeRow(row_id)

    def _handle_read_project(self):
        """If there's an existing annotation layer in the new project, read that instead."""
        annotation_lyr = QgsProject.instance().mapLayersByName(self.ANN_NAME)
        if not annotation_lyr:
            return

        # there's already an annotation layer, convert it to the table, after clearing the current contents
        self.points_lyr: QgsAnnotationLayer = annotation_lyr[0]
        self.points_lyr_id = self.points_lyr.id()
        for row_id in reversed(range(self.ui_table.rowCount())):
            self.ui_table.removeRow(row_id)
        for _, item in self.points_lyr.items().items():
            pt = point_to_wgs84(item.geometry(), self.iface.mapCanvas().mapSettings().destinationCrs())
            row_id = self.ui_table.rowCount()
            self.ui_table.insertRow(row_id)
            self._add_row_to_table(row_id, pt.y(), pt.x())

        # attach the node to a slot
        self._attach_node_to_slot()

    def _handle_points_btn_toggle(self, checked: bool):
        """hides/shows the waypoint layer in the canvas"""
        if not QgsProject.instance().mapLayer(self.points_lyr_id):
            self._reset_annotations()
        QgsProject.instance().layerTreeRoot().findLayer(self.points_lyr.id()).setItemVisibilityChecked(
            checked
        )

    def _handle_points_layer_toggle(self, node: QgsLayerTreeNode):
        """gets a signal when a layer's visibility as been changed so we switch the button in the UI"""
        if not node.name() == self.ANN_NAME:
            return

        self.ui_btn_show_point_lyr.setChecked(node.isVisible())

    def _handle_pt_up(self):
        """Move a location up in the table."""
        cur_row = self.ui_table.currentRow()
        cur_col = self.ui_table.currentColumn()
        if cur_row > 0:
            self.ui_table.insertRow(cur_row - 1)
            for col in range(self.ui_table.columnCount()):
                if self.ui_table.cellWidget(cur_row + 1, col):
                    self.ui_table.setCellWidget(
                        cur_row - 1, col, self.ui_table.cellWidget(cur_row + 1, col)
                    )
                else:
                    self.ui_table.setItem(cur_row - 1, col, self.ui_table.takeItem(cur_row + 1, col))
                self.ui_table.setCurrentCell(cur_row - 1, cur_col)
            self.ui_table.removeRow(cur_row + 1)

        self._reset_annotations()

    def _handle_pt_down(self):
        """Move a location down in the table."""
        cur_row = self.ui_table.currentRow()
        cur_col = self.ui_table.currentColumn()
        if cur_row < self.ui_table.rowCount() - 1:
            self.ui_table.insertRow(cur_row + 2)
            for col in range(self.ui_table.columnCount()):
                if self.ui_table.cellWidget(cur_row + 1, col):
                    self.ui_table.setCellWidget(cur_row + 2, col, self.ui_table.cellWidget(cur_row, col))
                else:
                    self.ui_table.setItem(cur_row + 2, col, self.ui_table.takeItem(cur_row, col))
                self.ui_table.setCurrentCell(cur_row + 2, cur_col)
            self.ui_table.removeRow(cur_row)

        self._reset_annotations()

    def _handle_init_maptool(self):
        """Set up the maptool: remember the last one used."""
        if self.ui_btn_add_pt.isChecked():
            self.last_maptool = self.iface.mapCanvas().mapTool()
            self.iface.mapCanvas().setMapTool(self.point_tool)

            # add a layer if not there already
            ann_lyr = QgsProject.instance().mapLayer(self.points_lyr_id)
            if not ann_lyr:
                self._reset_annotations()
            # make sure it's also visible
            QgsProject.instance().layerTreeRoot().findLayer(
                self.points_lyr.id()
            ).setItemVisibilityChecked(True)
        else:
            self._handle_doubleclick()

    def _handle_add_pt(self, pt: QgsPointXY):
        """Transforms the clicked point and adds it to the table."""
        # transform the point and insert into the table
        new_pt = point_to_wgs84(pt, self.iface.mapCanvas().mapSettings().destinationCrs())

        row_id = (
            self.ui_table.currentRow() + 1
            if self.ui_table.currentRow() != -1
            else self.ui_table.rowCount()
        )
        self.ui_table.insertRow(row_id)
        self._add_row_to_table(row_id, new_pt.y(), new_pt.x())

        # select the new point in the table so the next clicked point goes to the end of the table
        self.ui_table.clearSelection()
        self.ui_table.selectRow(row_id)

        # define the annotation's symbol
        self.points_lyr.addItem(self._get_annotation(pt, -1))

    def _handle_doubleclick(self):
        """Shows the parent dlg again and restores previous settings"""
        self._reset_annotations()
        self.ui_btn_add_pt.setChecked(False)

        # then restore some of the things we set up when initializing the point tool
        QApplication.restoreOverrideCursor()
        QApplication.processEvents()
        self.iface.mapCanvas().setMapTool(self.last_maptool)

    def _handle_remove_pt(self):
        """Remove a point from the locations table."""
        # first collect the row ids
        max_row = self.ui_table.rowCount()
        rm_idx = list()
        for row_id in range(max_row):
            if self.ui_table.item(row_id, 0).isSelected():
                rm_idx.append(row_id)

        # then remove those in reverse order to not mess with table internal ordering
        rm_idx = sorted(rm_idx, reverse=True)
        for idx in rm_idx:
            self.ui_table.removeRow(idx)

        self._reset_annotations()

    def _reset_annotations(self):
        """Helper method to reset the annotation layer based on the current locations table."""
        # first remove the annotation layer
        if QgsProject.instance().mapLayer(self.points_lyr_id):
            QgsProject.instance().removeMapLayer(self.points_lyr_id)

        # then build it up again with the new points
        self.points_lyr = QgsAnnotationLayer(
            self.ANN_NAME,
            QgsAnnotationLayer.LayerOptions(QgsProject.instance().transformContext()),
        )
        self.points_lyr_id = self.points_lyr.id()

        for row_id in range(self.ui_table.rowCount()):
            pt = QgsPointXY(
                float(self.ui_table.item(row_id, 1).text()),
                float(self.ui_table.item(row_id, 0).text()),
            )
            pt = point_to_wgs84(
                pt,
                self.iface.mapCanvas().mapSettings().destinationCrs(),
                QgsCoordinateTransform.ReverseTransform,
            )
            self.points_lyr.addItem(self._get_annotation(QgsPoint(pt.x(), pt.y()), row_id))

        # add layer to the project and connect the visibility signal
        QgsProject.instance().addMapLayer(self.points_lyr)
        self._attach_node_to_slot()

    def _attach_node_to_slot(self):
        """Attaches the node's visibility signal to a slot and sets the checked status of the button"""
        points_node: QgsLayerTreeNode = (
            QgsProject.instance().layerTreeRoot().findLayer(self.points_lyr_id)
        )
        points_node.visibilityChanged.connect(self._handle_points_layer_toggle)
        self.ui_btn_show_point_lyr.setChecked(points_node.isVisible())

    def _get_annotation(self, pt, row_id) -> QgsAnnotationMarkerItem:
        """Helper to create an annotation object"""

        # only color origin & destination if the parent wants it
        if not self.color_markers or row_id not in (
            0,
            self.ui_table.rowCount() - 1,
        ):
            svg = "via.svg"
        elif row_id == 0:
            svg = "origin.svg"
        else:
            svg = "destination.svg"

        symbol = QgsMarkerSymbol()
        symbol.deleteSymbolLayer(0)
        symbol_layer = QgsSvgMarkerSymbolLayer(str(get_resource_path("icons", svg)), 8)
        symbol_layer.setOffsetUnit(QgsUnitTypes.RenderPoints)
        symbol_layer.setOffset(
            QPointF(0, -11)
        )  # tweaked so the tip of the marker points at the clicked location
        symbol.appendSymbolLayer(symbol_layer)
        annotation = QgsAnnotationMarkerItem(QgsPoint(pt.x(), pt.y()))
        annotation.setSymbol(symbol)

        return annotation

    def setupUi(self):
        """does the same as the usual setupUi() method from pyuic5"""
        self.outer_layout = QVBoxLayout(self)
        self.buttons_layout = QHBoxLayout(self)

        # set up buttons
        self.ui_btn_add_pt = build_btn(self.buttons_layout, WayPtWidgetElems.ADD_PT, True)
        self.ui_btn_rm_pt = build_btn(self.buttons_layout, WayPtWidgetElems.DEL_PT)
        self.ui_btn_rm_all = build_btn(self.buttons_layout, WayPtWidgetElems.DEL_ALL)
        self.ui_btn_from_lyr = build_btn(self.buttons_layout, WayPtWidgetElems.FROM_LYR)
        self.ui_btn_show_point_lyr = build_btn(self.buttons_layout, WayPtWidgetElems.SHOW_POINTS)
        self.ui_btn_show_point_lyr.setCheckable(True)
        self.ui_btn_show_point_lyr.setChecked(True)
        self.ui_btn_up = build_btn(self.buttons_layout, WayPtWidgetElems.MV_UP)
        self.ui_btn_down = build_btn(self.buttons_layout, WayPtWidgetElems.MV_DOWN)

        # do the "from layer/json" dropdown button
        self.ui_btn_from_lyr.setPopupMode(QToolButton.MenuButtonPopup)
        self.ui_btn_from_lyr.setAutoRaise(False)
        self.ui_btn_from_lyr.triggered.connect(self.ui_btn_from_lyr.setDefaultAction)

        dropdown_menu = QMenu()
        actions = list()
        for btn, title, connect_fn in (
            (WayPtWidgetElems.FROM_LYR, "Point layer", self._handle_from_layer),
            (
                WayPtWidgetElems.FROM_JSON,
                "Valhalla JSON",
                self._handle_from_valhalla_json,
            ),
            (WayPtWidgetElems.FROM_URL, "OSRM URL", self._handle_from_osrm_url),
        ):
            icon_fp, tooltip = BUTTONS[btn]
            action = QAction(get_icon(icon_fp), f"From {title}", self.parent_dlg)
            action.triggered.connect(connect_fn)
            action.setToolTip(tooltip)
            dropdown_menu.addAction(action)
            actions.append(action)

        self.ui_btn_from_lyr.setMenu(dropdown_menu)
        self.ui_btn_from_lyr.setDefaultAction(actions[0])

        # add horizontal spacer
        space = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.buttons_layout.insertSpacerItem(5, space)

        # add the buttons to the outer layout
        self.outer_layout.addLayout(self.buttons_layout)

        # add table widget to the outer layout
        self.ui_table = QTableWidget(0, 4, self)
        self.ui_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.ui_table.setObjectName(WayPtWidgetElems.TABLE.value)
        self.ui_table.setHorizontalHeaderItem(0, QTableWidgetItem())
        self.ui_table.setHorizontalHeaderItem(1, QTableWidgetItem())
        radius_col = QTableWidgetItem()
        radius_col.setToolTip("Radius in meters")
        self.ui_table.setHorizontalHeaderItem(2, radius_col)
        extra_col = QTableWidgetItem()
        extra_col.setToolTip(
            "Extra location properties in URL form, e.g. 'bearing=120,20&hint=348sfj89sa' for OSRM or 'heading=120&preferred_side=same' for Valhalla "
        )
        self.ui_table.setHorizontalHeaderItem(3, extra_col)
        self.ui_table.setHorizontalHeaderLabels(("Lat", "Lon", "Radius", "Extra"))

        # set table dimensions
        self.ui_table.setMinimumHeight(200)
        table_header: QHeaderView = self.ui_table.horizontalHeader()
        table_header.setSectionResizeMode(QHeaderView.Stretch)
        self.outer_layout.addWidget(self.ui_table)

        # make connections
        self.ui_btn_add_pt.clicked.connect(self._handle_init_maptool)
        self.ui_btn_rm_pt.clicked.connect(self._handle_remove_pt)
        self.ui_btn_rm_all.clicked.connect(self._handle_clear_locations)
        self.point_tool.canvasClicked.connect(self._handle_add_pt)
        self.point_tool.doubleClicked.connect(self._handle_doubleclick)
        self.ui_btn_up.clicked.connect(self._handle_pt_up)
        self.ui_btn_down.clicked.connect(self._handle_pt_down)
        self.ui_btn_show_point_lyr.clicked.connect(self._handle_points_btn_toggle)
