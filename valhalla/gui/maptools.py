from qgis.gui import QgsMapCanvas, QgsMapMouseEvent, QgsMapToolEmitPoint
from qgis.PyQt.QtCore import pyqtSignal
from qgis.PyQt.QtGui import QCursor, QIcon

CUSTOM_CURSOR = QCursor(QIcon(":images/themes/default/cursors/mCapturePoint.svg").pixmap(16, 16))


class PointTool(QgsMapToolEmitPoint):
    def __init__(self, canvas: QgsMapCanvas):
        """
        :param canvas: current map canvas
        """
        QgsMapToolEmitPoint.__init__(self, canvas)

    doubleClicked = pyqtSignal()

    def canvasDoubleClickEvent(self, e: QgsMapMouseEvent) -> None:
        """Ends point adding and deletes markers from map canvas."""
        self.doubleClicked.emit()
