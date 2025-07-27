from pathlib import Path
from typing import Optional

from qgis.core import (
    QgsExpression,
    QgsFeature,
    QgsFeatureRequest,
    QgsField,
    QgsFields,
    QgsGeometry,
    QgsPoint,
    QgsProcessing,
    QgsProcessingAlgorithm,
    QgsProcessingException,
    QgsProcessingFeatureSource,
    QgsProcessingParameterBoolean,
    QgsProcessingParameterDefinition,
    QgsProcessingParameterEnum,
    QgsProcessingParameterFeatureSink,
    QgsProcessingParameterFeatureSource,
    QgsProcessingParameterField,
    QgsProcessingParameterNumber,
    QgsWkbTypes,
)
from qgis.PyQt.QtCore import QCoreApplication, QVariant
from qgis.PyQt.QtGui import QIcon

from valhalla.global_definitions import FieldNames, SpOptTypes
from valhalla.processing.processing_definitions import HELP_DIR
from valhalla.utils.geom_utils import WGS84
from valhalla.utils.misc_utils import wrap_in_html_tag
from valhalla.utils.resource_utils import get_icon


class SPOPTBaseAlgorithm(QgsProcessingAlgorithm):
    """The base class for the spatial optimization problems implemented in Pysal's Spopt package."""

    METRICS = (FieldNames.DURATION, FieldNames.DISTANCE)

    IN_MATRIX_SOURCE = "INPUT_MATRIX_LAYER"
    IN_FAC_SOURCE = "INPUT_FAC_LAYER"
    IN_FAC_ID = "INPUT_FAC_ID"
    IN_PREDEFINED_FAC_FIELD = (
        "INPUT_PREDEFINED_FAC_FIELD"  # TODO: rename proc params for user friendliness
    )
    IN_DEM_SOURCE = "INPUT_DEM_POINT_LAYER"
    IN_DEM_ID = "INPUT_DEM_ID"
    IN_DEM_WEIGHTS = "INPUT_DEM_WEIGHTS"
    IN_SERVICE_RADIUS = "INPUT_SERVICE_RADIUS"
    IN_N_FAC = "INPUT_N_FAC"

    IN_METRIC = "INPUT_METRIC"
    IN_LINES = "INPUT_LINES"

    OUT_FAC = "OUTPUT_FAC"
    OUT_DEM = "OUTPUT_DEM"

    GROUP_NAME = "Spatial Optimization"

    def __init__(self, problem_type: SpOptTypes):
        super(SPOPTBaseAlgorithm, self).__init__()
        self.problem_type = problem_type  # dictates parameters and processAlgorithm method

    def initAlgorithm(self, configuration, p_str=None, Any=None, *args, **kwargs):
        """Here, we use the spopt type to infer the allowed parameters."""
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                name=self.IN_MATRIX_SOURCE,
                description=f"{wrap_in_html_tag('Origin Destination Matrix', 'b')}. "
                "The Origin-Destination Matrix as a table layer.",
                types=[QgsProcessing.TypeVector],
            )
        )
        if self.problem_type in (SpOptTypes.LSCP, SpOptTypes.MCLP):
            self.addParameter(
                QgsProcessingParameterNumber(
                    name=self.IN_SERVICE_RADIUS,
                    description="Service Radius",
                    type=QgsProcessingParameterNumber.Double,
                    minValue=0,
                )
            )

        self.addParameter(
            QgsProcessingParameterFeatureSource(
                name=self.IN_FAC_SOURCE,
                description="The candidate facilities layer.",
                types=[QgsProcessing.TypeVectorPoint],
                optional=True,
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                name=self.IN_FAC_ID,
                description="Facility layer ID field.",
                parentLayerParameterName=self.IN_FAC_SOURCE,
                optional=True,
            )
        )
        if self.problem_type in (SpOptTypes.LSCP, SpOptTypes.MCLP):
            self.addParameter(
                QgsProcessingParameterField(
                    name=self.IN_PREDEFINED_FAC_FIELD,
                    description="Facility layer field indicating if a facility will be used definitively.",
                    parentLayerParameterName=self.IN_FAC_SOURCE,
                    optional=True,
                    type=QgsProcessingParameterField.Numeric,
                )
            )

        self.addParameter(
            QgsProcessingParameterFeatureSource(
                name=self.IN_DEM_SOURCE,
                description="The demand points layer.",
                types=[QgsProcessing.TypeVectorPoint],
                optional=True,
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                name=self.IN_DEM_ID,
                description="Demand points layer ID field.",
                parentLayerParameterName=self.IN_DEM_SOURCE,
                optional=True,
            )
        )

        if self.problem_type in (SpOptTypes.MCLP, SpOptTypes.PMEDIAN):
            self.addParameter(
                QgsProcessingParameterField(
                    name=self.IN_DEM_WEIGHTS,
                    description="Demand point weights",
                    parentLayerParameterName=self.IN_DEM_SOURCE,
                    optional=True,
                    type=QgsProcessingParameterField.Numeric,
                )
            )

        if self.problem_type != SpOptTypes.LSCP:
            self.addParameter(
                QgsProcessingParameterNumber(
                    name=self.IN_N_FAC,
                    description="Number of facilities to be sited",
                    type=QgsProcessingParameterNumber.Integer,
                    minValue=1,
                    defaultValue=1,
                )
            )

        metric_param = QgsProcessingParameterEnum(
            name=self.IN_METRIC,
            description="The metric to use as basis for the optimization",
            options=self.METRICS,
            defaultValue=FieldNames.DURATION,
        )
        # We assume users are more interested in the durations than the distances, so we hide this option in the advanced section
        metric_param.setFlags(QgsProcessingParameterDefinition.FlagAdvanced)

        self.addParameter(metric_param)

        lines_param = QgsProcessingParameterBoolean(
            name=self.IN_LINES,
            description="Draw lines connecting demand points and their respective facilities",
            defaultValue=False,
        )

        lines_param.setFlags(lines_param.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        self.addParameter(lines_param)

        # Only output facilities that are actually selected
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                name=self.OUT_FAC,
                description="Selected facilities",
                createByDefault=True,
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSink(
                name=self.OUT_DEM, description="Demand points", createByDefault=True
            )
        )

    def processAlgorithm(self, parameters, context, feedback):  # noqa: C901

        try:
            import numpy as np
            from pulp import PULP_CBC_CMD

            if self.problem_type == SpOptTypes.LSCP:
                from spopt.locate import LSCP
            if self.problem_type == SpOptTypes.MCLP:
                from spopt.locate import MCLP
            if self.problem_type == SpOptTypes.PCENTER:
                from spopt.locate import PCenter
            if self.problem_type == SpOptTypes.PMEDIAN:
                from spopt.locate import PMedian

        except ImportError as e:
            raise QgsProcessingException(
                self.tr(
                    f"Failed to import library {e.name}. Please open the Valhalla Settings to help you install this package via PyPI."
                )
            )

        # initialize variables that don't exist across all algorithms
        fac_predefined_field: Optional[str] = None
        dem_weight_field: Optional[str] = None
        service_radius: Optional[float] = None
        n_fac: Optional[int] = None

        # Get the parameters that can be specified for all spopt types
        od_matrix: QgsProcessingFeatureSource = self.parameterAsSource(
            parameters, self.IN_MATRIX_SOURCE, context
        )
        fac_source: QgsProcessingFeatureSource = self.parameterAsSource(
            parameters, self.IN_FAC_SOURCE, context
        )
        fac_id_field: Optional[str] = self.parameterAsString(parameters, self.IN_FAC_ID, context)
        dem_source: QgsProcessingFeatureSource = self.parameterAsSource(
            parameters, self.IN_DEM_SOURCE, context
        )
        dem_id_field: Optional[str] = self.parameterAsString(parameters, self.IN_DEM_ID, context)

        metric: str = self.METRICS[self.parameterAsEnum(parameters, self.IN_METRIC, context)]

        draw_lines: bool = self.parameterAsBool(parameters, self.IN_LINES, context)

        # And here we get the params specific to some, but not all spopt types
        if self.problem_type in (SpOptTypes.LSCP, SpOptTypes.MCLP):
            fac_predefined_field = self.parameterAsString(
                parameters, self.IN_PREDEFINED_FAC_FIELD, context
            )
            service_radius = self.parameterAsDouble(parameters, self.IN_SERVICE_RADIUS, context)

        if self.problem_type in (SpOptTypes.MCLP, SpOptTypes.PMEDIAN):
            dem_weight_field = self.parameterAsString(parameters, self.IN_DEM_WEIGHTS, context)

        if self.problem_type != SpOptTypes.LSCP:
            n_fac = self.parameterAsInt(parameters, self.IN_N_FAC, context)

        # build the return fields and get the feature sinks
        fac_return_fields = QgsFields()
        fac_id_type = (  # we pass the type of the ID field on if it's specified by the user
            fac_source.fields().field(fac_id_field).type() if fac_id_field else QVariant.Int
        )
        fac_fields = [QgsField(FieldNames.ID, fac_id_type)]

        if fac_predefined_field:
            fac_fields.append(
                QgsField("predefined", QVariant.Int)
            )  # we pass the predefined field on if specified
        for field in fac_fields:
            fac_return_fields.append(field)

        dem_id_type = (  # we pass the type of the ID field on if it's specified by the user
            dem_source.fields().field(dem_id_field).type() if dem_id_field else QVariant.Int
        )
        dem_return_fields = QgsFields()
        _ = [
            dem_return_fields.append(f)
            for f in (
                QgsField(FieldNames.ID, dem_id_type),
                QgsField(FieldNames.FACILITY_ID, fac_id_type),
            )
        ]

        if dem_weight_field:  # pass the weight field on if specified
            dem_return_fields.append(QgsField(FieldNames.WEIGHT, QVariant.Double))

        (fac_sink, fac_dest_id) = self.parameterAsSink(
            parameters,
            self.OUT_FAC,
            context,
            fac_return_fields,
            fac_source.wkbType()
            if fac_id_field
            else QgsWkbTypes.NoGeometry,  # if there's an ID field, we retrieve the original geometry
            fac_source.sourceCrs() if fac_source and fac_id_field else WGS84,
        )

        dem_geom_type = QgsWkbTypes.NoGeometry

        if dem_id_field:
            dem_geom_type = dem_source.wkbType()

        if draw_lines:
            dem_geom_type = QgsWkbTypes.LineString
            if not dem_id_field and not fac_id_field:
                raise QgsProcessingException(
                    "No connecting lines can be drawn if facility and demand point ID fields are not specified."
                )

        (dem_sink, dem_dest_id) = self.parameterAsSink(
            parameters,
            self.OUT_DEM,
            context,
            dem_return_fields,
            dem_geom_type,
            dem_source.sourceCrs() if dem_source and dem_id_field else WGS84,
        )

        spopt_in_matrix = []

        # get the unique sorted source and target ids from the matrix
        unique_source_ids = sorted(od_matrix.uniqueValues(od_matrix.fields().indexOf(FieldNames.SOURCE)))
        unique_target_ids = sorted(od_matrix.uniqueValues(od_matrix.fields().indexOf(FieldNames.TARGET)))

        if n_fac:
            if len(unique_target_ids) < n_fac:
                raise QgsProcessingException(
                    f"Cannot site {n_fac} facilities, since there are only {len(unique_target_ids)} available."
                )

        # we build the input matrix for the SPOPT classes' from_cost_matrix methods
        for target_id in unique_target_ids:
            # for each target (demand point), we add an empty array to our matrix and populate it with
            # the metric [duration/distance] to each source (facility)
            spopt_in_matrix.append([])
            exp = QgsExpression(
                self.get_expression_template(dem_id_type).format(
                    field=FieldNames.TARGET, value=target_id
                )
            )
            req = QgsFeatureRequest(exp)
            req.addOrderBy(FieldNames.SOURCE, ascending=True)
            for fac_feat in od_matrix.getFeatures(req):
                spopt_in_matrix[-1].append(fac_feat[metric])
        spopt_in_matrix = np.array(spopt_in_matrix)

        predefined_arr = []
        if self.problem_type in (SpOptTypes.LSCP, SpOptTypes.MCLP):
            if fac_predefined_field:
                if not dem_id_field:
                    raise QgsProcessingException(
                        "The predefined field can not be used if no id field is specified for the demand points."
                    )
                req = QgsFeatureRequest()
                req.addOrderBy(fac_id_field)
                for fac_feat in fac_source.getFeatures(req):
                    predefined_arr.append(fac_feat[fac_predefined_field])

        predefined_arr = (
            np.array(predefined_arr) if predefined_arr else None
        )  # need to convert to numpy array for spopt

        weights_arr = []
        if self.problem_type in (SpOptTypes.MCLP, SpOptTypes.PMEDIAN):
            if dem_weight_field:
                if not dem_id_field:
                    raise QgsProcessingException(
                        "The weight field can not be used if no id field is specified for the demand points."
                    )
                req = QgsFeatureRequest()
                req.addOrderBy(dem_id_field)
                for dem_feat in dem_source.getFeatures(req):
                    weights_arr.append(dem_feat[dem_weight_field])
            weights_arr = (
                np.array(weights_arr) if len(weights_arr) > 0 else [1 for i in spopt_in_matrix]
            )  # assign uniform weights if no weights are specified

        try:
            if self.problem_type == SpOptTypes.LSCP:
                problem = LSCP.from_cost_matrix(
                    spopt_in_matrix,
                    service_radius=service_radius,
                    predefined_facilities_arr=predefined_arr,
                )
            if self.problem_type == SpOptTypes.MCLP:
                problem = MCLP.from_cost_matrix(
                    spopt_in_matrix,
                    weights=weights_arr,
                    service_radius=service_radius,
                    p_facilities=n_fac,
                    predefined_facilities_arr=predefined_arr,
                )
            if self.problem_type == SpOptTypes.PCENTER:
                problem = PCenter.from_cost_matrix(spopt_in_matrix, p_facilities=n_fac)
            if self.problem_type == SpOptTypes.PMEDIAN:
                problem = PMedian.from_cost_matrix(
                    spopt_in_matrix,
                    weights=weights_arr,
                    p_facilities=n_fac,
                )

            problem.solve(PULP_CBC_CMD(msg=False))

        except RuntimeError as e:
            raise QgsProcessingException(f"Could not solve {self.NAME}: {e}")

        problem.client_facility_array()  # this creates the fac2cli attribute

        for fac_i in range(len(problem.fac2cli)):
            # now we join the optimization result with the input IDs from the OD matrix using the indices
            if len(problem.fac2cli[fac_i]) > 0:
                fac_feat = QgsFeature()
                fac_feat.setFields(fac_return_fields)
                fac_id = unique_source_ids[fac_i]
                fac_feat[FieldNames.ID] = fac_id
                if fac_predefined_field:  # join the predefined field if provided
                    fac_feat[FieldNames.PREDEFINED] = int(predefined_arr[fac_i])
                if fac_id_field:
                    # if the ID field for the facilities layer was provided, we use it to also
                    # pass through the geometry
                    exp = QgsExpression(
                        self.get_expression_template(fac_id_type).format(
                            field=fac_id_field, value=fac_id
                        )
                    )
                    req = QgsFeatureRequest(exp)
                    geom = [f for f in fac_source.getFeatures(req)][0].geometry()
                    fac_feat.setGeometry(geom)
                fac_sink.addFeature(fac_feat)
                for dem_i in range(len(problem.fac2cli[fac_i])):
                    #  same for the demand points: join using indices, pass the ID and the corresponding facility ID
                    dem_feat = QgsFeature()
                    dem_feat.setFields(dem_return_fields)
                    dem_id = unique_target_ids[problem.fac2cli[fac_i][dem_i]]
                    dem_feat[FieldNames.ID] = dem_id
                    dem_feat[FieldNames.FACILITY_ID] = unique_source_ids[fac_i]
                    if (
                        dem_id_field
                    ):  # and pass through the original geometry via joining with the provided ID field
                        exp = QgsExpression(
                            self.get_expression_template(dem_id_type).format(
                                field=dem_id_field, value=dem_id
                            )
                        )
                        req = QgsFeatureRequest(exp)
                        dem_source_feat = [f for f in dem_source.getFeatures(req)][0]
                        if not draw_lines:
                            dem_geom = dem_source_feat.geometry()
                            dem_feat.setGeometry(dem_geom)
                        elif draw_lines:
                            dem_geom = QgsPoint(dem_source_feat.geometry().asPoint())
                            fac_geom = QgsPoint(fac_feat.geometry().asPoint())
                            line_geom = QgsGeometry.fromPolyline([dem_geom, fac_geom])
                            dem_feat.setGeometry(line_geom)
                        if dem_weight_field:
                            dem_feat[FieldNames.WEIGHT] = dem_source_feat[dem_weight_field]

                    dem_sink.addFeature(dem_feat)

        return {self.OUT_FAC: fac_dest_id, self.OUT_DEM: dem_dest_id}

    @classmethod
    def get_expression_template(cls, value_type: QVariant.Type):
        """Gets a string for a QgsExpression that either checks value equality quoted or unquoted, depending on the given value type."""
        return "\"{field}\"='{value}'" if value_type == QVariant.String else '"{field}"={value}'

    def tr(self, string):
        """
        Returns a translatable string with the self.tr() function.
        """
        return QCoreApplication.translate("Processing", string)

    def createInstance(self):
        return type(self)()

    def group(self) -> str:
        return self.GROUP_NAME

    def groupId(self):
        return self.GROUP_NAME.lower().replace("_", " ")

    def icon(self) -> QIcon:
        return get_icon("icon_matrix.png")

    def name(self):
        return self.NAME

    def displayName(self):
        return "Location Set Covering Problem"

    def shortHelpString(self):
        """Displays the sidebar help in the algorithm window"""

        file = HELP_DIR / Path(f"{self.NAME}.help")

        with open(file) as fh:
            msg = fh.read()

        return msg
