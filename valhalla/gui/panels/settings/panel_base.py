from enum import Enum
from typing import List, Optional, Union

from qgis.gui import QgsAuthConfigSelect, QgsFileWidget
from qgis.PyQt.QtCore import QObject
from qgis.PyQt.QtWidgets import QCheckBox, QDialog, QLineEdit, QWidget

from ....core.settings import ValhallaSettings
from ....global_definitions import Dialogs
from ....gui.compiled.dlg_plugin_settings_ui import Ui_PluginSettingsDialog
from ....utils.misc_utils import str_to_bool


class PanelBase(QObject):
    SETTINGS_TYPE: Optional[Dialogs]
    RECOVER: Optional[List[Enum]]

    def __init__(self, dlg: Union[Ui_PluginSettingsDialog, QDialog]):
        super().__init__()
        self._dlg = dlg

        self.manage_settings(dlg)

    @classmethod
    def manage_settings(cls, dlg: QDialog):
        """Sets widget's text boxes to stored values in settings.ini, and connects signals"""
        if not cls.RECOVER:
            return

        for elem in cls.RECOVER:
            widget: QWidget = getattr(dlg, elem.value)
            text = ValhallaSettings().get(cls.SETTINGS_TYPE, elem)
            if isinstance(widget, QLineEdit):
                widget.setText(text)
                widget.textChanged.connect(dlg.on_settings_change)  # connecting to the parent dialog
            elif isinstance(widget, QgsAuthConfigSelect):
                widget.setConfigId(text)
                widget.selectedConfigIdChanged.connect(dlg.on_settings_change)
            elif isinstance(widget, QgsFileWidget):
                widget.setFilePath(text)
                widget.fileChanged.connect(dlg.on_settings_change)
            elif isinstance(widget, QCheckBox):
                widget.setChecked(str_to_bool(text))
                widget.toggled.connect(dlg.on_settings_change)

    def setup_panel(self):
        raise NotImplementedError

    @property
    def dlg(self):
        return self._dlg
