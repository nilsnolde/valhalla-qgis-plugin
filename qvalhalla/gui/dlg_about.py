from datetime import datetime
from typing import Optional

from qgis.PyQt.QtWidgets import QDialog

from .. import __version__
from ..gui.compiled.dlg_about_ui import Ui_AboutDialog
from ..utils.http_utils import get_status_response


class AboutDialog(QDialog, Ui_AboutDialog):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._parent = parent
        self.setupUi(self)
        self.ui_plugin_version_text.setText(__version__)

        self.exception_msg: Optional[str] = None
        self.buttonBox.accepted.connect(self.accept)
        self.ui_valhalla_version_text.setText("NA")
        self.ui_data_age_text.setText("NA")
        try:
            result = get_status_response(self._parent.router_widget.provider.url)
            valhalla_version: str = result["version"]
            if "-" in valhalla_version:
                std_version, commit_id = valhalla_version.split("-")
                valhalla_version = f'{std_version}-<a href="https://github.com/valhalla/valhalla/commit/{commit_id}">{commit_id}</a>'
            self.ui_valhalla_version_text.setText(valhalla_version)
            self.ui_data_age_text.setText(
                datetime.fromtimestamp(result["tileset_last_modified"]).isoformat() + " UTC"
            )
        except Exception as e:
            self.exception_msg = str(e)
