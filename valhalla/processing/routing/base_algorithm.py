from pathlib import Path
from typing import List, Optional, Tuple, Type

from qgis.core import (
    QgsFeatureSink,
    QgsFields,
    QgsProcessing,
    QgsProcessingAlgorithm,
    QgsProcessingParameterBoolean,
    QgsProcessingParameterDefinition,
    QgsProcessingParameterEnum,
    QgsProcessingParameterFeatureSink,
    QgsProcessingParameterFeatureSource,
    QgsProcessingParameterField,
    QgsProcessingParameterNumber,
    QgsProcessingParameterString,
    QgsVectorLayer,
)
from qgis.PyQt.QtCore import QCoreApplication
from qgis.PyQt.QtGui import QIcon

from valhalla.core.results_factory import ResultsFactory
from valhalla.core.settings import ProviderSetting, ValhallaSettings
from valhalla.global_definitions import (
    SETTINGS_WIDGETS_MAP,
    RouterEndpoint,
    RouterMethod,
    RouterProfile,
    RouterType,
    RoutingMetric,
)
from valhalla.gui.widgets.costing_settings.widget_settings_valhalla_base import (
    ValhallaSettingsBase,
)
from valhalla.processing.processing_definitions import HELP_DIR
from valhalla.utils.geom_utils import WGS84
from valhalla.utils.layer_utils import get_wgs_coords_from_layer
from valhalla.utils.misc_utils import wrap_in_html_tag
from valhalla.utils.resource_utils import get_graph_dir, get_icon


class ValhallaBaseAlgorithm(QgsProcessingAlgorithm):

    IN_PROVIDER = "INPUT_PROVIDER"
    IN_URL = "INPUT_URL"
    IN_PKG = "INPUT_PACKAGE"
    IN_MODE = "INPUT_MODE"
    IN_AVOID_LOCATIONS = "INPUT_AVOID_LOCATIONS"
    IN_AVOID_POLYGONS = "INPUT_AVOID_POLYGONS"
    IN_1 = "INPUT_LAYER_1"
    IN_FIELD_1 = "INPUT_FIELD_1"

    OUT = "OUTPUT"

    def __init__(
        self,
        provider: RouterType,
        endpoint: RouterEndpoint,
        profile: Optional[RouterProfile] = None,
    ):
        super(ValhallaBaseAlgorithm, self).__init__()

        self.router = provider  # avoid overriding QGIS' built-in provider method
        self.providers: List[ProviderSetting] = list()  # will be set in init_base_params
        self.endpoint = endpoint
        self.profile = RouterProfile(profile) if profile else RouterProfile.CAR
        if provider == RouterType.VALHALLA:
            costing_widget: Type[ValhallaSettingsBase] = SETTINGS_WIDGETS_MAP[self.profile]["widget"]

            # we keep the costing params dict for retrieving the parameter values later
            self.costing_defaults = self.get_costing_defaults(costing_widget)

        self.pkgs = [pkg_path.name for pkg_path in get_graph_dir(self.router).iterdir()]

    def tr(self, string):
        """
        Returns a translatable string with the self.tr() function.
        """
        return QCoreApplication.translate("Processing", string)

    def init_base_params(self, multi_layer: bool = False) -> None:
        """
        We call this method in each subclass' initAlgorithm method, since these parameters are constant
        across algorithms.

        :param multi_layer: If True, adds a number to the input layer and input field descriptions.
        """

        self.providers = ValhallaSettings().get_providers(RouterType.VALHALLA)
        servers = [prov.name for prov in self.providers]

        method_param = QgsProcessingParameterEnum(
            self.IN_PROVIDER,
            "Provider",
            servers,
            defaultValue=servers[0],
        )
        self.addParameter(method_param)

        # pkg_param = QgsProcessingParameterEnum(
        #     self.IN_PKG,
        #     "Package path (used if method is Bindings)",
        #     options=self.pkgs,
        #     defaultValue=0,
        # )
        # self.addParameter(pkg_param)

        # url_param = QgsProcessingParameterString(
        #     self.IN_URL, "URL (used if method is HTTP)", defaultValue=defaultUrl
        # )
        # self.addParameter(url_param)

        if self.router == RouterType.VALHALLA:
            mode_param = QgsProcessingParameterEnum(
                self.IN_MODE,
                "Mode",
                options=list(RoutingMetric),
                defaultValue=RoutingMetric[0],
            )
            mode_param.setHelp(
                "If 'shortest', Valhalla will solely use distance as cost and disregard all other costs, penalties and factors."
            )

            mode_param.setFlags(QgsProcessingParameterDefinition.FlagAdvanced)

            self.addParameter(mode_param)

            avoid_locations_param = QgsProcessingParameterFeatureSource(
                name=self.IN_AVOID_LOCATIONS,
                description="Point layer with locations to avoid",
                types=[QgsProcessing.TypeVectorPoint],
                optional=True,
            )

            avoid_locations_param.setFlags(
                avoid_locations_param.flags() | QgsProcessingParameterDefinition.FlagAdvanced
            )
            self.addParameter(avoid_locations_param)

            avoid_polygons_param = QgsProcessingParameterFeatureSource(
                name=self.IN_AVOID_POLYGONS,
                description="Point layer with polygons to avoid",
                types=[QgsProcessing.TypeVectorPolygon],
                optional=True,
            )
            avoid_polygons_param.setFlags(
                avoid_polygons_param.flags() | QgsProcessingParameterDefinition.FlagAdvanced
            )
            self.addParameter(avoid_polygons_param)
            self.setup_costing_options()

        input_layer_desc = f"Input point layer{' 1' if multi_layer else ''}"
        input_param = QgsProcessingParameterFeatureSource(
            name=self.IN_1,
            description=wrap_in_html_tag(input_layer_desc, "b"),
            types=[QgsProcessing.TypeVectorPoint],
        )
        self.addParameter(input_param)

        input_field_desc = f"Layer{' 1' if multi_layer else ''} ID field (can be used for joining)"
        input_field_param = QgsProcessingParameterField(
            name=self.IN_FIELD_1,
            description=input_field_desc,
            parentLayerParameterName=self.IN_1,
            optional=True,
        )
        self.addParameter(input_field_param)

        output_param = QgsProcessingParameterFeatureSink(
            name=self.OUT,
            description=f"{self.router}_{self.endpoint}"
            f"{f'_{self.profile}' if self.router == RouterType.VALHALLA else str()}",
            createByDefault=True,
        )
        self.addParameter(output_param)

    def get_base_params(self, parameters, context):
        provider: ProviderSetting = self.providers[
            self.parameterAsEnum(parameters, self.IN_PROVIDER, context)
        ]
        mode = RoutingMetric[self.parameterAsEnum(parameters, self.IN_MODE, context)]
        # url = self.parameterAsString(parameters, self.IN_URL, context)
        # pkg = (
        #     self.pkgs[self.parameterAsEnum(parameters, self.IN_PKG, context)]
        #     if len(self.pkgs) > 0
        #     else ""
        # )
        layer_1: QgsVectorLayer = self.parameterAsSource(parameters, self.IN_1, context)
        layer_field_name_1 = self.parameterAsString(parameters, self.IN_FIELD_1, context)

        params = dict()
        if self.router == RouterType.VALHALLA:
            params["options"] = dict()
            avoid_locations = self.parameterAsSource(parameters, self.IN_AVOID_LOCATIONS, context)
            if avoid_locations:
                params["avoid_locations"] = get_wgs_coords_from_layer(avoid_locations)

            avoid_polygons = self.parameterAsSource(parameters, self.IN_AVOID_POLYGONS, context)
            if avoid_polygons:
                params["avoid_polygons"] = get_wgs_coords_from_layer(avoid_polygons)

            params["options"] = self.get_costing_options(parameters, context)
            params["options"]["shortest"] = True if mode == RoutingMetric.SHORTEST else False

        factory_args = {
            "provider": self.router,
            "url": provider.url,
            "profile": self.profile,
            "method": RouterMethod.REMOTE,
        }

        # if method == RouterMethod.LOCAL:
        #     if not pkg:
        #         raise QgsProcessingException(
        #             f"You chose the '{method}' method but don't seem to have any packages downloaded."
        #         )
        #     factory_args.update(
        #         {
        #             "method": RouterMethod.LOCAL,
        #             "url": None,
        #             "pkg_path": str(get_graph_dir(self.router) / pkg),
        #         }
        #     )
        results_factory = ResultsFactory(**factory_args)

        return layer_1, layer_field_name_1, params, results_factory

    def setup_costing_options(self):
        """Takes the costing defaults retrieved from the settings widget and creates processing parameters from them."""
        for param_name, param_dict in self.costing_defaults:
            processing_param: QgsProcessingParameterDefinition

            processing_param_args = {
                "name": param_name,
                "description": " ".join(map(lambda w: w.capitalize(), param_name.split("_"))),
                "defaultValue": param_dict["value"],
                "optional": True,
            }

            param_type = param_dict["type"]

            if param_type in (int, float):
                param_min = param_dict["min"]
                param_max = param_dict["max"]

                processing_param = QgsProcessingParameterNumber(
                    **processing_param_args,
                    type=(
                        QgsProcessingParameterNumber.Integer
                        if param_type == int
                        else QgsProcessingParameterNumber.Double
                    ),
                    minValue=param_min,
                    maxValue=param_max,
                )
            elif param_type == bool:
                processing_param = QgsProcessingParameterBoolean(**processing_param_args)

            elif param_type == str:
                processing_param = QgsProcessingParameterString(**processing_param_args)

            else:
                raise TypeError(f"Type {param_type} not supported for costing options.")

            processing_param.setFlags(
                processing_param.flags() | QgsProcessingParameterDefinition.FlagAdvanced
            )
            processing_param.setHelp(param_dict["help"])
            self.addParameter(processing_param)

    @staticmethod
    def get_costing_defaults(costing_widget: Type[ValhallaSettingsBase]):
        """Retrieves the costing defaults from the given costing_widgets."""
        return costing_widget().get_params(include_info=True).items()

    def get_costing_options(self, parameters, context) -> dict:
        """Returns the costing options as set by the user in the processing algo UI."""
        costing_params = dict()
        for param_name, param_dict in self.costing_defaults:
            param_type = param_dict["type"]

            if param_type == int:
                parameter_getter = self.parameterAsInt
            elif param_type == float:
                parameter_getter = self.parameterAsDouble
            elif param_type == bool:
                parameter_getter = self.parameterAsBoolean
            elif param_type == str:
                parameter_getter = self.parameterAsString
            else:
                raise TypeError(f"Type {param_type} not supported for costing options.")
            costing_params[param_name] = parameter_getter(parameters, param_name, context)

        return costing_params

    def get_feature_sink(self, parameters, context, fields: QgsFields) -> Tuple[QgsFeatureSink, str]:
        """
        Convenience method to get the algorithm's feature sink with the corresponding endpoint's QgsFields
        and optionally additional fields (e.g. an ID field).

        :param parameters: passed from processAlgorithm()
        :param context: passed from processAlgorithm()
        :param fields: QgsFields that will be appended after the endpoint fields or overwrite the default if specified twice.
        """

        return self.parameterAsSink(
            parameters,
            self.OUT,
            context,
            fields,
            ResultsFactory.geom_type(self.endpoint),
            WGS84,
        )

    def createInstance(self):
        # we can ignore the unfulfilled parameter warning here because we know it will only be
        # instantiated by subclasses that automatically pass these parameters
        if self.router == RouterType.VALHALLA:
            return type(self)(profile=self.profile)
        else:
            return type(self)()

    def group(self) -> str:
        if self.router == RouterType.VALHALLA:
            return self.router.capitalize()
        else:
            return self.router.upper()

    def groupId(self):
        return self.router

    def icon(self) -> QIcon:
        return get_icon(f"icon_{self.endpoint}.png")

    def name(self):
        if self.router == RouterType.VALHALLA:
            return f"{self.router.lower()}_{self.endpoint.lower()}_{self.profile.lower()}"

        return f"{self.router.lower()}_{self.endpoint.lower()}"

    def displayName(self):
        if self.router == RouterType.VALHALLA:
            return f"{self.endpoint.capitalize()} | {self.profile.capitalize()}"

        return f"{self.endpoint.capitalize()}"  # there are no profiles for OSRM

    def shortHelpString(self):
        """Displays the sidebar help in the algorithm window"""

        file = HELP_DIR / Path(f"{self.router.lower()}_{self.endpoint.lower()}.help")

        with open(file) as fh:
            msg = fh.read()

        return msg
