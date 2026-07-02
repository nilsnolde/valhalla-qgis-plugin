import json

from qgis.core import Qgis
from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QDialog

from ..utils.resource_utils import get_valhalla_config_path
from . import UI_RESOURCE_PATH

GENERATED_FORM_CLASS, _ = uic.loadUiType(str(UI_RESOURCE_PATH / "dlg_config_editor.ui"))


class ConfigEditorDialog(QDialog, GENERATED_FORM_CLASS):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._parent = parent
        self.setupUi(self)

        config = get_valhalla_config_path()
        if config.exists():
            with config.open("r") as f:
                self.ui_text.setText(json.dumps(json.load(f), indent=2))

    # override
    def accept(self):
        try:
            text = json.loads(self.ui_text.toPlainText())
        except json.JSONDecodeError:
            self._parent.status_bar.pushMessage(
                "Invalid JSON", "Failed saving the Valhalla configuration", Qgis.MessageLevel.Warning, 6
            )
            return super().accept()

        with get_valhalla_config_path().open("w") as f:
            json.dump(text, f, indent=2)

        return super().accept()
