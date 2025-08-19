from qgis.core import Qgis, QgsMessageLog

from .. import PLUGIN_NAME


def qgis_log(message, level=Qgis.Info):
    """
    Writes to QGIS inbuilt logger accessible through panel.

    :param message: logging message to write, error or URL.
    :type message: str

    :param level: integer representation of logging level.
    :type level: int
    """

    QgsMessageLog.logMessage(message, PLUGIN_NAME.strip(), level)
