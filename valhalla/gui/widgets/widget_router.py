from qgis.PyQt.QtCore import QSize
from qgis.PyQt.QtWidgets import (
    QButtonGroup,
    QComboBox,
    QFormLayout,
    QHBoxLayout,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QToolButton,
    QWidget,
)

from ...core.settings import ProviderSetting, ValhallaSettings
from ...global_definitions import RouterMethod, RouterProfile, RouterType
from ...gui.dlg_routing_providers import ProviderDialog
from ...utils.resource_utils import get_icon
from ..ui_definitions import RouterWidgetElems

BUTTONS = {
    RouterWidgetElems.PROV_OPT: (
        ":images/themes/default/console/iconProcessingConsole.svg",
        "Provider Manager",
    ),
    RouterWidgetElems.PED: ("pedestrian.svg", "Bike mode"),
    RouterWidgetElems.BIKE: ("bike.svg", "Bike mode"),
    RouterWidgetElems.CAR: ("car.svg", "Car mode"),
    RouterWidgetElems.TRUCK: ("truck.svg", "Truck mode"),
    RouterWidgetElems.MBIKE: ("motorbike.svg", "Motorbike mode"),
}


PROFILE_TO_UI = {
    RouterWidgetElems.PED: RouterProfile.PED,
    RouterWidgetElems.BIKE: RouterProfile.BIKE,
    RouterWidgetElems.CAR: RouterProfile.CAR,
    RouterWidgetElems.TRUCK: RouterProfile.TRUCK,
    RouterWidgetElems.MBIKE: RouterProfile.MBIKE,
}


FILE_EXT = {RouterType.VALHALLA: ".tar", RouterType.OSRM: ".osrm"}


# TODO: make this class a singleton so every dialog gets the same instance
#   mainly useful for the QFileSystemWatcher
class RouterWidget(QWidget):
    def __init__(self, parent_dlg: QWidget = None):
        super().__init__(parent_dlg)
        self.setupUi()

        self._populate_providers()

        # assign and update the provider & method
        self._on_provider_method_changed()
        self._profile = RouterProfile.PED

        # add a directory watcher to get notified when a package was downloaded
        # self.watcher = QFileSystemWatcher()
        # for e in RouterType:
        #     path = get_settings_dir().joinpath(e.lower())
        #     path.mkdir(exist_ok=True, parents=True)
        #     self.watcher.addPath(str(path))

        # connections
        self.ui_cmb_prov.currentIndexChanged.connect(self._on_provider_method_changed)
        self.mode_btns.buttonToggled.connect(self._on_profile_change)
        # self.watcher.directoryChanged.connect(self._populate_providers)

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

    def _on_provider_method_changed(self):
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

        # and all the local packages
        # for prov in self.watcher.directories():
        #     router = os.path.basename(prov).lower()
        #     prov_display = (
        #         router.capitalize() if router == RouterType.VALHALLA else router.upper()
        #     )
        #     for pkg_path in Path(prov).iterdir():
        #         self.ui_cmb_prov.addItem(
        #             f"{prov_display} – {pkg_path.name}",
        #             (RouterType(router), RouterMethod.LOCAL, pkg_path.name),
        #         )

        self.ui_cmb_prov.blockSignals(False)

    def update_profile_buttons(self):
        btn: QToolButton
        for btn in self.mode_btns.buttons():
            if btn.objectName() in (RouterWidgetElems.TRUCK, RouterWidgetElems.MBIKE):
                btn.setEnabled(self._router == RouterType.VALHALLA)

        # switch to PED when provider is OSRM and non-available profile is selected
        getattr(self, RouterWidgetElems.PED.value).setChecked(
            self.router == RouterType.OSRM and self.profile in (RouterProfile.MBIKE, RouterProfile.TRUCK)
        )

    def setupUi(self):
        tool_buttons = {
            # RouterWidgetElems.PROV_OPT: (
            #     ":images/themes/default/console/iconProcessingConsole.svg",
            #     "Provider Manager",
            # ),
            RouterWidgetElems.PED: ("pedestrian.svg", "Pedestrian mode"),
            RouterWidgetElems.BIKE: ("bike.svg", "Bike mode"),
            RouterWidgetElems.CAR: ("car.svg", "Car mode"),
            RouterWidgetElems.TRUCK: ("truck.svg", "Truck mode"),
            RouterWidgetElems.MBIKE: ("motorbike.svg", "Motorbike mode"),
        }
        # first set up the buttons, then later add them where needed
        for btn_enum, (icon, tip) in tool_buttons.items():
            btn = QToolButton(self)
            btn.setIcon(get_icon(icon))
            btn.setObjectName(btn_enum.value)
            btn.setIconSize(QSize(24, 24))
            btn.setToolTip(tip)
            btn.setCheckable(True)
            setattr(self, btn_enum.value, btn)

        self.outer_layout = QFormLayout(self)

        # the upper row, i.e. providers
        self.provider_field = QHBoxLayout(self)
        self.ui_cmb_prov = QComboBox(self)
        self.ui_cmb_prov.setObjectName(RouterWidgetElems.PROV_COMBO.value)
        self.ui_btn_prov_options = QPushButton()
        self.ui_btn_prov_options.setObjectName(RouterWidgetElems.PROV_OPT.value)
        self.ui_btn_prov_options.setIcon(get_icon("server.svg"))
        self.ui_btn_prov_options.setIconSize(QSize(24, 24))
        self.ui_btn_prov_options.setFixedSize(self.ui_cmb_prov.height(), self.ui_cmb_prov.height())
        self.ui_btn_prov_options.clicked.connect(self._on_btn_prov_options_clicked)

        self.provider_field.addWidget(self.ui_cmb_prov)
        self.provider_field.addWidget(self.ui_btn_prov_options)

        self.outer_layout.addRow("Provider", self.provider_field)

        # the lower row, i.e. profiles
        self.profile_layout = QHBoxLayout(self)
        self.mode_btns = QButtonGroup()
        self.mode_btns.setExclusive(True)
        for btn_enum in PROFILE_TO_UI.keys():
            btn = getattr(self, btn_enum.value)
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
