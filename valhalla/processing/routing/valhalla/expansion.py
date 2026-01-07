from typing import Union

from qgis.core import (
    QgsField,
    QgsFields,
    QgsProcessingException,
    QgsProcessingParameterEnum,
    QgsProcessingParameterString,
)
from qgis.PyQt.QtCore import QVariant

from ....global_definitions import (
    DEFAULT_LAYER_FIELDS,
    FieldNames,
    RouterEndpoint,
    RouterProfile,
    RouterType,
)
from ....third_party.routingpy import routingpy
from ....utils.layer_utils import get_wgs_coords_from_feature
from ....utils.logger_utils import qgis_log
from ...routing.base_algorithm import (
    ValhallaBaseAlgorithm,
)


class ValhallaExpansionBase(ValhallaBaseAlgorithm):
    METRICS = {"Time (seconds)": "time", "Distance (meters)": "distance"}

    IN_INTERVALS = "INPUT_INTERVALS"
    IN_METRIC = "INPUT_METRIC"

    def __init__(self, profile: Union[RouterProfile, str]):
        super(ValhallaExpansionBase, self).__init__(
            provider=RouterType.VALHALLA,
            endpoint=RouterEndpoint.EXPANSION,
            profile=RouterProfile(profile),
        )

    def group(self):
        return "Expansion"

    def groupId(self):
        return "valhalla_expansion"

    def initAlgorithm(self, configuration, p_str=None, Any=None, *args, **kwargs):
        self.init_base_params()

        interval_param = QgsProcessingParameterString(self.IN_INTERVALS, "Intervals (comma-separated)")
        interval_param.setHelp("Analogous to isochrone intervals")

        metric_param = QgsProcessingParameterEnum(
            self.IN_METRIC,
            "Metric",
            list(self.METRICS),
            defaultValue=list(self.METRICS.keys())[0],
        )
        metric_param.setHelp("The unit of the specified intervals.")

        for param in (interval_param, metric_param):
            self.addParameter(param)

    def processAlgorithm(self, parameters, context, feedback):
        (
            layer_1,
            layer_field_name_1,
            params,
            results_factory,
        ) = self.get_base_params(parameters, context)

        try:
            params["intervals"] = [
                float(x)
                for x in self.parameterAsString(parameters, self.IN_INTERVALS, context).split(",")
            ]
        except ValueError:
            msg = "Please provide intervals as comma separated values, e.g.: '25, 50'."
            qgis_log(msg)
            raise QgsProcessingException(msg)

        params["expansion_properties"] = ("duration", "distance")
        params["interval_type"] = self.METRICS[
            list(self.METRICS.keys())[self.parameterAsEnum(parameters, self.IN_METRIC, context)]
        ]

        return_fields = QgsFields()
        id_field_type = QVariant.Int
        if layer_field_name_1:
            id_field_type = layer_1.fields().field(layer_field_name_1).type()

        for field in (
            f
            for f in (
                QgsField(FieldNames.LOCATION_ID, id_field_type),
                *DEFAULT_LAYER_FIELDS[self.endpoint],
            )
        ):
            return_fields.append(field)

        sink, dest_id = self.get_feature_sink(parameters, context, return_fields)

        total_count = layer_1.featureCount()

        for count, feature in enumerate(layer_1.getFeatures()):
            if feedback.isCanceled():
                break

            coords = get_wgs_coords_from_feature(feature, layer_1.sourceCrs())
            try:
                for result_feat in results_factory.get_results(
                    self.endpoint, [coords], params, return_fields
                ):
                    result_feat[FieldNames.LOCATION_ID] = (
                        feature[layer_field_name_1] if layer_field_name_1 else feature.id()
                    )
                    sink.addFeature(result_feat)
                    feedback.setProgress(int((count + 1) / total_count * 100))
            except (
                routingpy.exceptions.RouterApiError,
                routingpy.exceptions.RouterServerError,
            ) as e:
                raise QgsProcessingException(f"HTTP {e.status}: {e.message}")

        return {self.OUT: dest_id}


class ValhallaExpansionCar(ValhallaExpansionBase):
    def __init__(self):
        super(ValhallaExpansionCar, self).__init__(profile=RouterProfile.CAR)


class ValhallaExpansionTruck(ValhallaExpansionBase):
    def __init__(self):
        super(ValhallaExpansionTruck, self).__init__(profile=RouterProfile.TRUCK)


class ValhallaExpansionMotorcycle(ValhallaExpansionBase):
    def __init__(self):
        super(ValhallaExpansionMotorcycle, self).__init__(profile=RouterProfile.MBIKE)


class ValhallaExpansionPedestrian(ValhallaExpansionBase):
    def __init__(self):
        super(ValhallaExpansionPedestrian, self).__init__(profile=RouterProfile.PED)


class ValhallaExpansionBicycle(ValhallaExpansionBase):
    def __init__(self):
        super(ValhallaExpansionBicycle, self).__init__(profile=RouterProfile.BIKE)
