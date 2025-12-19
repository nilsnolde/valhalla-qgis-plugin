from typing import Optional

from qgis.core import QgsMapLayerProxyModel, QgsVectorLayer
from qgis.PyQt.QtWidgets import QDialog

from .compiled.dlg_from_layer_ui import Ui_FromLayerDialog


class FromLayerDialog(QDialog, Ui_FromLayerDialog):
    def __init__(self, parent=None):
        super(FromLayerDialog, self).__init__(parent)
        self.setupUi(self)
        self.from_layer.setFilters(QgsMapLayerProxyModel.PointLayer)

        self.layer: Optional[QgsVectorLayer] = None

    def done(self, r: int = 0):
        if r == QDialog.Accepted:
            self.layer = self.from_layer.currentLayer()

        super().done(r)
