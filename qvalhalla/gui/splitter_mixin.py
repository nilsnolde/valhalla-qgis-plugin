from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QResizeEvent
from qgis.PyQt.QtWidgets import QSplitter, QSplitterHandle, QToolButton, QVBoxLayout
from qvalhalla.utils.resource_utils import get_icon


class SplitterMixin:
    def __init__(self, splitter: QSplitter, parent=None):
        """
        The Splitter mixin class adds functionality to the routing and spopt dialogs' splitters, like resizing and
        memorizing splitter state, and inserts a collapse button into the splitter handle.
        """
        self.splitter = splitter
        self.parent = parent

        # splitter collapse button
        splitter_handle: QSplitterHandle = self.splitter.handle(1)
        handle_layout = QVBoxLayout()
        handle_layout.setContentsMargins(0, 0, 0, 0)
        self.collapse_button = QToolButton(splitter_handle)
        self.collapse_button.setAutoRaise(True)
        self.collapse_button.setCheckable(True)
        self.collapse_button.setChecked(True)
        self.collapse_button.setFixedSize(24, 24)
        self.collapse_button.setIcon(get_icon("costing_options.svg"))
        self.collapse_button.setCursor(Qt.ArrowCursor)
        self.collapse_button.setToolTip(
            "Click to collapse/expand the costing options panel. <br/>"
            "If collapsed, costing options won't be used."
        )
        handle_layout.addWidget(self.collapse_button)
        handle_layout.addStretch()
        splitter_handle.setLayout(handle_layout)
        self.splitter.setSizes((2000, 2500))
        self.previous_splitter_state = self.splitter.saveState()
        self.collapsed_size = [int(self.width() * 0.5), self.height()]
        self.expanded_size = [self.width(), self.height()]

        self.collapse_button.clicked.connect(self._toggle_settings_collapse)
        self.splitter.splitterMoved.connect(self._on_splitter_change)

    def _on_splitter_change(self, pos, ix):
        self.collapse_button.setChecked(not self.splitter.sizes()[1] == 0)

    def _toggle_settings_collapse(self):
        if self.collapse_button.isChecked():
            self.splitter.restoreState(self.previous_splitter_state)
            self.resize(*self.expanded_size)
        else:
            self.previous_splitter_state = self.splitter.saveState()
            self.splitter.setSizes((1, 0))
            self.resize(*self.collapsed_size)

    def resizeEvent(self, event: QResizeEvent):
        """
        Intercepts QDialog's native resizeEvent method and - if the resizing is performed by the user -
        stores the dialog's new width for the current collapsed state, and its new width for both
        collapsed states.
        """
        super(type(self), self).resizeEvent(event)
        if not event.spontaneous():  # only for resizing performed by user
            return

        if self.collapse_button.isChecked():
            self.expanded_size = [self.width(), self.height()]
            self.collapsed_size[1] = self.height()  # save height for both collapse states
        else:
            self.collapsed_size = [self.width(), self.height()]
            self.expanded_size[1] = self.height()
