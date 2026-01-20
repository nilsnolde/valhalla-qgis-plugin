from typing import Optional, Union

from qgis.core import (
    QgsField,
    QgsFields,
    QgsProcessing,
    QgsProcessingException,
)
from qgis.PyQt.QtCore import QVariant

from ....core.results_factory import DEFAULT_LAYER_FIELDS
from ....global_definitions import (
    FieldNames,
    RouterEndpoint,
    RouterProfile,
    RouterType,
)
from ....third_party.routingpy import routingpy
from ....utils.layer_utils import (
    get_wgs_coords_from_feature,
    get_wgs_coords_from_layer,
)
from ...routing.base_algorithm import (
    ValhallaBaseAlgorithm,
)


class MapMatchBase(ValhallaBaseAlgorithm):
    IN_1_TYPES = [QgsProcessing.TypeVectorLine]

    def __init__(
        self,
        profile: Optional[Union[RouterProfile, str]] = None,
    ):
        super(MapMatchBase, self).__init__(
            provider=RouterType.VALHALLA,
            endpoint=RouterEndpoint.MAP_MATCH,
            profile=profile,
        )

    def group(self):
        return "Map Match"

    def groupId(self):
        return "valhalla_map_match"

    def initAlgorithm(self, configuration, p_str=None, Any=None, *args, **kwargs):
        self.init_base_params()

    def processAlgorithm(self, parameters, context, feedback):  # noqa: C901
        (
            layer_1,
            layer_field_name_1,
            params,
            results_factory,
        ) = self.get_base_params(parameters, context)

        params["narrative"] = False

        return_fields = QgsFields()
        layer_1_field_type = QVariant.Int

        field_list = []
        if layer_field_name_1:
            layer_1_field_type = layer_1.fields().field(layer_field_name_1).type()
        field_list.append(QgsField(FieldNames.ID, layer_1_field_type))

        for field in (f for f in (*field_list, *DEFAULT_LAYER_FIELDS[self.endpoint])):
            return_fields.append(field)

        total_count = layer_1.featureCount()

        # For a LineString layer, we want one match per feature layer
        sink, dest_id = self.get_feature_sink(parameters, context, return_fields)
        coords = get_wgs_coords_from_layer(layer_1)

        for count, feature in enumerate(layer_1.getFeatures()):
            coords = get_wgs_coords_from_feature(feature, layer_1.sourceCrs())

            if feedback.isCanceled():
                break
            try:
                for ix, result_feat in enumerate(
                    results_factory.get_results(self.endpoint, coords, params, return_fields)
                ):
                    result_feat[FieldNames.ID] = ix
                    sink.addFeature(result_feat)
                    feedback.setProgress(int((count + 1) / total_count * 100))
            except (
                routingpy.exceptions.RouterApiError,
                routingpy.exceptions.RouterServerError,
            ) as e:
                raise QgsProcessingException(f"HTTP {e.status}: {e.message}")
        return {self.OUT: dest_id}


class ValhallaMapMatchCar(MapMatchBase):
    def __init__(self):
        super(ValhallaMapMatchCar, self).__init__(profile=RouterProfile.CAR)


class ValhallaMapMatchTruck(MapMatchBase):
    def __init__(self):
        super(ValhallaMapMatchTruck, self).__init__(profile=RouterProfile.TRUCK)


class ValhallaMapMatchMotorcycle(MapMatchBase):
    def __init__(self):
        super(ValhallaMapMatchMotorcycle, self).__init__(profile=RouterProfile.MBIKE)


class ValhallaMapMatchPedestrian(MapMatchBase):
    def __init__(self):
        super(ValhallaMapMatchPedestrian, self).__init__(profile=RouterProfile.PED)


class ValhallaMapMatchBicycle(MapMatchBase):
    def __init__(self):
        super(ValhallaMapMatchBicycle, self).__init__(profile=RouterProfile.BIKE)
