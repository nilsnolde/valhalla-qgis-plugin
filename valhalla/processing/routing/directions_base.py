from typing import Callable, Optional, Union

from qgis.core import (
    QgsFeature,
    QgsFeatureRequest,
    QgsField,
    QgsFields,
    QgsProcessing,
    QgsProcessingException,
    QgsProcessingParameterEnum,
    QgsProcessingParameterFeatureSource,
    QgsProcessingParameterField,
    QgsWkbTypes,
)
from qgis.PyQt.QtCore import QVariant

from ...core.results_factory import DEFAULT_LAYER_FIELDS
from ...global_definitions import (
    FieldNames,
    RouterEndpoint,
    RouterProfile,
    RouterType,
)
from ...third_party.routingpy import routingpy
from ...utils.layer_utils import (
    get_wgs_coords_from_feature,
    get_wgs_coords_from_layer,
)
from ...utils.logger_utils import qgis_log
from ...utils.misc_utils import wrap_in_html_tag
from ..processing_definitions import MergeStrategy
from ..routing.base_algorithm import (
    ValhallaBaseAlgorithm,
)


class DirectionsBase(ValhallaBaseAlgorithm):

    IN_ORDER = "INPUT_ORDER"
    IN_2 = "INPUT_LAYER_2"
    IN_FIELD_2 = "INPUT_FIELD_2"
    IN_MERGE_STRATEGY = "INPUT_MERGE_STRATEGY"

    def __init__(
        self,
        provider: Union[RouterType, str],
        profile: Optional[Union[RouterProfile, str]] = None,
    ):
        super(DirectionsBase, self).__init__(
            provider=provider,
            endpoint=RouterEndpoint.DIRECTIONS,
            profile=profile,
        )

    def group(self):
        return "Directions" if self.endpoint == RouterEndpoint.DIRECTIONS else "Optimized Directions"

    def groupId(self):
        return (
            "valhalla_directions"
            if self.endpoint == RouterEndpoint.DIRECTIONS
            else "valhalla_directions_optimized"
        )

    def initAlgorithm(self, configuration, p_str=None, Any=None, *args, **kwargs):
        self.init_base_params(multi_layer=True)

        self.addParameter(
            QgsProcessingParameterField(
                name=self.IN_ORDER,
                description="Sort points by (if one single point layer is provided, this field can be used for determining the route order)",
                parentLayerParameterName=self.IN_1,
                optional=True,
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSource(
                name=self.IN_2,
                description=f"{wrap_in_html_tag('Input point layer 2', 'b')}. "
                "If provided, directions between points in each layer will be computed",
                types=[QgsProcessing.TypeVectorPoint],
                optional=True,
            )
        )
        self.addParameter(
            QgsProcessingParameterField(
                name=self.IN_FIELD_2,
                description="Layer 2 ID Field (can be used for joining)",
                parentLayerParameterName=self.IN_2,
                optional=True,
            )
        )

        self.addParameter(
            QgsProcessingParameterEnum(
                name=self.IN_MERGE_STRATEGY,
                description="The way two layers are handled, if a second layer is provided.",
                options=list(MergeStrategy),
                defaultValue=MergeStrategy.ROW_BY_ROW,
            )
        )

    def processAlgorithm(self, parameters, context, feedback):  # noqa: C901
        (
            layer_1,
            layer_field_name_1,
            params,
            results_factory,
        ) = self.get_base_params(parameters, context)

        if self.router == RouterType.VALHALLA:
            params["instructions"] = False

        order_field = self.parameterAsString(parameters, self.IN_ORDER, context)

        layer_2 = self.parameterAsSource(parameters, self.IN_2, context)
        layer_field_name_2 = self.parameterAsString(parameters, self.IN_FIELD_2, context)

        strategy_val = self.parameterAsEnum(parameters, self.IN_MERGE_STRATEGY, context)
        strategy = list(MergeStrategy)[strategy_val]

        return_fields = QgsFields()
        layer_1_field_type = QVariant.Int
        layer_2_field_type = QVariant.Int

        field_list = []
        if layer_field_name_1:
            layer_1_field_type = layer_1.fields().field(layer_field_name_1).type()
        field_list.append(QgsField(FieldNames.ID, layer_1_field_type))

        if (
            layer_2
        ):  # if we compute between two layers, reset the ID field to source and add a target id field
            field_list[0].setName(FieldNames.SOURCE)
            if layer_field_name_2:
                layer_2_field_type = layer_2.fields().field(layer_field_name_2).type()
            field_list.append(QgsField(FieldNames.TARGET, layer_2_field_type))

        for field in (f for f in (*field_list, *DEFAULT_LAYER_FIELDS[self.endpoint])):
            return_fields.append(field)

        if not layer_2:
            # for MultiPoint layers, we want one route for each MultiPoint
            if QgsWkbTypes.isMultiType(layer_1.wkbType()):
                sink, dest_id = self.get_feature_sink(parameters, context, return_fields)

                total_count = layer_1.featureCount()

                for count, feature in enumerate(layer_1.getFeatures()):
                    if feedback.isCanceled():
                        break

                    coords = get_wgs_coords_from_feature(feature, layer_1.sourceCrs())
                    try:
                        for result_feat in results_factory.get_results(
                            self.endpoint, coords, params, return_fields
                        ):
                            result_feat[FieldNames.ID] = (
                                feature[layer_field_name_1] if layer_field_name_1 else feature.id()
                            )
                            sink.addFeature(result_feat)
                            feedback.setProgress(int((count + 1) / total_count * 100))
                    except (
                        routingpy.exceptions.RouterApiError,
                        routingpy.exceptions.RouterServerError,
                    ) as e:
                        raise QgsProcessingException(f"HTTP {e.status}: {e.message}")
            else:
                # For a SinglePoint layer, we want one route that passes through all features
                sink, dest_id = self.get_feature_sink(parameters, context, return_fields)
                order_by_clause = QgsFeatureRequest()
                if order_field:
                    order_by_clause.addOrderBy(order_field)

                coords = get_wgs_coords_from_layer(layer_1, order_by=order_field)
                try:
                    for ix, result_feat in enumerate(
                        results_factory.get_results(self.endpoint, coords, params, return_fields)
                    ):
                        result_feat[FieldNames.ID] = ix
                        sink.addFeature(result_feat)
                except (
                    routingpy.exceptions.RouterApiError,
                    routingpy.exceptions.RouterServerError,
                ) as e:
                    raise QgsProcessingException(f"HTTP {e.status}: {e.message}")
        else:  # if a second layer is provided
            sink, dest_id = self.get_feature_sink(parameters, context, return_fields)

            join_condition = self.get_join_condition(strategy, layer_field_name_1, layer_field_name_2)

            total_count = sum(
                [join_condition(x, y) for x in layer_1.getFeatures() for y in layer_2.getFeatures()]
            )
            count = 0

            for idx_1, feature_1 in enumerate(layer_1.getFeatures()):
                for idx_2, feature_2 in enumerate(layer_2.getFeatures()):
                    if feedback.isCanceled():
                        break

                    if join_condition(feature_1, feature_2):
                        coords = [
                            get_wgs_coords_from_feature(feature, layer_1.sourceCrs())
                            for feature in (feature_1, feature_2)
                        ]
                        try:
                            for result_feat in results_factory.get_results(
                                self.endpoint, coords, params, return_fields
                            ):
                                result_feat[FieldNames.SOURCE] = (
                                    feature_1[layer_field_name_1]
                                    if layer_field_name_1
                                    else feature_1.id()
                                )
                                result_feat[FieldNames.TARGET] = (
                                    feature_2[layer_field_name_2]
                                    if layer_field_name_2
                                    else feature_2.id()
                                )
                                sink.addFeature(result_feat)
                                count += 1
                                feedback.setProgress(int(count / total_count * 100))
                        except (
                            routingpy.exceptions.RouterApiError,
                            routingpy.exceptions.RouterServerError,
                        ) as e:
                            raise QgsProcessingException(f"HTTP {e.status}: {e.message}")
        return {self.OUT: dest_id}

    @staticmethod
    def get_join_condition(
        merge_strategy: MergeStrategy,
        layer_field_1: Optional[str],
        layer_field_2: Optional[str],
    ) -> Callable[[QgsFeature, QgsFeature], bool]:
        """
        Determines how two layers should be joined and returns a function that can be called with one feature from
        each layer. This prevents having to check the merge strategy and existence of field names for
        each combination of features.
        """
        # if merge strategy is all by all, we want to route between all features
        if merge_strategy == MergeStrategy.ALL_BY_ALL:

            def join_func(a, b):
                return True

        # if layer field names are provided for both layers, use these names as the join condition
        elif merge_strategy == MergeStrategy.ROW_BY_ROW and all((layer_field_1, layer_field_2)):

            def join_func(a, b):
                return a[layer_field_1] == b[layer_field_2]

        # if no layer field names are provided, just join them by their default order
        elif merge_strategy == MergeStrategy.ROW_BY_ROW and not any((layer_field_1, layer_field_2)):

            def join_func(a, b):
                return a.id() == b.id()

        # if only one layer field name has been provided, throw error
        elif merge_strategy == MergeStrategy.ROW_BY_ROW and any((layer_field_1, layer_field_2)):
            msg = f"If the merge strategy is {merge_strategy}, provide either both layer's field names or none at all."
            qgis_log(msg)
            raise QgsProcessingException(msg)

        return join_func
