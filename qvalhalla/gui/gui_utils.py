from qgis.gui import QgsMessageBar
from qgis.PyQt.QtWidgets import QLayout, QSizePolicy


def add_msg_bar(layout: QLayout) -> QgsMessageBar:
    """
    Adds a message bar to the passed layout in the first position and returns it.

    :param layout: the layout the message bar should be added to
    :returns: the initialized message bar object
    """
    status_bar = QgsMessageBar()
    status_bar.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
    layout.insertWidget(0, status_bar, 2)

    return status_bar
