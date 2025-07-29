from datetime import datetime
from typing import Optional

from qgis.PyQt.QtWidgets import QDialog

from .. import __version__
from ..gui.compiled.dlg_about_ui import Ui_AboutDialog
from ..utils.http_utils import get_status_response


class AboutDialog(QDialog, Ui_AboutDialog):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.parent = parent
        self.setupUi(self)
        self.ui_plugin_version_text.setText(__version__)

        self.exception_msg: Optional[str] = None
        self.buttonBox.accepted.connect(self.accept)
        self.ui_valhalla_version_text.setText("NA")
        self.ui_data_age_text.setText("NA")
        try:
            result = get_status_response(self.parent.router_widget.provider.url)
            self.ui_valhalla_version_text.setText(result["version"])
            self.ui_data_age_text.setText(
                datetime.fromtimestamp(result["tileset_last_modified"]).isoformat() + " UTC"
            )
        except Exception as e:
            self.exception_msg = str(e)
