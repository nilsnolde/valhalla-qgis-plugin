import json
import os
from pathlib import Path
from shutil import move, rmtree

from qgis.core import Qgis
from qgis.PyQt.QtCore import QDir, QProcess
from qgis.PyQt.QtWidgets import (
    QAction,
    QDialog,
    QFileDialog,
    QFileSystemModel,
    QListView,
    QMenu,
    QMessageBox,
    QToolButton,
    QWidget,
)

from ...core.settings import ValhallaSettings
from ...utils.qt_utils import FileNameInDirFilterProxy
from ...utils.resource_utils import get_icon
from ..compiled.widget_graphs_ui import Ui_GraphWidget
from ..dlg_config_editor import ConfigEditorDialog
from ..dlg_graph_from_pbf import GraphFromPBFDialog
from ..dlg_graph_from_url import GraphFromURLDialog
from ..dlg_server_log import ServerLogDialog
from ..ui_definitions import ID_JSON

FOLDER_BUTTON_TOOLTIP = "Set the graph library directory\nCurrently: {}"


class GraphWidget(QWidget, Ui_GraphWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.setupUi(self)
        self.extendUi()
        self._parent = parent

        self.graph_dir = ValhallaSettings().get_graph_dir()

        self.dlg_log = ServerLogDialog()
        self.from_url_dlg = GraphFromURLDialog(self._parent)
        self.config_dlg = ConfigEditorDialog(self._parent)

        # building the graph needs a bit more setup, it's a whole orchestration of processes...
        self.from_pbf_dlg = GraphFromPBFDialog(self._parent)
        self.pbf_graph_dir = ""
        self.pbf_path = ""
        self.thread_count = os.cpu_count() or 1

        def make_build_process() -> QProcess:
            proc = QProcess(self)
            proc.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
            proc.readyReadStandardOutput.connect(self._on_build_pbf_log_ready)

            return proc

        self.valhalla_build_admins = make_build_process()
        self.valhalla_build_admins.finished.connect(self._on_admins_finished)
        self.valhalla_build_tiles = make_build_process()
        self.valhalla_build_tiles.finished.connect(self._on_tiles_finished)

        # button icons
        # self.ui_btn_graph_add.setIcon(get_icon(":images/themes/default/grid.svg"))
        self.ui_btn_graph_remove.setIcon(get_icon("graph_remove.svg"))
        self.ui_btn_settings.setIcon(get_icon(":images/themes/default/console/iconSettingsConsole.svg"))
        self.ui_btn_graph_folder.setIcon(get_icon("graph_folder.svg"))
        self.ui_btn_graph_log.setIcon(get_icon(":images/themes/default/mMessageLog.svg"))
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
        self.from_pbf_dlg.finished.connect(self._on_graph_add_build)
        self.ui_btn_graph_remove.clicked.connect(self._on_graph_remove)
        self.ui_btn_graph_folder.clicked.connect(self._on_graph_folder_change)
        self.ui_btn_settings.clicked.connect(self.config_dlg.exec)
        self.ui_btn_graph_log.clicked.connect(self.dlg_log.exec)
        self.graph_dir_model.directoryLoaded.connect(self.graph_dir_proxy.invalidateFilter)
        self.graph_dir_model.rootPathChanged.connect(self.graph_dir_proxy.invalidateFilter)

    def extendUi(self):
        # turn the "graph add" button into a menu to choose from HTTP, local graph build etc
        self.ui_btn_graph_add_tar.setPopupMode(QToolButton.MenuButtonPopup)
        self.ui_btn_graph_add_tar.setAutoRaise(False)
        self.ui_btn_graph_add_tar.triggered.connect(self.ui_btn_graph_add_tar.setDefaultAction)

        dropdown_menu = QMenu()
        actions = list()
        for icon, title, connect_fn in (
            (get_icon("graph_add_tar.svg"), "From Tar", self._on_graph_add_tar),
            (
                get_icon("graph_add_url.svg"),
                "From URL",
                lambda: self.from_url_dlg.exec(),
            ),
            (get_icon("graph_add_build.svg"), "From PBF", lambda: self.from_pbf_dlg.open()),
        ):
            action = QAction(icon, title, self)
            action.triggered.connect(connect_fn)
            action.setToolTip(f"Add Graph {title}")
            dropdown_menu.addAction(action)
            actions.append(action)

        self.ui_btn_graph_add_tar.setMenu(dropdown_menu)
        self.ui_btn_graph_add_tar.setDefaultAction(actions[0])

    def _on_graph_add_build(self, result: QDialog.DialogCode):
        if result == QDialog.DialogCode.Rejected:
            return

        if (
            self.valhalla_build_admins.state() == QProcess.ProcessState.Running
            or self.valhalla_build_tiles.state() == QProcess.ProcessState.Running
        ):
            self._parent.status_bar.pushWarning(
                "Other graph build is currently running, try again after it finished...", 6
            )
            return

        temp_dir = self.graph_dir.joinpath("temp_build_dir")
        inline_config = {"mjolnir": {"admin": str(temp_dir.joinpath("admins.sqlite").resolve())}}

        args = ["-i", json.dumps(inline_config), self.from_pbf_dlg.pbf_path]
        build_admins_exe = ValhallaSettings().get_binary_dir().joinpath("valhalla_build_admins")
        self.valhalla_build_admins.start(str(build_admins_exe.resolve()), args)
        self._parent.status_bar.pushInfo("", "Started building admins...")
        self.dlg_log.text_log.append(
            f"Executing {self.valhalla_build_admins.program()} {' '.join(self.valhalla_build_admins.arguments())}"
        )

    def _on_admins_finished(self, exit_code: int, exit_status: QProcess.ExitStatus):
        self.dlg_log.text_log.append(f"Finished building admins with exit code {exit_code}")
        if exit_status == QProcess.ExitStatus.CrashExit:
            self._parent.status_bar.pushMessage("Building admins failed, see log!", Qgis.Critical, 0)
            return

        self._parent.status_bar.pushMessage("Building admins succeeded...", Qgis.Success, 0)

        temp_dir = self.graph_dir.joinpath("temp_build_dir")
        graph_dir = self.from_pbf_dlg.graph_dir
        inline_config = {
            "mjolnir": {
                "admin": str(temp_dir.joinpath("admins.sqlite")),
                "tile_dir": str(temp_dir.joinpath(graph_dir.name)),
                # TODO: "timezone":
            }
        }

        args = [
            "-i",
            json.dumps(inline_config),
            "-j",
            str(self.from_pbf_dlg.ui_int_threads.value() or os.cpu_count()),
            self.from_pbf_dlg.pbf_path,
        ]
        build_tiles_exe = ValhallaSettings().get_binary_dir().joinpath("valhalla_build_tiles")
        self.valhalla_build_tiles.start(str(build_tiles_exe.resolve()), args)
        self._parent.status_bar.pushInfo("", "Started building graph tiles...")
        self.dlg_log.text_log.append(
            f"Executing {self.valhalla_build_tiles.program()} {' '.join(self.valhalla_build_tiles.arguments())}"
        )

    def _on_tiles_finished(self, exit_code: int, exit_status: QProcess.ExitStatus):
        self.dlg_log.text_log.append(f"Finished building tiles with exit code {exit_code}")
        if exit_status == QProcess.ExitStatus.CrashExit:
            self._parent.status_bar.pushMessage("Building tiles failed, see log!", Qgis.Critical, 0)
            return

        self._parent.status_bar.pushMessage("Building tiles succeeded...", Qgis.Success, 0)

        temp_dir = self.graph_dir.joinpath("temp_build_dir")
        graph_dir = Path(self.from_pbf_dlg.graph_dir).resolve()

        # TODO: produce an extract and remove tile_dir

        # create the id.json
        # TODO: to auto-update the list & combobox we need to create this file at the same time as the directory
        id_json_path = temp_dir.joinpath(ID_JSON)
        with id_json_path.open("w") as f:

            json.dump(
                {
                    "mjolnir": {
                        "tile_dir": str(graph_dir.joinpath(graph_dir.name).resolve()),
                        "tile_extract": str(graph_dir.joinpath(graph_dir.name + ".tar").resolve()),
                        "tile_url": "",
                        "tile_url_user_pw": "",
                    },
                    "loki": {"use_connectivity": True},
                },
                f,
                indent=2,
            )

        # move the whole directory which will finally update the graph list/dropdown
        if graph_dir.exists():
            rmtree(graph_dir)
        move(temp_dir, graph_dir)

    def _check_list_view(self):
        root = self.ui_list_graphs.rootIndex()
        if not self.ui_list_graphs.model().rowCount(root):
            self._parent.status_bar.pushMessage(
                "No graphs", f"Couldn't find any usable graph in {self.graph_dir}", Qgis.Warning, 6
            )

    def _on_build_pbf_log_ready(self):
        log = self.sender().readAll().data().decode()
        self.dlg_log.text_log.append(log)

    def _on_graph_remove(self):
        self.ui_list_graphs: QListView
        idx = self.ui_list_graphs.selectedIndexes()
        if not idx:
            return
        idx = idx[0]
        path = Path(self.graph_dir_model.filePath(self.graph_dir_proxy.mapToSource(idx)))

        # make sure this was not by accident
        ret = QMessageBox.warning(
            self,
            "Remove graph",
            f"You're sure you want to delete\n{path}",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes,
        )

        if ret != QMessageBox.Yes:
            return

        try:
            rmtree(path)
        except:
            pass
        self._parent.status_bar.pushMessage("Removed graph", f"{path.stem}", Qgis.Warning, 3)

    def _on_graph_add_tar(self):
        try:
            in_tar_path = QFileDialog.getOpenFileName(
                self,
                "Import graph",
                QDir.homePath(),
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
                "Graph exists",
                f"The graph {out_tar_dir} already exists. Should it be replaced?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
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
