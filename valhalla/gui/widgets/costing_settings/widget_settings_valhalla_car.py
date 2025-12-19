from ...compiled.routing_settings_valhalla_car_widget_ui import (
    Ui_settings_valhalla_car,
)
from ...widgets.costing_settings.widget_settings_valhalla_base import (
    ValhallaSettingsBase,
)


class ValhallaSettingsCarWidget(ValhallaSettingsBase, Ui_settings_valhalla_car):
    def __init__(self, parent=None):
        super(ValhallaSettingsCarWidget, self).__init__(parent)
        self.setupUi(self)
