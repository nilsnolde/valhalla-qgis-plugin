from qgis.PyQt import uic

from ... import UI_RESOURCE_PATH
from ...widgets.costing_settings.widget_settings_valhalla_base import (
    ValhallaSettingsBase,
)

GENERATED_FORM_CLASS, _ = uic.loadUiType(
    str(UI_RESOURCE_PATH / "routing_settings_valhalla_mbike_widget.ui")
)


class ValhallaSettingsMbikeWidget(ValhallaSettingsBase, GENERATED_FORM_CLASS):
    def __init__(self, parent=None):
        super(ValhallaSettingsMbikeWidget, self).__init__(parent)
        self.setupUi(self)
