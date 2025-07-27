from qgis.core import (
    Qgis,
    QgsMapLayerProxyModel,
    QgsProcessingContext,
    QgsProcessingException,
    QgsProcessingFeedback,
    QgsProcessingOutputLayerDefinition,
    QgsProject,
    QgsVectorLayer,
)
from qgis.gui import QgisInterface, QgsFieldComboBox
from qgis.PyQt.QtWidgets import QDialog, QToolButton

from ..core.settings import ValhallaSettings
from ..global_definitions import (
    FieldNames,
    RouterMethod,
    RouterType,
    RoutingMetric,
    SpOptTypes,
)
from ..gui.compiled.dlg_spopt_ui import Ui_SpatialOptimization
from ..processing.routing.osrm.matrix import OSRMMatrix
from ..processing.routing.valhalla.matrix import ValhallaMatrix
from ..processing.spatial_optimization.lscp import LSCPAlgorithm
from ..processing.spatial_optimization.mclp import MCLPAlgorithm
from ..processing.spatial_optimization.pcenter import PCenterAlgorithm
from ..processing.spatial_optimization.pmedian import PMedianAlgorithm
from .dlg_about import AboutDialog
from .gui_utils import add_msg_bar
from .splitter_mixin import SplitterMixin
from .widgets.widget_router import PROFILE_TO_UI, RouterWidget
from .widgets.widget_routing_params import RoutingParamsWidget

MENU_TABS = {
    SpOptTypes.LSCP: "ui_lscp_params",
    SpOptTypes.MCLP: "ui_mclp_params",
    SpOptTypes.PCENTER: "ui_pcenter_params",
    SpOptTypes.PMEDIAN: "ui_pmedian_params",
}

MATRX_ALGO_MAP = {RouterType.OSRM: OSRMMatrix, RouterType.VALHALLA: ValhallaMatrix}

SPOPT_ALGO_MAP = {
    SpOptTypes.LSCP: LSCPAlgorithm,
    SpOptTypes.MCLP: MCLPAlgorithm,
    SpOptTypes.PCENTER: PCenterAlgorithm,
    SpOptTypes.PMEDIAN: PMedianAlgorithm,
}


class SpoptDialog(QDialog, Ui_SpatialOptimization, SplitterMixin):
    def __init__(self, parent=None, iface: QgisInterface = None):
        super().__init__(parent=parent)
        self.setupUi(self)
        SplitterMixin.__init__(self, self.splitter)
        self.iface = iface

        # add a status bar
        self.status_bar = add_msg_bar(self.verticalWrapper)

        self.router_widget = RouterWidget(self)
        self.router_box.layout().addWidget(self.router_widget)
        self.routing_params_widget = RoutingParamsWidget(self, self.iface)
        self.splitterRightLayout.layout().addWidget(self.routing_params_widget)

        self.ui_fac_layer.setFilters(QgsMapLayerProxyModel.PointLayer)
        self.ui_dem_point_layer.setFilters(QgsMapLayerProxyModel.PointLayer)

        self._on_profile_change()

        for fieldCombo in (
            self.ui_fac_id_field,
            self.ui_dem_point_id_field,
            self.ui_mclp_weights,
            self.ui_lscp_predefined,
            self.ui_mclp_predefined,
            self.ui_pmedian_weights,
        ):
            fieldCombo.setAllowEmptyFieldName(True)

        # connections
        self.ui_fac_layer.layerChanged.connect(
            lambda layer: self._on_layer_changed(self.ui_fac_id_field, layer)
        )
        self.ui_fac_layer.layerChanged.connect(self.ui_mclp_predefined.setLayer)
        self.ui_fac_layer.layerChanged.connect(self.ui_lscp_predefined.setLayer)
        self.ui_dem_point_layer.layerChanged.connect(
            lambda layer: self._on_layer_changed(self.ui_dem_point_id_field, layer)
        )
        self.ui_dem_point_layer.layerChanged.connect(self.ui_mclp_weights.setLayer)
        self.ui_dem_point_layer.layerChanged.connect(self.ui_pmedian_weights.setLayer)

        self.ui_fac_layer.layerChanged.emit(self.ui_fac_layer.currentLayer())
        self.ui_dem_point_layer.layerChanged.emit(self.ui_dem_point_layer.currentLayer())

        self.router_widget.ui_cmb_prov.currentIndexChanged.connect(self._on_provider_change)

        self.menu_widget.currentRowChanged["int"].connect(self.ui_params_stacked.setCurrentIndex)
        self.router_widget.mode_btns.buttonToggled.connect(self._on_profile_change)
        self.execute_btn.clicked.connect(self._on_execute)
        self.ui_about_btn.clicked.connect(self._on_about_click)

    def _on_execute(self):
        """
        Runs when the execute button is clicked. Chains two processing algorithms:
          1. The matrix algorithm (either OSRM or Valhalla with respective profile)
          2. The SpOpt algorithm (to which the matrix layer and parameters gathered from the UI are passed)
        """
        ctx = QgsProcessingContext()
        feedback = QgsProcessingFeedback()
        matrix_out_param = QgsProcessingOutputLayerDefinition("TEMPORARY_OUTPUT")

        matrix_algo_class = MATRX_ALGO_MAP[self.router_widget.provider]

        provider = self.router_widget.provider
        method = self.router_widget.method

        profile = self.router_widget.profile
        fac_layer = self.ui_fac_layer.currentLayer()
        fac_id_field = self.ui_fac_id_field.currentField()

        dem_point_layer = self.ui_dem_point_layer.currentLayer()
        dem_point_id_field = self.ui_dem_point_id_field.currentField()

        matrix_params = {
            matrix_algo_class.IN_1: fac_layer,
            matrix_algo_class.IN_FIELD_1: fac_id_field,
            matrix_algo_class.IN_2: dem_point_layer,
            matrix_algo_class.IN_FIELD_2: dem_point_id_field,
            matrix_algo_class.OUT: matrix_out_param,
        }

        if provider == RouterType.OSRM:
            url = ValhallaSettings().get_router_url(provider, profile)
            matrix_algo = matrix_algo_class()

            matrix_params.update({matrix_algo_class.IN_URL: url})
        else:
            matrix_algo = matrix_algo_class(profile=profile)
            additional_params = self.routing_params_widget.get_costing_params()

            # here, we need to rename the global costing params
            if additional_params.get("avoid_locations"):
                additional_params[matrix_algo_class.IN_AVOID_LOCATIONS] = additional_params.pop(
                    "avoid_locations"
                )
            if additional_params.get("avoid_polygons"):
                additional_params[matrix_algo_class.IN_AVOID_POLYGONS] = additional_params.pop(
                    "avoid_polygons"
                )

            if additional_params["options"].get("shortest"):
                # while valhalla expects the shortest option to be in the "options" dict, the processing algo
                # expects it to be in the top level params dict
                additional_params[matrix_algo_class.IN_MODE] = (
                    int(RoutingMetric.SHORTEST)
                    if additional_params["options"].pop("shortest")
                    else int(RoutingMetric.FASTEST)
                )
            matrix_params.update(additional_params)

        matrix_params.update({matrix_algo_class.IN_METHOD: int(method)})

        if method == RouterMethod.LOCAL:
            pkg = self.router_widget.package_path
            matrix_params.update(
                {
                    matrix_algo_class.IN_PKG: matrix_algo.pkgs.index(
                        pkg
                    )  # we need the index since this is an enum param
                }
            )

        matrix_algo.initAlgorithm({})
        matrix_algo.prepareAlgorithm(matrix_params, ctx, feedback)
        layer_id = matrix_algo.processAlgorithm(matrix_params, ctx, feedback)[matrix_algo_class.OUT]
        matrix_layer = ctx.takeResultLayer(layer_id)

        spopt_type = list(SpOptTypes)[self.menu_widget.currentRow()]
        spopt_algo = SPOPT_ALGO_MAP[spopt_type]()

        spopt_out_fac_param = QgsProcessingOutputLayerDefinition("TEMPORARY_OUTPUT")
        spopt_out_dem_param = QgsProcessingOutputLayerDefinition("TEMPORARY_OUTPUT")

        optimization_metric = (
            FieldNames.DURATION if self.ui_metric_duration.isChecked() else FieldNames.DISTANCE
        )

        spopt_params = {
            spopt_algo.IN_MATRIX_SOURCE: matrix_layer,
            spopt_algo.IN_FAC_SOURCE: fac_layer,
            spopt_algo.IN_FAC_ID: fac_id_field,
            spopt_algo.IN_DEM_SOURCE: dem_point_layer,
            spopt_algo.IN_DEM_ID: dem_point_id_field,
            spopt_algo.IN_METRIC: optimization_metric,
            spopt_algo.IN_LINES: self.ui_draw_connecting_lines.isChecked(),
            spopt_algo.OUT_FAC: spopt_out_fac_param,
            spopt_algo.OUT_DEM: spopt_out_dem_param,
            **self.get_spopt_params(spopt_type),
        }

        spopt_algo.initAlgorithm({})
        spopt_algo.prepareAlgorithm(spopt_params, ctx, feedback)
        try:
            out_dict = spopt_algo.processAlgorithm(spopt_params, ctx, feedback)

        except QgsProcessingException as e:
            self.status_bar.pushMessage("Error", str(e), Qgis.Critical, 8)
            return

        out_fac_layer = ctx.takeResultLayer(out_dict[spopt_algo.OUT_FAC])
        out_dem_layer = ctx.takeResultLayer(out_dict[spopt_algo.OUT_DEM])

        QgsProject.instance().addMapLayer(out_fac_layer)
        QgsProject.instance().addMapLayer(out_dem_layer)

        if self.ui_return_matrix.isChecked():
            QgsProject.instance().addMapLayer(matrix_layer)

    def get_spopt_params(self, spopt_type: SpOptTypes):
        if spopt_type == SpOptTypes.LSCP:
            service_radius = self.ui_lscp_service_radius.value()
            predefined_field = self.ui_lscp_predefined.currentField()
            return {
                LSCPAlgorithm.IN_SERVICE_RADIUS: service_radius,
                LSCPAlgorithm.IN_PREDEFINED_FAC_FIELD: predefined_field,
            }

        elif spopt_type == SpOptTypes.MCLP:
            service_radius = self.ui_mclp_service_radius.value()
            n_fac = self.ui_mclp_n_fac.value()
            predefined_field = self.ui_lscp_predefined.currentField()
            dem_weights_field = self.ui_mclp_weights.currentField()

            return {
                MCLPAlgorithm.IN_SERVICE_RADIUS: service_radius,
                MCLPAlgorithm.IN_N_FAC: n_fac,
                MCLPAlgorithm.IN_PREDEFINED_FAC_FIELD: predefined_field,
                MCLPAlgorithm.IN_DEM_WEIGHTS: dem_weights_field,
            }

        if spopt_type == SpOptTypes.PCENTER:
            n_fac = self.ui_pcenter_n_fac.value()
            return {PCenterAlgorithm.IN_N_FAC: n_fac}

        if spopt_type == SpOptTypes.PMEDIAN:
            n_fac = self.ui_pmedian_n_fac.value()
            dem_weights_field = self.ui_pmedian_weights.currentField()
            return {
                PMedianAlgorithm.IN_N_FAC: n_fac,
                PMedianAlgorithm.IN_DEM_WEIGHTS: dem_weights_field,
            }

    @staticmethod
    def _on_about_click():
        about = AboutDialog()
        about.exec()

    @staticmethod
    def _on_layer_changed(field_combo: QgsFieldComboBox, layer: QgsVectorLayer):
        """
        Sets the fieldCombo layer to the passed layer
        and sets the current field to one of [id, ID] if such field exists
        """
        field_combo.setLayer(layer)
        try:
            field_names = [field.name() for field in layer.fields()]
            for id_ in ("id", "ID"):
                if id_ in field_names:
                    field_combo.setField(id_)
        except AttributeError:
            pass

    def _on_provider_change(self, menu_index: int):
        """Disables/enables some widgets if it's OSRM isochrone/expansion"""
        self.router_widget.update_profile_buttons()
        is_osrm = self.router_widget.provider == RouterType.OSRM

        # disable a few widgets
        self.routing_params_widget.exclude_locations.setEnabled(not is_osrm)
        self.routing_params_widget.exclude_polygons.setEnabled(not is_osrm)
        self.routing_params_widget.ui_settings_stacked.setEnabled(not is_osrm)
        self.routing_params_widget.ui_metric_box.setEnabled(not is_osrm)
        self.routing_params_widget.ui_reset_settings.setEnabled(not is_osrm)

    def _on_profile_change(self):
        for ui_enum, profile_enum in PROFILE_TO_UI.items():
            btn: QToolButton = getattr(self.router_widget, ui_enum.value)
            if btn.isChecked():
                self.routing_params_widget.set_current_costing_widget(profile_enum)
                return
