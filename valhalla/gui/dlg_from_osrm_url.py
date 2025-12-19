from qgis.PyQt.QtWidgets import QDialog

from .compiled.dlg_from_osrm_url_ui import Ui_FromOsrmUrlDialog


class FromOsrmUrlDialog(QDialog, Ui_FromOsrmUrlDialog):
    def __init__(self, parent=None):
        super(FromOsrmUrlDialog, self).__init__(parent)
        self.setupUi(self)
