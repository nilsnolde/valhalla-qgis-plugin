from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QDialog

from .. import RESOURCE_PATH

FORM_CLASS, _ = uic.loadUiType(str(RESOURCE_PATH / "ui" / "dlg_server_log.ui"))


class ServerLogDialog(QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)
