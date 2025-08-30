import json
import platform

from qgis.core import Qgis
from qgis.PyQt.QtCore import QDir, QProcess, QSize
from qgis.PyQt.QtWidgets import (
    QButtonGroup,
    QComboBox,
    QFileSystemModel,
    QFormLayout,
    QHBoxLayout,
    QSizePolicy,
    QSpacerItem,
    QToolButton,
    QWidget,
)

from ...core.settings import ProviderSetting, ValhallaSettings
from ...global_definitions import RouterMethod, RouterProfile, RouterType
from ...gui.dlg_plugin_settings import PluginSettingsDialog
from ...gui.dlg_routing_providers import ProviderDialog
from ...gui.dlg_server_log import ServerLogDialog
from ...utils.misc_utils import deep_merge
from ...utils.qt_utils import FileNameInDirFilterProxy
from ...utils.resource_utils import check_valhalla_installation, get_icon, get_valhalla_config_path
from ..ui_definitions import ID_JSON, RouterWidgetElems

PROFILE_TO_UI = {
    RouterWidgetElems.PED: RouterProfile.PED,
    RouterWidgetElems.BIKE: RouterProfile.BIKE,
    RouterWidgetElems.CAR: RouterProfile.CAR,
    RouterWidgetElems.TRUCK: RouterProfile.TRUCK,
    RouterWidgetElems.MBIKE: RouterProfile.MBIKE,
}


# TODO: make this class a singleton so every dialog gets the same instance
#   mainly useful for the QFileSystemWatcher
class RouterWidget(QWidget):
    def __init__(self, parent_dlg: QWidget = None):
        super().__init__()
        self._parent = parent_dlg
        self.setupUi()

        self.settings_dlg = PluginSettingsDialog(self)
        graph_dir = ValhallaSettings().get_graph_dir()

        self._populate_providers()
        self._on_graph_changed(self.ui_cmb_graphs.currentText())

        # assign and update the provider & method
        self._on_provider_method_changed()
        self._profile = RouterProfile.PED

        # connections
        self.ui_cmb_prov.currentIndexChanged.connect(self._on_provider_method_changed)
        self.mode_btns.buttonToggled.connect(self._on_profile_change)
        self.ui_btn_prov_options.clicked.connect(self._on_btn_prov_options_clicked)

        # TODO: https://github.com/kevinkreiser/prime_server/pull/137
        # Windows has no service support yet, so no need to enable local servers
        if platform.system() == "Windows":
            self.ui_btn_server_start.setEnabled(False)
            self.ui_btn_server_stop.setEnabled(False)
            self.ui_btn_server_log.setEnabled(False)
            self.ui_btn_server_conf.setEnabled(False)
            self.ui_cmb_graphs.setEnabled(False)
            return

        # below ONLY for linux/osx

        # the process which will start a local valhalla server
        self.valhalla_service = QProcess(self)
        self.valhalla_service.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        self.dlg_server_log = ServerLogDialog()

        # make the combobox use a similar view/model as the GraphWidget
        self.graph_dir_model = QFileSystemModel()
        self.graph_dir_model.setFilter(QDir.Filter.NoDotAndDotDot | QDir.Filter.Dirs)
        self.graph_dir_model.setRootPath(str(graph_dir.resolve()))

        self.graph_dir_proxy = FileNameInDirFilterProxy(ID_JSON)
        self.graph_dir_proxy.setSourceModel(self.graph_dir_model)
        self.graph_dir_proxy.setRootPath(str(graph_dir.resolve()))

        self.ui_cmb_graphs.setModel(self.graph_dir_proxy)
        self.ui_cmb_graphs.setModelColumn(0)
        root_idx = self.graph_dir_model.index(str(graph_dir.resolve()))
        self.ui_cmb_graphs.setRootModelIndex(self.graph_dir_proxy.mapFromSource(root_idx))

        # more connections
        self.ui_btn_server_conf.clicked.connect(self._on_settings_clicked)
        self.ui_btn_server_start.clicked.connect(self._on_server_start)
        self.ui_btn_server_stop.clicked.connect(self._on_server_stop)
        self.ui_btn_server_log.clicked.connect(self.dlg_server_log.show)
        self.ui_cmb_graphs.currentTextChanged.connect(self._on_graph_changed)
        self.valhalla_service.readyReadStandardOutput.connect(self._on_server_log_ready)
        self.valhalla_service.stateChanged.connect(self._on_server_state_changed)
        self.graph_dir_model.directoryLoaded.connect(self.graph_dir_proxy.invalidateFilter)

    @property
    def router(self) -> RouterType:
        return self._router

    @property
    def provider(self) -> ProviderSetting:
        return self._provider

    @property
    def method(self) -> RouterMethod:
        return self._method

    @property
    def package_path(self) -> str:
        return self._package_path

    @property
    def profile(self) -> RouterProfile:
        return self._profile

    @profile.setter
    def profile(self, profile):
        self._profile = profile

    def _on_graph_changed(self, new_name):
        if not new_name:
            return

        # load the current graph settings (tile_dir etc)
        graph_dir = ValhallaSettings().get_graph_dir()
        id_json = graph_dir.joinpath(new_name, ID_JSON).resolve()
        with id_json.open("r") as f:
            graph_settings = json.load(f)

        # overwrite valhalla.json with those graph settings
        config = get_valhalla_config_path()
        if not config.exists():
            return

        with config.open("r+") as f:
            valhalla_settings = json.load(f)
            new_settings = deep_merge(valhalla_settings, graph_settings)
            f.seek(0)
            f.truncate()
            json.dump(new_settings, f, indent=2)

    def _on_server_state_changed(self, new_state: QProcess.ProcessState):
        # default to QProcess.ProcessState.Running
        msg = "Local Valhalla server started"
        level = Qgis.Info
        if new_state == QProcess.ProcessState.NotRunning:
            msg = "Local Valhalla server stopped"
            level = Qgis.Warning
        elif new_state == QProcess.ProcessState.Starting:
            return

        self._parent.status_bar.pushMessage(msg, level, 3)

    def _on_server_log_ready(self):
        log = self.valhalla_service.readAll().data().decode()
        self.dlg_server_log.text_log.append(log)

    def _on_server_start(self):
        binary_dir = ValhallaSettings().get_binary_dir()
        no_binary_dir = False
        msg = "Can't find Valhalla executables."
        level = Qgis.Critical
        if not binary_dir:
            no_binary_dir = True
        elif not binary_dir.exists():
            no_binary_dir = True
        if not check_valhalla_installation():
            level = Qgis.Critical if no_binary_dir else Qgis.Warning
            no_binary_dir = no_binary_dir or False
            msg += " pyvalhalla-weekly is not installed."

        if no_binary_dir:
            self._parent.status_bar.pushMessage(msg, level, 6)
            self.settings_dlg.open()
            return

        args = [str(get_valhalla_config_path()), "1"]

        # need to run the executable directly
        # with "python -m valhalla xxx" it'd run 2 processes and only kill the first/outer one
        valhalla_service = binary_dir.joinpath("valhalla_service")
        self.valhalla_service.start(str(valhalla_service.resolve()), args)
        self.dlg_server_log.text_log.append(
            f"Started {valhalla_service} with PID {self.valhalla_service.processId()}..."
        )

    def _on_server_stop(self):
        if self.valhalla_service.state() == QProcess.ProcessState.NotRunning:
            return
        self.dlg_server_log.text_log.append("Stopping valhalla service...")
        self.valhalla_service.kill()

    def _on_settings_clicked(self):
        self.settings_dlg.show()

    def _on_provider_method_changed(self):
        if self.ui_cmb_prov.currentIndex() == -1:
            return

        (
            self._router,
            self._method,
            self._package_path,
            self._provider,
        ) = self.ui_cmb_prov.currentData()

    def _on_profile_change(self):
        self._profile = PROFILE_TO_UI[RouterWidgetElems(self.mode_btns.checkedButton().objectName())]

    def _populate_providers(self):
        """Fill the provider's combobox"""
        # need to block signals here, another function also connects to the
        # combobox's signal and would be triggered otherwise
        self.ui_cmb_prov.blockSignals(True)

        prev_idx = self.ui_cmb_prov.currentIndex()
        self.ui_cmb_prov.clear()

        # first add the remote options
        for provider in ValhallaSettings().get_providers(RouterType.VALHALLA):
            self.ui_cmb_prov.addItem(
                provider.name, (RouterType.VALHALLA, RouterMethod.REMOTE, "", provider)
            )

        # jump to previous combobox index if it's all valid
        if prev_idx != -1 and self.ui_cmb_prov.count() >= (prev_idx + 1):
            self.ui_cmb_prov.setCurrentIndex(prev_idx)

        self.ui_cmb_prov.blockSignals(False)

    def setupUi(self):
        def add_btn(btn_name: str, icon: str, tip: str, checkable=True) -> QToolButton:
            btn = QToolButton(self)
            btn.setIcon(get_icon(icon))
            btn.setObjectName(btn_name)
            btn.setIconSize(QSize(24, 24))
            btn.setToolTip(tip)
            btn.setCheckable(checkable)
            setattr(self, btn_name, btn)

            return btn

        self.outer_layout = QFormLayout(self)

        # the upper row, i.e. providers
        self.provider_field = QHBoxLayout(self)
        self.ui_cmb_prov = QComboBox(self)
        self.ui_cmb_prov.setObjectName(RouterWidgetElems.PROV_COMBO.value)
        add_btn(RouterWidgetElems.PROV_OPT.value, "server.svg", "Server manager", False)

        self.provider_field.addWidget(self.ui_cmb_prov)
        self.provider_field.addWidget(self.ui_btn_prov_options)

        self.outer_layout.addRow("Provider", self.provider_field)

        # the middle row, i.e. local server
        self.server_layout = QHBoxLayout(self)
        for btn_name, (icon, tip) in {
            RouterWidgetElems.SERVER_START: (
                ":images/themes/default/mActionStart.svg",
                "Start a local Valhalla server",
            ),
            RouterWidgetElems.SERVER_STOP: (
                ":images/themes/default/mActionStop.svg",
                "Stop the local Valhalla server",
            ),
        }.items():
            self.server_layout.addWidget(add_btn(btn_name, icon, tip, False))
        self.ui_cmb_graphs = QComboBox(self)
        self.ui_cmb_graphs.setObjectName(RouterWidgetElems.SERVER_GRAPHS_COMBO.value)
        self.ui_cmb_graphs.setToolTip("List of locally available graphs")
        self.server_layout.addWidget(self.ui_cmb_graphs)
        for btn_name, (icon, tip) in {
            RouterWidgetElems.SERVER_CONF: (
                ":images/themes/default/propertyicons/layerconfiguration.svg",
                "Configure the local server",
            ),
            RouterWidgetElems.SERVER_LOG: (
                ":images/themes/default/mMessageLog.svg",
                "View local server logs",
            ),
        }.items():
            self.server_layout.addWidget(add_btn(btn_name, icon, tip, False))

        self.outer_layout.addRow("Local Server", self.server_layout)

        # the lower row, i.e. profiles
        mode_buttons = {
            RouterWidgetElems.PED: ("pedestrian.svg", "Pedestrian mode"),
            RouterWidgetElems.BIKE: ("bike.svg", "Bike mode"),
            RouterWidgetElems.CAR: ("car.svg", "Car mode"),
            RouterWidgetElems.TRUCK: ("truck.svg", "Truck mode"),
            RouterWidgetElems.MBIKE: ("motorbike.svg", "Motorbike mode"),
        }
        self.profile_layout = QHBoxLayout(self)
        self.mode_btns = QButtonGroup()
        self.mode_btns.setExclusive(True)
        for btn_enum, (icon, tip) in mode_buttons.items():
            btn = add_btn(btn_enum.value, icon, tip)
            self.mode_btns.addButton(btn)
            self.profile_layout.addWidget(btn)
        self.mode_btns.buttons()[0].setChecked(True)  # set pedestrian as checked button

        self.profile_layout.insertSpacerItem(
            5, QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        )
        self.outer_layout.addRow("Profile", self.profile_layout)

    def _on_btn_prov_options_clicked(self):
        dlg = ProviderDialog(self)
        dlg.exec()
        # refresh the combobox
        self._populate_providers()
