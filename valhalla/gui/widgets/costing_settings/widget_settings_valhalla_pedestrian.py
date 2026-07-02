from qgis.PyQt import uic

from ... import UI_RESOURCE_PATH
from ...widgets.costing_settings.widget_settings_valhalla_base import (
    ValhallaSettingsBase,
)

GENERATED_FORM_CLASS, _ = uic.loadUiType(
    str(UI_RESOURCE_PATH / "routing_settings_valhalla_pedestrian_widget.ui")
)


class ValhallaSettingsPedestrianWidget(ValhallaSettingsBase, GENERATED_FORM_CLASS):
    def __init__(self, parent=None):
        super(ValhallaSettingsPedestrianWidget, self).__init__(parent)
        self.setupUi(self)
