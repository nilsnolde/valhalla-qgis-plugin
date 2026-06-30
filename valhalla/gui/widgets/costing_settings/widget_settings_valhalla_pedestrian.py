from qgis.PyQt import uic

from .... import RESOURCE_PATH
from ...widgets.costing_settings.widget_settings_valhalla_base import (
    ValhallaSettingsBase,
)

FORM_CLASS, _ = uic.loadUiType(
    str(RESOURCE_PATH / "ui" / "routing_settings_valhalla_pedestrian_widget.ui")
)


class ValhallaSettingsPedestrianWidget(ValhallaSettingsBase, FORM_CLASS):
    def __init__(self, parent=None):
        super(ValhallaSettingsPedestrianWidget, self).__init__(parent)
        self.setupUi(self)
