from ...compiled.routing_settings_valhalla_pedestrian_widget_ui import (
    Ui_settings_valhalla_pedestrian,
)
from ...widgets.costing_settings.widget_settings_valhalla_base import (
    ValhallaSettingsBase,
)


class ValhallaSettingsPedestrianWidget(ValhallaSettingsBase, Ui_settings_valhalla_pedestrian):
    def __init__(self, parent=None):
        super(ValhallaSettingsPedestrianWidget, self).__init__(parent)
        self.setupUi(self)
