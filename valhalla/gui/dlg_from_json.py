from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QDialog

from .. import RESOURCE_PATH

FORM_CLASS, _ = uic.loadUiType(str(RESOURCE_PATH / "ui" / "dlg_from_json.ui"))


class FromValhallaJsonDialog(QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        super(FromValhallaJsonDialog, self).__init__(parent)
        self.setupUi(self)
