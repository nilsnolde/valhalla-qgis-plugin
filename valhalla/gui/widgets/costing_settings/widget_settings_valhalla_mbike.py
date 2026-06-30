from qgis.PyQt import uic

from .... import RESOURCE_PATH
from ...widgets.costing_settings.widget_settings_valhalla_base import (
    ValhallaSettingsBase,
)

FORM_CLASS, _ = uic.loadUiType(str(RESOURCE_PATH / "ui" / "routing_settings_valhalla_mbike_widget.ui"))


class ValhallaSettingsMbikeWidget(ValhallaSettingsBase, FORM_CLASS):
    def __init__(self, parent=None):
        super(ValhallaSettingsMbikeWidget, self).__init__(parent)
        self.setupUi(self)
