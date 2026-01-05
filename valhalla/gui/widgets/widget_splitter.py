from typing import Optional

from qgis.PyQt.QtCore import QSize
from qgis.PyQt.QtWidgets import QSplitter, QSplitterHandle, QToolButton


class SplitterHandleWithButton(QSplitterHandle):
    def __init__(self, orientation, parent):
        super().__init__(orientation, parent)

        self.btn = QToolButton(self)
        self.btn.setCheckable(True)
        self.btn.setAutoRaise(True)
        self.btn.setIconSize(QSize(12, 12))
        self.btn.setFixedSize(QSize(16, 16))


class SplitterWithHandleButton(QSplitter):
    """A splitter with a button at top center"""

    def __init__(self, orientation, parent=None):
        super().__init__(orientation, parent)
        self.setHandleWidth(18)
        self.handle_button: Optional[QToolButton] = None

    def createHandle(self):
        h = SplitterHandleWithButton(self.orientation(), self)
        self.handle_button = h.btn
        return h
