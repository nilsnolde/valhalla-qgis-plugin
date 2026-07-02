from qgis.PyQt import uic

from ... import UI_RESOURCE_PATH
from ...widgets.costing_settings.widget_settings_valhalla_base import (
    ValhallaSettingsBase,
)

GENERATED_FORM_CLASS, _ = uic.loadUiType(
    str(UI_RESOURCE_PATH / "routing_settings_valhalla_car_widget.ui")
)


class ValhallaSettingsBusWidget(ValhallaSettingsBase, GENERATED_FORM_CLASS):
    """
    Costing settings widget for the bus profile.
    Bus costing inherits all auto/car costing options (see Valhalla API docs),
    so this widget reuses the car UI.
    """

    def __init__(self, parent=None):
        super(ValhallaSettingsBusWidget, self).__init__(parent)
        self.setupUi(self)
