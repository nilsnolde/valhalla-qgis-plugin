from pathlib import Path
from shutil import rmtree

from qgis.core import Qgis
from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QDialog, QMessageBox

from ..core.settings import ValhallaSettings
from . import UI_RESOURCE_PATH

GENERATED_FORM_CLASS, _ = uic.loadUiType(str(UI_RESOURCE_PATH / "dlg_graph_from_pbf.ui"))


class GraphFromPBFDialog(QDialog, GENERATED_FORM_CLASS):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._parent = parent
        self.setupUi(self)

        self.graph_dir: Path
        self.temp_graph_dir: Path
        self.pbf_path: str

    # override
    def accept(self):
        self.pbf_path = self.ui_pbf_file.filePath()
        graph_name = self.ui_text_name.text()
        if not self.pbf_path:
            self._parent.status_bar.pushMessage(
                "No PBF", "Needs a PBF file", Qgis.MessageLevel.Critical, 6
            )
            return super().reject()
        elif not graph_name:
            self._parent.status_bar.pushMessage(
                "No Graph name", "Needs a graph name", Qgis.MessageLevel.Critical, 6
            )
            return super().reject()

        try:
            self.graph_dir = ValhallaSettings().get_graph_dir().joinpath(graph_name)
        except FileExistsError:
            ret = QMessageBox.warning(
                self,
                "Graph exists",
                f"The graph {self.graph_dir} already exists. Should it be replaced?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if ret == QMessageBox.StandardButton.No:
                return

            rmtree(self.graph_dir)

        self.graph_dir.mkdir(parents=True, exist_ok=True)

        return super().accept()
