from typing import Union

from qgis.core import (
    QgsField,
    QgsFields,
    QgsProcessingException,
    QgsProcessingParameterEnum,
    QgsProcessingParameterNumber,
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
from ..base_algorithm import (
    ValhallaBaseAlgorithm,
)


class ValhallaIsochronesBase(ValhallaBaseAlgorithm):
    METRICS = {"Time (seconds)": "time", "Distance (meters)": "distance"}

    IN_INTERVALS = "INPUT_INTERVALS"
    IN_GENERALIZE = "INPUT_GENERALIZE"
    IN_DENOISE = "INPUT_DENOISE"
    IN_METRIC = "INPUT_METRIC"

    def __init__(self, profile: Union[RouterProfile, str]):
        super(ValhallaIsochronesBase, self).__init__(
            provider=RouterType.VALHALLA,
            endpoint=RouterEndpoint.ISOCHRONES,
            profile=profile,
        )

    def group(self):
        return "Isochrone"

    def groupId(self):
        return "valhalla_isochrone"

    def initAlgorithm(self, configuration, p_str=None, Any=None, *args, **kwargs):
        self.init_base_params()

        interval_param = QgsProcessingParameterString(self.IN_INTERVALS, "Intervals (comma-separated)")
        interval_param.setHelp(
            "Iso intervals that will be computed for each input feature. You can specify up to four intervals."
        )

        metric_param = QgsProcessingParameterEnum(
            self.IN_METRIC,
            "Metric",
            list(self.METRICS),
            defaultValue=list(self.METRICS.keys())[0],
        )
        metric_param.setHelp("The unit of the specified intervals.")

        denoise_param = QgsProcessingParameterNumber(
            self.IN_DENOISE,
            "Denoise",
            type=QgsProcessingParameterNumber.Double,
            minValue=0,
            maxValue=1,
        )

        denoise_param.setHelp(
            "A floating point value from 0 to 1 (default of 1) which can be used to remove smaller contours. "
            "A value of 1 will only return the largest contour for a given time value. A value of 0.5 drops any "
            "contours that are less than half the area of the largest contour in the set of contours for that "
            "same time value."
        )

        generalize_param = QgsProcessingParameterNumber(
            self.IN_GENERALIZE,
            "Generalize",
            type=QgsProcessingParameterNumber.Integer,
            minValue=0,
            maxValue=1000,
        )

        generalize_param.setHelp(
            "A floating point value in meters used as the tolerance for Douglas-Peucker generalization."
            " Note: Generalization of contours can lead to self-intersections, as well as intersections"
            " of adjacent contours."
        )

        for param in (interval_param, metric_param, denoise_param, generalize_param):
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

        params["interval_type"] = self.METRICS[
            list(self.METRICS)[self.parameterAsEnum(parameters, self.IN_METRIC, context)]
        ]
        params["polygons"] = True
        params["denoise"] = self.parameterAsDouble(parameters, self.IN_DENOISE, context)
        params["generalize"] = self.parameterAsInt(parameters, self.IN_GENERALIZE, context)

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
        total_count = layer_1.featureCount()

        for count, feature in enumerate(layer_1.getFeatures()):
            if feedback.isCanceled():
                break

            coords = get_wgs_coords_from_feature(feature, layer_1.sourceCrs())
            try:
                for result_feat in results_factory.get_results(
                    self.endpoint, [coords], params, return_fields
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

        return {self.OUT: dest_id}


class ValhallaIsochroneCar(ValhallaIsochronesBase):
    def __init__(self):
        super(ValhallaIsochroneCar, self).__init__(profile=RouterProfile.CAR)


class ValhallaIsochroneTruck(ValhallaIsochronesBase):
    def __init__(self):
        super(ValhallaIsochroneTruck, self).__init__(profile=RouterProfile.TRUCK)


class ValhallaIsochroneMotorcycle(ValhallaIsochronesBase):
    def __init__(self):
        super(ValhallaIsochroneMotorcycle, self).__init__(profile=RouterProfile.MBIKE)


class ValhallaIsochronePedestrian(ValhallaIsochronesBase):
    def __init__(self):
        super(ValhallaIsochronePedestrian, self).__init__(profile=RouterProfile.PED)


class ValhallaIsochroneBicycle(ValhallaIsochronesBase):
    def __init__(self):
        super(ValhallaIsochroneBicycle, self).__init__(profile=RouterProfile.BIKE)
