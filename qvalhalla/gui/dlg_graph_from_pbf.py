from shutil import rmtree

from qgis.core import Qgis
from qgis.PyQt.QtWidgets import QDialog, QMessageBox

from ..core.settings import ValhallaSettings
from .compiled.dlg_graph_from_pbf_ui import Ui_GraphFromPBF


class GraphFromPBFDialog(QDialog, Ui_GraphFromPBF):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._parent = parent
        self.setupUi(self)

        self.graph_dir: str
        self.pbf_path: str

    # override
    def accept(self):
        self.pbf_path = self.ui_pbf_file.filePath()
        graph_name = self.ui_text_name.text()
        if not self.pbf_path:
            self._parent.status_bar.pushMessage("No PBF", "Needs a PBF file", Qgis.Critical, 6)
            return super().reject()
        elif not graph_name:
            self._parent.status_bar.pushMessage("No Graph name", "Needs a graph name", Qgis.Critical, 6)
            return super().reject()

        try:
            # don't create the directory yet; it needs the proper id.json to show up in the dropdown/list
            self.graph_dir = ValhallaSettings().get_graph_dir().joinpath(graph_name)
        except FileExistsError:
            ret = QMessageBox.warning(
                self,
                "Graph exists",
                f"The graph {self.graph_dir} already exists. Should it be replaced?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
            if ret == QMessageBox.No:
                return

            rmtree(self.graph_dir)

        return super().accept()
