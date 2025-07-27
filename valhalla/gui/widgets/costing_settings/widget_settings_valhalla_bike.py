from ...compiled.routing_settings_valhalla_bike_widget_ui import (
    Ui_settings_valhalla_bike,
)
from .widget_settings_valhalla_base import ValhallaSettingsBase

BIKE_SPEED_MAP = {  # default speeds in km/h
    "Road": 25,
    "Hybrid": 18,
    "Cross": 20,
    "Mountain": 16,
}


class ValhallaSettingsBikeWidget(ValhallaSettingsBase, Ui_settings_valhalla_bike):
    def __init__(self, parent=None):
        super(ValhallaSettingsBikeWidget, self).__init__(parent)
        self.setupUi(self)

        self.cycling_speed.setValue(BIKE_SPEED_MAP[self.bicycle_type.currentText()])
        self.bicycle_type.currentTextChanged.connect(self.set_default_speed)

    def set_default_speed(self, bicycle_type: str) -> None:
        """Sets the default speed according to the bicycle type.

        :param bicycle_type: One of the supported Valhalla bicycle types ( "Road", "Hybrid", "Cross", "Mountain")
        """
        self.cycling_speed.setValue(BIKE_SPEED_MAP[bicycle_type])
