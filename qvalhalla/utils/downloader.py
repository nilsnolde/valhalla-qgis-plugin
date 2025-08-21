from pathlib import Path
from typing import List

from qgis.core import Qgis, QgsFileDownloader
from qgis.gui import QgisInterface, QgsMessageBar, QgsMessageBarItem
from qgis.PyQt.QtCore import Qt, QUrl
from qgis.PyQt.QtWidgets import QProgressBar, QPushButton

from .resource_utils import decompress_pkg

iface: QgisInterface


class Downloader:
    def __init__(self, url: str, fp: Path, status_bar: QgsMessageBar):
        """
        Wraps :class:`QgsFileDownloader` to asynchronously download files. Mostly
        useful for big files: it gives the user the opportunity to cancel the
        download at any time. Download will start immediately. All signals are
        connected to the iface.messageBar
        """
        self.url = url
        self.fp: Path = fp
        self.status_bar = status_bar

        self.downloader = QgsFileDownloader(QUrl(url), str(fp), "", True)
        self.downloader.downloadError.connect(self._on_error)
        self.downloader.downloadProgress.connect(self._on_progress)
        self.downloader.downloadCompleted.connect(self._on_success)
        self.downloader.downloadCanceled.connect(self._on_canceled)

        # set up the progress bar already
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(100)
        self.progress_bar.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        progress_msg: QgsMessageBarItem = self.status_bar.createMessage("Download Progress: ")
        progress_msg.layout().addWidget(self.progress_bar)

        # button for canceling
        self.cancel_btn: QPushButton = QPushButton()
        self.cancel_btn.setText("Abort")
        self.cancel_btn.clicked.connect(self.downloader.cancelDownload)
        progress_msg.layout().addWidget(self.cancel_btn)

        self.status_bar.pushWidget(progress_msg, Qgis.Info)

        # start the download
        self.downloader.startDownload()

    def _on_error(self, errors: List[str]):
        """handles errors of the asynchronous file downloader"""
        self.status_bar.clearWidgets()
        self.status_bar.pushMessage(
            f"Download Error for {self.url}",
            "{}".format("\n".join(errors)),
            Qgis.Critical,
            8,
        )

    def _on_progress(self, received: int, total: int):
        """report progress to the message bar"""
        if not received or not total:
            return

        self.progress_bar.setValue(received / total * 100)

    def _on_success(self, url: QUrl):
        """tell the user it's done"""
        self.status_bar.clearWidgets()
        decompress_pkg(self.fp)
        self.status_bar.pushMessage(
            "Download Finished",
            f"Find the package at {self.fp}",
            Qgis.Success,
            5,
        )

    def _on_canceled(self):
        """When the user hit the cancel button in the message bar"""
        self.status_bar.clearWidgets()
        self.status_bar.pushMessage("Download Canceled", "", Qgis.Warning, 5)
