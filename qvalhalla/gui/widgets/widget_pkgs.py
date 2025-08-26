import os
import webbrowser
from datetime import datetime
from enum import Enum
from functools import partial
from pathlib import Path
from typing import Optional

from qgis.core import Qgis
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QToolButton, QTreeWidget, QTreeWidgetItem, QWidget

from ...core.settings import ValhallaSettings
from ...global_definitions import RouterType
from ...utils.downloader import Downloader
from ...utils.geom_utils import decode_polyline
from ...utils.resource_utils import get_local_pkg_path


class PkgTypes(Enum):
    FREE = "Free"
    PREMIUM = "Premium"
    PURCHASED = "Purchased"


class PkgWidget(QTreeWidget):
    def __init__(
        self,
        parent_widget: Optional[QWidget],
        all_pkgs: list,
        router: RouterType,
    ):
        super().__init__()
        self.parent = parent_widget
        self.router = router

        # set basics for the table widget
        self.setColumnCount(3)
        self.setHeaderLabels(["Region", "Data Date", ""])
        self.setIndentation(10)

        # section size is the column width basically
        self.header().setDefaultSectionSize(100)
        self.header().setMinimumSectionSize(32)
        # self.header().setSectionResizeMode(0, QHeaderView.ResizeToContents)

        all_pkgs = {
            PkgTypes.PURCHASED: filter(
                lambda pkg: pkg.is_purchased is True and pkg.free is False,
                all_pkgs,
            ),
            PkgTypes.PREMIUM: filter(
                lambda pkg: pkg.is_purchased is False and pkg.free is False,
                all_pkgs,
            ),
            PkgTypes.FREE: filter(
                lambda pkg: pkg.is_purchased is False and pkg.free is True,
                all_pkgs,
            ),
        }

        # keep a reference to the geometries
        self.pkg_geoms = dict()

        get_date = (
            lambda fp: datetime.utcfromtimestamp(Path(fp).stat().st_mtime).strftime("%Y-%m-%d")
            if fp
            else ""
        )

        # add the top level items
        for pkg_type, pkg_it in all_pkgs.items():
            top_item = QTreeWidgetItem([pkg_type.value, "", ""])
            self.addTopLevelItem(top_item)
            # then add the sub-items
            for pkg in pkg_it:
                item = QTreeWidgetItem(top_item)
                item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                item.setText(0, pkg.name)
                item.setToolTip(0, pkg.name)
                item.setText(1, get_date(pkg.local_fp))

                # depending on free or premium we want different things to happen
                icon, tooltip, callback = None, None, None
                if pkg_type == PkgTypes.PURCHASED:
                    callback = partial(self._on_click_download, pkg.filename, pkg_type)
                    if pkg.local_fp:
                        icon = ":images/themes/default/mActionReload.svg"
                        tooltip = f"Update {pkg.name}"
                    else:
                        icon = ":images/themes/default/downloading_svg.svg"
                        tooltip = f"Download {pkg.name}"
                elif pkg_type == PkgTypes.PREMIUM:
                    icon = ":images/themes/default/mIconFileLink.svg"
                    tooltip = "Go to shop"
                    callback = partial(webbrowser.open, f"https://gis-ops.com/{pkg.name}")
                elif pkg_type == PkgTypes.FREE:
                    if os.path.exists(pkg.local_fp):
                        item.setText(2, "No updates")
                    else:
                        callback = partial(self._on_click_download, pkg.filename, pkg_type)
                        icon = ":images/themes/default/downloading_svg.svg"
                        tooltip = f"Download {pkg.name}"

                if icon is not None and tooltip is not None and callback is not None:
                    btn = QToolButton(self)
                    btn.setIcon(QIcon.fromTheme(icon))
                    btn.setToolTip(tooltip)
                    btn.clicked.connect(callback)
                    self.setItemWidget(item, 2, btn)

                self.pkg_geoms[pkg.name] = decode_polyline(pkg.polyline)

        self.header().resizeSection(2, 32)
        self.resizeColumnToContents(1)

    def _on_click_download(self, filename: str, pkg_type: PkgTypes):
        pkg_path = get_local_pkg_path(filename, self.router)
        # if file exists, don't download again..
        if pkg_path.exists() and pkg_type == PkgTypes.FREE:
            self.parent.status_bar.pushMessage(
                "Package exists",
                f"Package {filename} already exists.",
                Qgis.Warning,
                5,
            )
            return

        url = f"{ValhallaSettings().get_shop_url()}/wp-content/uploads/{filename}"
        # will start the download right away; needs to be an instance attribute
        # or it'll be GCd
        self.downloader = Downloader(url, pkg_path, self.parent.status_bar)
