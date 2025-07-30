import json
import webbrowser
from copy import deepcopy
from typing import List, Optional, Tuple

from qgis.core import (  # noqa: F811
    Qgis,
    QgsFeature,
    QgsFields,
    QgsGeometry,
    QgsPointXY,
    QgsProject,
    QgsVectorLayer,
    QgsWkbTypes,
)
from qgis.gui import QgisInterface, QgsDockWidget
from qgis.PyQt.QtWidgets import (
    QLineEdit,
    QMessageBox,
    QTextEdit,
    QToolButton,
    QWidget,
)

from ..core.results_factory import ResultsFactory
from ..core.settings import ProviderSetting, ValhallaSettings
from ..exceptions import ValhallaError
from ..global_definitions import (
    DEFAULT_LAYER_FIELDS,
    Dialogs,
    RouterEndpoint,
    RouterMethod,
    RouterType,
)
from ..gui.widgets.widget_router import PROFILE_TO_UI, RouterWidget
from ..gui.widgets.widget_routing_params import RoutingParamsWidget
from ..gui.widgets.widget_waypoints import WaypointsWidget
from ..third_party.routingpy import routingpy
from ..third_party.routingpy.routingpy.utils import deep_merge_dicts
from ..utils.http_utils import get_status_response
from ..utils.layer_utils import post_process_layer
from ..utils.resource_utils import get_graph_dir, get_icon, get_resource_path
from .compiled.widget_routing_dock_ui import Ui_routing_widget
from .dlg_about import AboutDialog
from .gui_utils import add_msg_bar

MENU_TABS = {
    RouterEndpoint.DIRECTIONS: "ui_directions_params",
    RouterEndpoint.ISOCHRONES: "ui_isochrones_params",
    RouterEndpoint.MATRIX: "ui_matrix_params",
    RouterEndpoint.EXPANSION: "ui_expansion_params",
}

DEFAULT_PROVIDERS = [
    ProviderSetting("FOSSGIS", "https://valhalla1.openstreetmap.de", "", "access_key"),  # auth_key
    ProviderSetting("localhost", "http://localhost:8002", "", ""),  # auth_key
]

HELP_URL = "https://github.com/nilsnolde/valhalla-qgis-plugin?tab=readme-ov-file#how-to"


class RoutingDockWidget(QgsDockWidget, Ui_routing_widget):
    def __init__(self, iface: QgisInterface = None):
        QgsDockWidget.__init__(self)
        widget = QWidget(self)
        self.setupUi(widget)
        self.ui_log_btn.setIcon(get_icon("url.svg"))
        self.ui_graph_btn.setIcon(get_icon("graph_extent_icon.svg"))

        self.iface = iface

        # add a status bar
        self.status_bar = add_msg_bar(self.verticalWrapper)
        # keep the params so we can show them in the log window
        self.log_params = dict()
        self.endpoint = ""

        # make sure we have at least one remote HTTP API URL
        settings = ValhallaSettings()
        if not settings.get_providers(RouterType.VALHALLA):
            for prov in DEFAULT_PROVIDERS:
                settings.set_provider(RouterType.VALHALLA.lower(), prov)

        # add custom widgets to this dialog
        self.router_widget = RouterWidget(self)
        self.router_box.layout().addWidget(self.router_widget)
        self.waypoints_widget = WaypointsWidget(self, self.iface)
        self.waypoints_box.layout().addWidget(self.waypoints_widget)
        self.routing_params_widget = RoutingParamsWidget(self, self.iface)
        self.options_box.layout().addWidget(self.routing_params_widget)

        # initial factory, will/should always be HTTP
        self.factory = ResultsFactory(
            self.router_widget.router,
            self.router_widget.method,
            self.router_widget.profile,
            self.router_widget.provider.url,
        )

        self._on_profile_change()

        # connections
        self.menu_widget.currentRowChanged["int"].connect(self._on_router_or_menu_change)
        self.menu_widget.currentRowChanged["int"].connect(self.ui_params_stacked.setCurrentIndex)
        self.router_widget.ui_cmb_prov.currentIndexChanged.connect(self._on_provider_changed)
        self.execute_btn.clicked.connect(self._on_execute)
        self.ui_about_btn.clicked.connect(self._on_about_click)
        self.ui_log_btn.clicked.connect(self._on_log_click)
        self.router_widget.mode_btns.buttonToggled.connect(self._on_profile_change)
        self.ui_graph_btn.clicked.connect(self._on_graph_click)
        self.ui_help_btn.clicked.connect(lambda: webbrowser.open(HELP_URL))

        # icons on left side menu
        self.menu_widget.item(0).setIcon(get_icon("directions_icon.svg"))
        self.menu_widget.item(1).setIcon(get_icon("isochrones_icon.svg"))
        self.menu_widget.item(2).setIcon(get_icon("matrix_icon.svg"))
        self.menu_widget.item(3).setIcon(get_icon("expansion_icon.svg"))

        self.setWindowTitle("Valhalla - Routing")

        self.setWidget(widget)

    def _get_params(self, endpoint: RouterEndpoint) -> dict:
        """Returns the current parameters"""

        def get_intervals(widget: QLineEdit) -> List[float]:
            try:
                intervals = [float(x) for x in widget.text().split(",")]
                if not intervals:
                    raise ValueError
                return intervals
            except ValueError:
                return list()

        # this relies on the fact that we have the order of endpoints in the left menu widget
        params = dict()
        if self.router_widget.router == RouterType.VALHALLA:
            if endpoint == RouterEndpoint.DIRECTIONS:
                params["instructions"] = False

            elif endpoint == RouterEndpoint.ISOCHRONES:
                params["intervals"] = get_intervals(self.ui_isochrone_intervals)
                params["interval_type"] = (
                    "distance" if self.ui_isochrone_distance.isChecked() else "time"
                )
                params["polygons"] = True
                params["denoise"] = float(self.ui_isochrone_denoise.value())
                params["generalize"] = int(self.ui_isochrone_generalize.value())

            elif endpoint == RouterEndpoint.EXPANSION:
                params["intervals"] = get_intervals(self.ui_expansion_intervals)
                params["interval_type"] = (
                    "distance" if self.ui_expansion_distance.isChecked() else "time"
                )
                params["expansion_properties"] = ("duration", "distance")
                params["dedupe"] = self.ui_expansion_dedupe.isChecked()
                params["skip_opposites"] = self.ui_expansion_skip_opps.isChecked()

            # only append the costing options if the costing options widget is active
            return {
                **params,
                **(
                    self.routing_params_widget.get_costing_params()
                    if self.options_box.isChecked()
                    else dict()
                ),
            }
        else:
            if endpoint == RouterEndpoint.DIRECTIONS:
                params["overview"] = "full"

            return params

    def _get_output_layer(
        self,
        endpoint: RouterEndpoint,
        locations: List[Tuple[float, float]],
        params: dict,
    ) -> QgsVectorLayer:
        """
        Returns the result features as a single vector layer.

        :endpoint: one of RouterEndpoint
        :profile: one of RouterProfile
        :locations: locations as iterable of lng/lat coordinate tuples
        :params: additional parameter dictionary
        """
        router = self.router_widget.router
        layer_name = "{} {} {}".format(
            router.capitalize() if router == RouterType.VALHALLA else router.upper(),
            endpoint.capitalize(),
            self.router_widget.profile.capitalize() if self.router_widget.profile else "",
        )

        out_lyr = QgsVectorLayer(
            f"{QgsWkbTypes.displayString(self.factory.geom_type(endpoint))}?crs=EPSG:4326",
            layer_name,
            "memory",
        )
        layer_fields = QgsFields()
        for f in DEFAULT_LAYER_FIELDS[endpoint]:
            layer_fields.append(f)

        out_lyr.dataProvider().addAttributes(layer_fields)
        out_lyr.updateFields()

        for feat in self.factory.get_results(endpoint, locations, params):
            out_lyr.dataProvider().addFeature(feat)

        out_lyr.updateExtents()

        # give the layer some styling etc.
        post_process_layer(out_lyr, endpoint)

        return out_lyr

    def _on_execute(self):
        self.endpoint = list(MENU_TABS)[self.menu_widget.currentRow()]
        params = self._get_params(self.endpoint)
        self.factory.profile = self.router_widget.profile  # update profile

        if (
            self.endpoint in (RouterEndpoint.ISOCHRONES, RouterEndpoint.EXPANSION)
            and not params["intervals"]
        ):
            self.status_bar.pushMessage(
                "Please provide intervals as comma separated numbers (e.g. 100,200,300)",
                Qgis.Critical,
                8,
            )
            return

        # get both the locations and location parameters (only OSRM) from the waypoint table
        locations = self.waypoints_widget.get_locations(self.router_widget.router)
        params.update(self.waypoints_widget.get_extra_params(self.router_widget.router))

        # build the stuff for logging
        # params have "options" instead of "costing_options" bcs of routing-py
        self.log_params = deepcopy(params)
        if current_options := self.log_params.get("options"):
            self.log_params.pop("options")
            temp = {"costing_options": {self.router_widget.profile: current_options}}
            self.log_params = deep_merge_dicts(temp, self.log_params)

        self.log_params["costing"] = self.router_widget.profile
        self.log_params["locations"] = [
            {"lon": wp._position[0], "lat": wp._position[1], **wp._kwargs} for wp in locations
        ]

        try:
            lyr = self._get_output_layer(self.endpoint, locations, params)
        except routingpy.exceptions.RouterError as e:  # HTTP error
            msg = str(e.message.get("error") or e.message) if isinstance(e.message, dict) else e.message
            self.status_bar.pushMessage(
                f"HTTP Error {e.status}",
                msg,
                Qgis.Critical,
                8,
            )
            return
        except (RuntimeError, ValhallaError) as e:  # Bindings & factory error
            self.status_bar.pushMessage("Error", str(e), Qgis.Critical, 8)
            return

        QgsProject.instance().addMapLayer(lyr)

    def _on_settings_change(self, new_text, widget: Optional[QWidget] = ""):
        attr = widget.objectName() if widget else self.sender().objectName()
        ValhallaSettings().set(Dialogs.ROUTING, attr, str(new_text))

    def _on_router_or_menu_change(self, menu_index: int):
        """Disables/enables some widgets if it's OSRM isochrone/expansion"""
        # is_osrm = self.router_widget.router == RouterType.OSRM
        # is_osrm_forbidden_endpoint = menu_index in (1, 3) and is_osrm

        # # disable a few widgets
        # self.routing_params_widget.exclude_locations.setEnabled(not is_osrm)
        # self.routing_params_widget.exclude_polygons.setEnabled(not is_osrm)
        # self.routing_params_widget.ui_settings_stacked.setEnabled(not is_osrm)
        # self.routing_params_widget.ui_metric_box.setEnabled(not is_osrm)
        # self.routing_params_widget.ui_reset_settings.setEnabled(not is_osrm)

        # self.waypoints_widget.setEnabled(not is_osrm_forbidden_endpoint)
        # self.ui_valhalla_isochrones_params.setEnabled(not is_osrm_forbidden_endpoint)
        # self.ui_valhalla_expansion_params.setEnabled(not is_osrm_forbidden_endpoint)
        # self.execute_btn.setEnabled(not is_osrm_forbidden_endpoint)

        # # update their tooltips
        # tooltip = "Methods Isochrones and Expansion not available with OSRM"
        # self.waypoints_widget.setToolTip(tooltip if is_osrm_forbidden_endpoint else "")
        # self.execute_btn.setToolTip(tooltip if is_osrm_forbidden_endpoint else "")
        # self.ui_valhalla_isochrones_params.setToolTip(tooltip if is_osrm_forbidden_endpoint else "")
        # self.ui_valhalla_expansion_params.setToolTip(tooltip if is_osrm_forbidden_endpoint else "")

        if menu_index == 0:
            # self.ui_endpoint_label.setText("Routing")
            self.setWindowTitle("Valhalla - Routing")
        elif menu_index == 1:
            # self.ui_endpoint_label.setText("Isochrones")
            self.setWindowTitle("Valhalla - Isochrones")
        elif menu_index == 2:
            # self.ui_endpoint_label.setText("Matrix")
            self.setWindowTitle("Valhalla - Matrix")
        elif menu_index == 3:
            # self.ui_endpoint_label.setText("Expansion")
            self.setWindowTitle("Valhalla - Expansion")

    def _on_about_click(self):
        about = AboutDialog(self)
        if exc_msg := about.exception_msg:
            self.status_bar.pushWarning("Failed /status request", exc_msg)
        about.exec()

    def _on_log_click(self):
        if not self.factory.url or not self.log_params:
            self.status_bar.pushMessage("Nothing happened yet:)", Qgis.MessageLevel.Warning, 3)
            return

        msg_box = QMessageBox()
        msg_box.setWindowTitle(f"Last {self.endpoint.lower()} request")
        msg_box.setText(self.factory.url)
        msg_box.setDetailedText(json.dumps(self.log_params, indent=2))
        edit_box = msg_box.findChild(QTextEdit)
        edit_box.setFixedHeight(edit_box.height() + 300)

        # show the details (i.e. request params) by default
        for btn in msg_box.buttons():
            if msg_box.buttonRole(btn) == QMessageBox.ActionRole:
                btn.click()

        msg_box.exec()

    def _on_provider_changed(self, row_id: int):
        """
        Enables/disables certain UI elements depending on the provider.
        """
        # updates the profile tool buttons (OSRM only gets foot/bike/car for now)
        self.router_widget.update_profile_buttons()
        # disables/enables other widgets in this dialog
        self._on_router_or_menu_change(self.menu_widget.currentRow())

        router_type = self.router_widget.router
        method = self.router_widget.method
        profile = self.router_widget.profile
        pkg_path = ""
        provider: ProviderSetting = self.router_widget.provider
        if method == RouterMethod.LOCAL:
            try:
                if router_type == RouterType.VALHALLA:
                    import valhalla  # noqa: F401
                elif router_type == RouterType.OSRM:
                    import osrm  # type: ignore # noqa: F401
                pkg_name = self.router_widget.ui_cmb_prov.itemData(row_id)[2]
                pkg_path = get_graph_dir(router_type) / pkg_name
            except (ImportError, ModuleNotFoundError) as e:
                self.status_bar.pushMessage("Python package not installed", str(e), Qgis.Critical, 8)
                return

        # reset the factory
        self.factory = ResultsFactory(router_type, method, profile, pkg_path=pkg_path, url=provider.url)

    def _on_graph_click(self):
        curr_prov: ProviderSetting = self.router_widget.ui_cmb_prov.currentData()[-1]
        if curr_prov.url == DEFAULT_PROVIDERS[0].url:
            self.status_bar.pushInfo(
                "No worries", "The public server has the full world graph and admins/timezones loaded"
            )
            return

        try:
            result = get_status_response(self.router_widget.provider.url, True)
            if not result.get("bbox"):
                raise Exception(
                    "Can't retrieve graph extent, the server doesn't allow it, see https://valhalla.github.io/valhalla/api/status/api-reference/."
                )
        except Exception as e:
            self.status_bar.pushCritical("Failed /status request", str(e))
            return

        msg_missing_dbs: List[str] = []
        if not result["has_admins"]:
            msg_missing_dbs.append("Admin DB is missing from graph, expect wrong driving side.")
        if not result["has_timezones"]:
            msg_missing_dbs.append(
                "Timezones DB is missing from graph, expect non-functional time-dependent settings."
            )
        if msg_missing_dbs:
            self.status_bar.pushWarning("Missing DB(s)", "\n".join(msg_missing_dbs))
        else:
            self.status_bar.pushInfo(
                "DB(s) exist", "Both admin areas and timezones are built into the graph."
            )

        # add the graph extent layer
        lyr_name = f"{curr_prov.name} - Valhalla Graph Extent"
        if QgsProject.instance().mapLayersByName(lyr_name):
            self.status_bar.pushInfo(
                "Layer exists", f"Graph extents layer '{lyr_name}' already exists, skipping..."
            )
            return

        extent_lyr = QgsVectorLayer("Polygon?crs=EPSG:4326", lyr_name, "memory")
        feat = QgsFeature(QgsFields())
        feat.setGeometry(
            QgsGeometry.fromPolygonXY(
                [
                    [
                        QgsPointXY(lon, lat)
                        for lon, lat in result["bbox"]["features"][0]["geometry"]["coordinates"][0]
                    ]
                ]
            )
        )
        extent_lyr.dataProvider().addFeature(feat)
        extent_lyr.updateExtents()
        extent_lyr.loadNamedStyle(str(get_resource_path("styles", "graph_extent.qml")))
        QgsProject.instance().addMapLayer(extent_lyr, True)

    def _on_profile_change(self):
        for ui_enum, profile_enum in PROFILE_TO_UI.items():
            btn: QToolButton = getattr(self.router_widget, ui_enum.value)
            if btn.isChecked():
                self.routing_params_widget.set_current_costing_widget(profile_enum)
                return
