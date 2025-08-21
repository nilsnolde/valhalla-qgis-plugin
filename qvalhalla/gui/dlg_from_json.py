from qgis.PyQt.QtWidgets import QDialog

from .compiled.dlg_from_json_ui import Ui_FromValhallaJsonDialog


class FromValhallaJsonDialog(QDialog, Ui_FromValhallaJsonDialog):
    def __init__(self, parent=None):
        super(FromValhallaJsonDialog, self).__init__(parent)
        self.setupUi(self)
