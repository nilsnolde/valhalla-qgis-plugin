from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QDialog

from . import UI_RESOURCE_PATH

GENERATED_FORM_CLASS, _ = uic.loadUiType(str(UI_RESOURCE_PATH / "dlg_from_json.ui"))


class FromValhallaJsonDialog(QDialog, GENERATED_FORM_CLASS):
    def __init__(self, parent=None):
        super(FromValhallaJsonDialog, self).__init__(parent)
        self.setupUi(self)
