import json
from shutil import rmtree
from urllib.parse import urlparse

from qgis.core import Qgis
from qgis.PyQt.QtWidgets import QDialog, QMessageBox

from ..core.settings import ValhallaSettings
from .compiled.dlg_graph_from_url_ui import Ui_GraphFromUrl
from .ui_definitions import ID_JSON


class GraphFromURLDialog(QDialog, Ui_GraphFromUrl):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._parent = parent
        self.setupUi(self)

    # override
    def accept(self):
        url = self.ui_text_url.text()
        parsed_url = urlparse(url)
        if not url or not parsed_url.scheme:
            self._parent.status_bar.pushMessage("No URL", "Needs a valid HTTP(s) URL", Qgis.Critical, 6)
            return super().reject()

        try:
            graph_name = self.ui_text_name.text()
            if not graph_name:
                graph_name = f"{parsed_url.netloc}"
            graph_dir = ValhallaSettings().get_graph_dir().joinpath(graph_name)
            graph_dir.mkdir(exist_ok=False)
        except FileExistsError:
            ret = QMessageBox.warning(
                self,
                "Graph exists",
                f"The graph {graph_dir} already exists. Should it be replaced?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
            if ret == QMessageBox.No:
                return

            rmtree(graph_dir)
            graph_dir.mkdir()

        # create the id.json
        id_json_path = graph_dir.joinpath(ID_JSON)
        user_pw = ""
        if (user := self.ui_text_user.text()) and (pw := self.ui_text_password.text()):
            user_pw = f"{user}:{pw}"
        with id_json_path.open("w") as f:
            json.dump(
                {
                    "mjolnir": {
                        "tile_dir": str(graph_dir.resolve()),
                        "tile_extract": "",
                        "tile_url": url,
                        "tile_url_user_pw": user_pw,
                    },
                    "loki": {"use_connectivity": False},
                },
                f,
                indent=2,
            )

        return super().accept()
