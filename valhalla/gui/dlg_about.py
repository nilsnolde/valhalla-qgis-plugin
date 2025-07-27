from qgis.PyQt.QtWidgets import QDialog

from ..gui.compiled.dlg_about_ui import Ui_AboutDialog


class AboutDialog(QDialog, Ui_AboutDialog):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.parent = parent
        self.setupUi(self)
