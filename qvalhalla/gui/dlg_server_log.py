from qgis.PyQt.QtWidgets import QDialog

from ..gui.compiled.dlg_server_log_ui import Ui_ServerLog


class ServerLogDialog(QDialog, Ui_ServerLog):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)
