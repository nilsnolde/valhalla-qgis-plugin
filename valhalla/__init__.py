# -*- coding: utf-8 -*-
"""
/***************************************************************************
Valhalla QGIS Plugin
                              -------------------
        begin                : 2020-02-08
        git sha              : $Format:%H$
        copyright            : (C) 2025 by Nils Nolde
        email                : nilsnolde+github@proton.me
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import configparser
from datetime import datetime
from pathlib import Path

from qgis.gui import QgisInterface


def classFactory(iface: QgisInterface):
    """Load plugin class from file."""
    from .plugin import ValhallaPlugin

    return ValhallaPlugin(iface)


today = datetime.today()

BASE_DIR = Path(__file__).parent.resolve()
METADATA = configparser.ConfigParser()
METADATA.read(BASE_DIR.joinpath("metadata.txt"), encoding="utf-8")
PLUGIN_NAME = METADATA["general"]["name"]
__version__ = METADATA["general"]["version"]
__author__ = METADATA["general"]["author"]
__email__ = METADATA["general"]["email"]
__web__ = METADATA["general"]["homepage"]
__date__ = today.strftime("%Y-%m-%d")
__copyright__ = "(C) {} by {}".format(today.year, __author__)

RESOURCE_PATH = BASE_DIR.joinpath("resources").resolve()
