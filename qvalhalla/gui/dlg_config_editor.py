import json

from qgis.core import Qgis
from qgis.PyQt.QtWidgets import QDialog

from ..gui.compiled.dlg_config_editor_ui import Ui_ConfigEditor
from ..utils.resource_utils import get_valhalla_config_path


class ConfigEditorDialog(QDialog, Ui_ConfigEditor):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._parent = parent
        self.setupUi(self)

        with get_valhalla_config_path().open("r") as f:
            self.ui_text.setText(json.dumps(json.load(f), indent=2))

    # override
    def accept(self):
        try:
            text = json.loads(self.ui_text.toPlainText())
        except json.JSONDecodeError:
            self._parent.status_bar.pushMessage(
                "Invalid JSON", "Failed saving the Valhalla configuration", Qgis.Warning, 6
            )
            return super().accept()

        with get_valhalla_config_path().open("w") as f:
            json.dump(text, f, indent=2)

        return super().accept()
