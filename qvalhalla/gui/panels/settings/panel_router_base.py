from typing import List, Optional, Union

from qgis.core import (
    QgsCoordinateReferenceSystem,
    QgsFeature,
    QgsField,
    QgsFillSymbol,
    QgsGeometry,
    QgsProject,
    QgsRasterLayer,
    QgsVectorLayer,
)
from qgis.gui import QgsMapCanvas
from qgis.PyQt.QtCore import Qt, QTimer, QVariant
from qgis.PyQt.QtWidgets import (
    QCompleter,
    QDialog,
    QHBoxLayout,
    QLineEdit,
    QTreeWidgetItem,
    QTreeWidgetItemIterator,
    QVBoxLayout,
)

from ....global_definitions import Dialogs, PkgDetails, RouterType
from ....gui.panels.settings.panel_base import PanelBase
from ....gui.widgets.widget_pkgs import PkgWidget
from ...compiled.dlg_plugin_settings_ui import Ui_PluginSettingsDialog

# only needs to be set up once
LYR_PROPS = {
    "color": "transparent",
    "outline_color": "red",
    "outline_width": "5",
    "outline_width_unit": "Pixel",
}
BASE_MAP = QgsRasterLayer(
    "type=xyz&url=https://cartodb-basemaps-a.global.ssl.fastly.net/light_all/%7Bz%7D/%7Bx%7D/%7By%7D.png&zmax=19&zmin=0&crs=EPSG3857",
    "OSM",
    "wms",
)


class PanelRouterBase(PanelBase):
    SETTINGS_TYPE = Dialogs.SETTINGS
    ROUTER = None

    def __init__(
        self,
        dlg: Union[Ui_PluginSettingsDialog, QDialog],
        pkgs: List[PkgDetails],
    ):
        super().__init__(dlg)
        self.pkgs = pkgs

        self.ui_hlayout: Optional[QHBoxLayout] = None
        self.ui_pkg_tree: Optional[PkgWidget] = None
        self.ui_canvas: Optional[QgsMapCanvas] = None
        self.ui_searchbar: Optional[QLineEdit] = None
        self.completer: Optional[QCompleter] = None
        self.cur_lyr: Optional[QgsVectorLayer] = None

        # start a timer which only fires the textChanged signal every whatever ms
        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self._on_timeout)
        self.changed_text = ""

        # add the base map first thing
        QgsProject.instance().addMapLayer(BASE_MAP, False)

    def setup_panel(self):
        """Adds the composite widget with the map canvas"""
        # indicating that the user is offline the first time opening the plugin
        if not self.pkgs:
            # label = QLabel(
            #     '<span style=" font-size:1.2em; font-weight:600; color:#aa0000;">Network Offline</span>'
            # )
            # if self.ROUTER == RouterType.VALHALLA:
            #     self.dlg.ui_valhalla_remote_pkgs.layout().addWidget(label)
            # elif self.ROUTER == RouterType.OSRM:
            #     self.dlg.ui_osrm_remote_pkgs.layout().addWidget(label)
            return

        # set up the package widgets
        self.ui_hlayout = QHBoxLayout()

        # the search bar
        self.ui_searchbar = QLineEdit()
        self.ui_searchbar.setClearButtonEnabled(True)
        self.ui_searchbar.setPlaceholderText("Search for graph packages")
        self.ui_searchbar.textChanged.connect(self._on_search_change)
        completer = QCompleter([pkg.name for pkg in self.pkgs])
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.ui_searchbar.setCompleter(completer)

        # the package tree
        self.ui_pkg_tree = PkgWidget(self.dlg, self.pkgs, self.ROUTER)
        self.ui_pkg_tree.itemSelectionChanged.connect(self._on_selected_pkg_change)
        self.ui_hlayout.addWidget(self.ui_pkg_tree)

        # create base map
        self.ui_canvas = QgsMapCanvas(self.dlg)
        self.ui_canvas.setDestinationCrs(QgsCoordinateReferenceSystem.fromEpsgId(3857))
        self._reset_canvas()
        self.ui_canvas.show()
        self.ui_hlayout.addWidget(self.ui_canvas)

        # add the widgets to the vertical layout
        layout: QVBoxLayout = (
            self.dlg.ui_valhalla_pkgs.layout()
            if self.ROUTER == RouterType.VALHALLA
            else self.dlg.ui_osrm_pkgs.layout()
        )
        layout.addWidget(self.ui_searchbar)
        layout.addLayout(self.ui_hlayout)

    def _on_search_change(self, new_text: str):
        """
        When typing (or auto-complete) this updates the tree widget
        with only matching items (startswith() as matcher); only every 200 ms
        """
        self.timer.start(200)
        self.changed_text = new_text

    def _on_timeout(self):
        """Will only fire when QTimer has ended"""
        select_item: Optional[QTreeWidgetItem] = None

        def set_item_status(item: QTreeWidgetItem, status: bool):
            if item.parent():
                item.parent().setHidden(status)
            item.setHidden(status)

        iterator: QTreeWidgetItemIterator = QTreeWidgetItemIterator(self.ui_pkg_tree)
        while iterator.value():
            item: QTreeWidgetItem = iterator.value()
            if (
                not self.changed_text
                or item.text(0).lower().startswith(self.changed_text.lower())
                and self.ui_pkg_tree.indexOfTopLevelItem(item) == -1
            ):
                set_item_status(item, False)
                select_item = item
            else:
                item.setHidden(True)
            iterator += 1

        # makes sure that the item is showing in the canvas
        if select_item:
            self.ui_pkg_tree.clearSelection()
            select_item.setSelected(True)
            if select_item.parent():
                select_item.parent().setExpanded(True)

        # reset the canvas if no text in the search bar
        if not self.changed_text:
            self._reset_canvas()

    def _on_selected_pkg_change(self):
        """Removes the current layer and adds a new one for the selected package boundaries"""
        selected = self.ui_pkg_tree.selectedItems()
        if not selected:
            return
        item: QTreeWidgetItem = selected[0]

        if self.ui_pkg_tree.indexOfTopLevelItem(item) != -1:
            self._reset_canvas()
            return

        # add the layer
        if self.cur_lyr:
            QgsProject.instance().removeMapLayer(self.cur_lyr.id())
        self.cur_lyr = QgsVectorLayer("Polygon?crs=EPSG:4326", "pkg_geom", "memory")
        self.cur_lyr.dataProvider().addAttributes([QgsField("id", QVariant.Int)])
        self.cur_lyr.updateFields()

        # create and add the feature
        feat = QgsFeature()
        feat.setGeometry(QgsGeometry.fromPolygonXY([self.ui_pkg_tree.pkg_geoms[item.text(0)]]))
        feat.setAttributes([0])
        self.cur_lyr.dataProvider().addFeature(feat)
        self.cur_lyr.updateExtents()

        # style the layer
        self.cur_lyr.renderer().setSymbol(QgsFillSymbol.createSimple(LYR_PROPS))

        QgsProject.instance().addMapLayer(self.cur_lyr, False)

        # zoom to the one feature
        self.cur_lyr.selectAll()
        self.ui_canvas.setLayers([self.cur_lyr, BASE_MAP])
        self.ui_canvas.zoomToSelected(self.cur_lyr)
        self.cur_lyr.deselect(next(self.cur_lyr.getFeatures()).id())

    def _reset_canvas(self):
        """Resets the canvas to not show any layers"""
        self.ui_canvas.setExtent(BASE_MAP.extent())
        self.ui_canvas.setLayers([BASE_MAP])
        if self.cur_lyr:
            QgsProject.instance().removeMapLayer(self.cur_lyr.id())
            self.cur_lyr = None

        self.ui_pkg_tree.clearSelection()
