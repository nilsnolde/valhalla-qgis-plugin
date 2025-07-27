from enum import Enum
from pathlib import Path

from .. import BASE_DIR


class MergeStrategy(str, Enum):
    ROW_BY_ROW = "row by row"
    ALL_BY_ALL = "all by all"


HELP_DIR = BASE_DIR.joinpath(Path("help"))
