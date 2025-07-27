from valhalla.gui.compiled.routing_settings_valhalla_truck_widget_ui import (
    Ui_settings_valhalla_truck,
)
from valhalla.gui.widgets.costing_settings.widget_settings_valhalla_base import (
    ValhallaSettingsBase,
)


class ValhallaSettingsTruckWidget(ValhallaSettingsBase, Ui_settings_valhalla_truck):
    def __init__(self, parent=None):
        super(ValhallaSettingsTruckWidget, self).__init__(parent)
        self.setupUi(self)
