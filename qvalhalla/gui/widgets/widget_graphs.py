import json
from pathlib import Path
from shutil import move, rmtree

from qgis.core import Qgis
from qgis.PyQt.QtCore import QDir
from qgis.PyQt.QtWidgets import QFileDialog, QFileSystemModel, QListView, QMessageBox, QWidget

from ...core.settings import ValhallaSettings
from ...utils.qt_utils import FileNameInDirFilterProxy
from ...utils.resource_utils import get_icon
from ..compiled.widget_graphs_ui import Ui_GraphWidget
from ..dlg_config_editor import ConfigEditorDialog
from ..ui_definitions import ID_JSON

FOLDER_BUTTON_TOOLTIP = "Set the graph library directory\nCurrently: {}"


class GraphWidget(QWidget, Ui_GraphWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.setupUi(self)
        self._parent = parent

        self.graph_dir = ValhallaSettings().get_graph_dir()

        # button icons
        self.ui_btn_graph_add.setIcon(get_icon(":images/themes/default/grid.svg"))
        self.ui_btn_graph_remove.setIcon(get_icon("graph_remove.svg"))
        self.ui_btn_settings.setIcon(get_icon(":images/themes/default/console/iconSettingsConsole.svg"))
        self.ui_btn_graph_folder.setIcon(get_icon("graph_folder.svg"))
        self.ui_btn_graph_folder.setToolTip(FOLDER_BUTTON_TOOLTIP.format(self.graph_dir))

        # use the graph dir as model for the list view with the restriction that a directory
        # has to contain a "id.json"
        self.graph_dir_model = QFileSystemModel()
        self.graph_dir_model.setFilter(QDir.Filter.NoDotAndDotDot | QDir.Filter.Dirs)
        self.graph_dir_model.setRootPath(str(self.graph_dir.resolve()))

        self.graph_dir_proxy = FileNameInDirFilterProxy(ID_JSON)
        self.graph_dir_proxy.setSourceModel(self.graph_dir_model)
        self.graph_dir_proxy.setRootPath(str(self.graph_dir.resolve()))
        self.ui_list_graphs.setModel(self.graph_dir_proxy)

        root_idx = self.graph_dir_model.index(str(self.graph_dir.resolve()))
        self.ui_list_graphs.setRootIndex(self.graph_dir_proxy.mapFromSource(root_idx))

        # connections
        self.ui_btn_graph_add.clicked.connect(self._on_graph_add)
        self.ui_btn_graph_remove.clicked.connect(self._on_graph_remove)
        self.ui_btn_graph_folder.clicked.connect(self._on_graph_folder_change)
        self.ui_btn_graph_remove.clicked.connect(self._on_graph_remove)
        self.ui_btn_settings.clicked.connect(self._on_config_edit)
        self.graph_dir_model.directoryLoaded.connect(self.graph_dir_proxy.invalidateFilter)
        self.graph_dir_model.rootPathChanged.connect(self.graph_dir_proxy.invalidateFilter)

    def _check_list_view(self):
        root = self.ui_list_graphs.rootIndex()
        if not self.ui_list_graphs.model().rowCount(root):
            self._parent.status_bar.pushMessage(
                "No graphs", f"Couldn't find any usable graph in {self.graph_dir}", Qgis.Warning, 6
            )

    def _on_config_edit(self):
        dlg = ConfigEditorDialog(self._parent)
        dlg.exec()

    def _on_graph_remove(self):
        self.ui_list_graphs: QListView
        idx = self.ui_list_graphs.selectedIndexes()
        if not idx:
            return
        idx = idx[0]
        path = Path(self.graph_dir_model.filePath(self.graph_dir_proxy.mapToSource(idx)))
        try:
            rmtree(path)
        except:
            pass
        self._parent.status_bar.pushMessage("Removed graph", f"{path.stem}", Qgis.Warning, 3)

    def _on_graph_add(self):
        try:
            in_tar_path = QFileDialog.getOpenFileName(
                self,
                "Import graph",
                "/home/nilsnolde/dev/cpp/valhalla/site",
                "Tar Files (*.tar)",
                options=QFileDialog.Option.ShowDirsOnly,
            )[0]
            if not in_tar_path:
                return
            in_tar_path = Path(in_tar_path)
            out_tar_dir = self.graph_dir.joinpath(in_tar_path.stem)
            out_tar_dir.mkdir(exist_ok=False)
        except FileExistsError:
            ret = QMessageBox.warning(
                self,
                "File exists",
                f"The graph {out_tar_dir} already exists. Should it be replaced?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes,
            )
            if ret == QMessageBox.No:
                return

        # move the tar file
        out_tar_file = out_tar_dir.joinpath(in_tar_path.name)
        if out_tar_file.exists():
            out_tar_file.unlink()
        move(in_tar_path, out_tar_file)

        # create/update the id.json
        id_json_path = out_tar_dir.joinpath(ID_JSON)
        with id_json_path.open("w") as f:
            json.dump(
                {
                    "mjolnir": {
                        "tile_dir": "",
                        "tile_extract": str(out_tar_file.resolve()),
                        "tile_url": "",
                        "tile_url_user_pw": "",
                    },
                    "loki": {"use_connectivity": True},
                },
                f,
                indent=2,
            )

    def _on_graph_folder_change(self):
        new_graph_dir = QFileDialog.getExistingDirectory(
            self,
            "Select new graph directory",
            str(self.graph_dir.resolve()),
            QFileDialog.Option.ShowDirsOnly | QFileDialog.Option.DontResolveSymlinks,
        )
        if not new_graph_dir:
            return

        # update everything that's got to do with the graph dir
        self.graph_dir = Path(new_graph_dir).resolve()

        ValhallaSettings().set_graph_dir(self.graph_dir)
        self.ui_btn_graph_folder.setToolTip(FOLDER_BUTTON_TOOLTIP.format(self.graph_dir))

        self.graph_dir_model.setRootPath(new_graph_dir)
        self.graph_dir_proxy.setRootPath(new_graph_dir)

        # get the source index for that folder and map it through the proxy
        src_root = self.graph_dir_model.index(new_graph_dir)
        self.ui_list_graphs.setRootIndex(self.graph_dir_proxy.mapFromSource(src_root))

        self._check_list_view()
