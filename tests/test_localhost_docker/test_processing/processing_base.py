import shutil
from typing import List, Tuple

from qgis.core import (
    QgsFeature,
    QgsField,
    QgsFields,
    QgsLineString,
    QgsMultiPoint,
    QgsPoint,
    QgsPolygon,
    QgsProcessingAlgorithm,
    QgsProcessingContext,
    QgsProcessingFeedback,
    QgsProcessingOutputLayerDefinition,
    QgsProcessingUtils,
    QgsVectorLayer,
    QgsWkbTypes,
)
from qgis.PyQt.QtCore import QVariant
from qvalhalla import BASE_DIR
from qvalhalla.core.settings import get_settings_dir

from ... import LocalhostDockerTestCase
from ...constants import GRAPHS, POLYGON_4326, WAYPOINTS_4326


class ProcessingBase(LocalhostDockerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # copy the graphs if necessary
        for router, fname in GRAPHS:
            out_fp = get_settings_dir().joinpath(fname)
            if not out_fp.exists():
                shutil.copy2(BASE_DIR.parent.joinpath("tests", "data", fname), out_fp)

        layer_fields = QgsFields()
        layer_fields.append(QgsField("ID", QVariant.Int))
        layer_fields.append(QgsField("ID_str", QVariant.String))

        # single point layer
        cls.layer_1 = QgsVectorLayer(
            f"{QgsWkbTypes.displayString(QgsWkbTypes.Point)}",
            "layer_1",
            "memory",
        )

        cls.layer_1.dataProvider().addAttributes(layer_fields)
        cls.layer_1.updateFields()

        for i, coords in enumerate(WAYPOINTS_4326):
            feat = QgsFeature()
            geom = QgsPoint(*coords)
            feat.setGeometry(geom)
            feat.setAttributes([i, str(i)])
            cls.layer_1.dataProvider().addFeature(feat)

        # another single point layer
        cls.layer_2 = QgsVectorLayer(
            f"{QgsWkbTypes.displayString(QgsWkbTypes.Point)}",
            "layer_2",
            "memory",
        )

        cls.layer_2.dataProvider().addAttributes(layer_fields)
        cls.layer_2.updateFields()

        for i, coords in enumerate(reversed(WAYPOINTS_4326)):
            feat = QgsFeature()
            geom = QgsPoint(*coords)
            feat.setGeometry(geom)
            feat.setAttributes([i, str(i)])
            cls.layer_2.dataProvider().addFeature(feat)

        # multipoint layer
        cls.layer_mp = QgsVectorLayer(
            f"{QgsWkbTypes.displayString(QgsWkbTypes.MultiPoint)}",
            "layer_mp",
            "memory",
        )

        cls.layer_mp.dataProvider().addAttributes(layer_fields)
        cls.layer_mp.updateFields()

        for ix, waypoints in enumerate((WAYPOINTS_4326[0:2], WAYPOINTS_4326[1:])):
            feat = QgsFeature()
            multipoint = QgsMultiPoint()
            points = [QgsPoint(*coord) for coord in waypoints]
            _ = [multipoint.addGeometry(point) for point in points]
            feat.setGeometry(multipoint)
            feat.setAttributes([ix, str(ix)])
            cls.layer_mp.dataProvider().addFeature(feat)

        cls.avoid_polygon_layer = QgsVectorLayer(
            f"{QgsWkbTypes.displayString(QgsWkbTypes.Polygon)}",
            "layer_avoid_polygon",
            "memory",
        )

        feat = QgsFeature()
        feat.setGeometry(QgsPolygon(QgsLineString([QgsPoint(*coord) for coord in POLYGON_4326[0]])))
        cls.avoid_polygon_layer.dataProvider().addFeature(feat)

    def run_routing_algorithm(
        self, alg: QgsProcessingAlgorithm, params: dict
    ) -> Tuple[List[QgsFeature], List[float]]:
        """Prepares and runs the algorithm, then returns the list of features"""
        progress_changed_vals = []

        # always request to localhost
        params["INPUT_PROVIDER"] = 1

        def on_progress_changed(progress: float):
            nonlocal progress_changed_vals  # noqa: F824
            progress_changed_vals.append(progress)

        alg.initAlgorithm({})
        ctx = QgsProcessingContext()
        feedback = QgsProcessingFeedback()
        feedback.progressChanged.connect(on_progress_changed)

        # handle the output properly
        out_param = QgsProcessingOutputLayerDefinition("TEMPORARY_OUTPUT")
        out_param.createOptions = {"fileEncoding": "System"}
        params[alg.OUT] = out_param

        alg.prepareAlgorithm(params, ctx, feedback)
        layer_id = alg.processAlgorithm(params, ctx, feedback)[alg.OUT]

        return (
            list(QgsProcessingUtils.mapLayerFromString(layer_id, ctx).getFeatures()),
            progress_changed_vals,
        )

    def run_spopt_algorithm(self, alg: QgsProcessingAlgorithm, params: dict) -> Tuple:

        # The SpOpt algorithms have different outputs than the routing ones, so I created a separate
        # method for calling them
        alg.initAlgorithm({})
        ctx = QgsProcessingContext()
        feedback = QgsProcessingFeedback()

        out_param_fac = QgsProcessingOutputLayerDefinition("TEMPORARY_OUTPUT")
        out_param_dem = QgsProcessingOutputLayerDefinition("TEMPORARY_OUTPUT")
        out_param_fac.createOptions = {"fileEncoding": "System"}
        out_param_dem.createOptions = {"fileEncoding": "System"}
        params[alg.OUT_FAC] = out_param_fac
        params[alg.OUT_DEM] = out_param_dem

        alg.prepareAlgorithm(params, ctx, feedback)
        result_dict = alg.processAlgorithm(params, ctx, feedback)

        fac_layer_id = result_dict[alg.OUT_FAC]
        dem_layer_id = result_dict[alg.OUT_DEM]

        return (
            list(QgsProcessingUtils.mapLayerFromString(fac_layer_id, ctx).getFeatures()),
            QgsProcessingUtils.mapLayerFromString(fac_layer_id, ctx).wkbType(),
            list(QgsProcessingUtils.mapLayerFromString(dem_layer_id, ctx).getFeatures()),
            QgsProcessingUtils.mapLayerFromString(dem_layer_id, ctx).wkbType(),
        )
