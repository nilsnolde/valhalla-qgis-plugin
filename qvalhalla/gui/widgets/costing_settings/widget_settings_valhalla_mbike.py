from ...compiled.routing_settings_valhalla_mbike_widget_ui import (
    Ui_settings_valhalla_mbike,
)
from ...widgets.costing_settings.widget_settings_valhalla_base import (
    ValhallaSettingsBase,
)


class ValhallaSettingsMbikeWidget(ValhallaSettingsBase, Ui_settings_valhalla_mbike):
    def __init__(self, parent=None):
        super(ValhallaSettingsMbikeWidget, self).__init__(parent)
        self.setupUi(self)
