from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QDialog

from . import UI_RESOURCE_PATH

GENERATED_FORM_CLASS, _ = uic.loadUiType(str(UI_RESOURCE_PATH / "dlg_from_osrm_url.ui"))


class FromOsrmUrlDialog(QDialog, GENERATED_FORM_CLASS):
    def __init__(self, parent=None):
        super(FromOsrmUrlDialog, self).__init__(parent)
        self.setupUi(self)
