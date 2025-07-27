import json
from datetime import datetime
from enum import Enum, unique
from typing import Dict, Optional, Tuple

from qgis.core import QgsNetworkAccessManager, QgsNetworkReplyContent
from qgis.gui import QgisInterface
from qgis.PyQt.QtCore import QUrl
from qgis.PyQt.QtNetwork import QNetworkReply, QNetworkRequest
from qgis.PyQt.QtWidgets import QDialog, QWidget

from .. import BASE_DIR
from ..core.core_definitions import REMOTE_PKG_FN, REMOTE_PKG_FP
from ..core.settings import ValhallaSettings
from ..global_definitions import Dialogs
from ..gui.panels.settings.panel_base import PanelBase
from ..utils.logger_utils import qgis_log
from ..utils.resource_utils import get_icon
from .compiled.dlg_plugin_settings_ui import Ui_PluginSettingsDialog
from .gui_utils import add_msg_bar
from .panels.settings import PanelGeneral

iface: QgisInterface


@unique
class Panels(Enum):
    GENERAL = 0
    # VALHALLA = 1


class PluginSettingsUi(str, Enum):
    AUTH = "ui_account_auth"


# TODO: remember to put the HTTP URL again
# PKG_REQ = QNetworkRequest(QUrl(f"{NetworkAnalystSettings().get_shop_url()}/wp-content/uploads/{REMOTE_PKG_FN}"))
# ORDER_REQ = QNetworkRequest(QUrl(f"{NetworkAnalystSettings().get_shop_url()}/wp-json/wc/v3/gis-ops/orders"))
PKG_REQ = QNetworkRequest(
    QUrl(str(BASE_DIR.joinpath("..", "tests", "mock_data", REMOTE_PKG_FN).resolve().as_uri()))
)
# ORDER_REQ = QNetworkRequest(
#     QUrl(
#         str(
#             BASE_DIR.joinpath("..", "tests", "mock_data", "order_mock.json")
#             .resolve()
#             .as_uri()
#         )
#     )
# )


class PluginSettingsDialog(QDialog, Ui_PluginSettingsDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.menu_widget.currentRowChanged["int"].connect(self.ui_stacked_panels.setCurrentIndex)
        self.menu_widget.setCurrentRow(0)

        # add a status bar
        self.status_bar = add_msg_bar(self.main_layout)

        # set the right auth string
        # auth_id = NetworkAnalystSettings().get(Dialogs.SETTINGS, PluginSettingsUi.AUTH)
        # self.ui_account_auth.setConfigId(auth_id or "")

        self.nam = QgsNetworkAccessManager.instance()
        self.panels: Optional[Dict[Panels, Tuple[PanelBase, str]]] = None
        self.head_res: Optional[QNetworkReply] = None

        # make sure to get the latest version of the premium_pkgs.json before starting the UI
        self.head_res: QNetworkReply = self.nam.head(PKG_REQ)
        self.head_res.finished.connect(self._on_head_finish)

    def _on_head_finish(self):
        """Passes empty premium_pkgs lists to the panels if the network is offline"""
        time_fmt = "%Y-%m-%d %H:%M:%S"
        if self.head_res.error() == QNetworkReply.NoError:
            # inspect the last_modified header of the HEAD request
            last_mod: datetime = self.head_res.header(QNetworkRequest.LastModifiedHeader).toPyDateTime()
            stored_mod = datetime.strptime(
                ValhallaSettings().get(Dialogs.SETTINGS, "package_json_age") or "1970-01-01 00:00:00",
                time_fmt,
            )

            # if the downloaded file is newer than the stored one or doesn't exist, download it
            if last_mod > stored_mod or not REMOTE_PKG_FP.exists():
                meta_res: QgsNetworkReplyContent = self.nam.blockingGet(PKG_REQ, "", True)
                with open(REMOTE_PKG_FP, "w") as f:
                    json.dump(json.loads(bytes(meta_res.content())), f)
                ValhallaSettings().set(
                    Dialogs.SETTINGS,
                    "package_json_age",
                    str(last_mod.strftime(time_fmt)),
                )

                qgis_log(f"Newer pkg_name.json downloaded from {last_mod}")

            # open the JSON and distribute it on the panels
            with open(REMOTE_PKG_FP) as f:
                remote_pkgs = json.load(f)  # noqa: F841
        else:
            # self.status_bar.pushMessage(
            #     "HTTP Error", self.head_res.errorString(), Qgis.Critical, 5
            # )
            remote_pkgs = {"valhalla": [], "osrm": []}  # noqa: F841

        # also get the user's purchases
        # TODO: get the real deal with a client class
        with open(BASE_DIR.joinpath("..", "tests", "mock_data", "order_mock.json")) as f:
            ordered_pkgs = json.load(f)  # noqa: F841

        # finally we can build all the panels
        self.panels = {
            # Panels.VALHALLA: (
            #     PanelValhalla(
            #         self,
            #         [],  #normalize_pkgs(remote_pkgs, ordered_pkgs, RouterType.VALHALLA),
            #     ),
            #     "valhalla.png",
            # ),
            # Panels.OSRM: (
            #     PanelOsrm(
            #         self,
            #         normalize_pkgs(remote_pkgs, ordered_pkgs, RouterType.OSRM),
            #     ),
            #     "osrm.png",
            # ),
            Panels.GENERAL: (
                PanelGeneral(self),
                ":images/themes/default/mActionMapSettings.svg",
            ),
        }
        for idx, (_, (panel, icon_fp)) in enumerate(self.panels.items()):
            self.menu_widget.item(idx).setIcon(get_icon(icon_fp))
            panel.setup_panel()

    def on_settings_change(self, new_text, widget: Optional[QWidget] = ""):
        attr = widget.objectName() if widget else self.sender().objectName()
        ValhallaSettings().set(Dialogs.SETTINGS, attr, str(new_text))
