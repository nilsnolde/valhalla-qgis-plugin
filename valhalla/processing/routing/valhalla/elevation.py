from qgis.core import (
    QgsField,
    QgsFields,
    QgsProcessingException,
)
from qgis.PyQt.QtCore import QVariant

from ....global_definitions import (
    DEFAULT_LAYER_FIELDS,
    FieldNames,
    RouterEndpoint,
    RouterType,
)
from ....third_party.routingpy import routingpy
from ....utils.layer_utils import get_wgs_coords_from_feature
from ...routing.base_algorithm import (
    ValhallaBaseAlgorithm,
)


class ValhallaElevation(ValhallaBaseAlgorithm):
    WITH_COSTING_OPTIONS = False

    def __init__(self):
        super(ValhallaElevation, self).__init__(
            provider=RouterType.VALHALLA, endpoint=RouterEndpoint.ELEVATION
        )

    def initAlgorithm(self, configuration, p_str=None, Any=None, *args, **kwargs):
        self.init_base_params()

    def processAlgorithm(self, parameters, context, feedback):
        (
            layer_1,
            layer_field_name_1,
            params,
            results_factory,
        ) = self.get_base_params(parameters, context)

        return_fields = QgsFields()
        id_field_type = QVariant.Int
        if layer_field_name_1:
            id_field_type = layer_1.fields().field(layer_field_name_1).type()

        for field in (
            f
            for f in (
                QgsField(FieldNames.ID, id_field_type),
                *DEFAULT_LAYER_FIELDS[self.endpoint],
            )
        ):
            return_fields.append(field)

        sink, dest_id = self.get_feature_sink(parameters, context, return_fields)

        locations = []
        for feature in layer_1.getFeatures():
            coords = get_wgs_coords_from_feature(feature, layer_1.sourceCrs())
            locations.append(coords)

        try:
            for idx, result_feat in enumerate(
                results_factory.get_results(self.endpoint, locations, params, return_fields)
            ):
                result_feat[FieldNames.ID] = idx
                sink.addFeature(result_feat)
        except (
            routingpy.exceptions.RouterApiError,
            routingpy.exceptions.RouterServerError,
        ) as e:
            raise QgsProcessingException(f"HTTP {e.status}: {e.message}")

        return {self.OUT: dest_id}
