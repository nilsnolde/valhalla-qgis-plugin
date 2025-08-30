import os.path

from qgis.PyQt.QtCore import QModelIndex, QSortFilterProxyModel


def norm(p):
    return os.path.normcase(os.path.normpath(os.path.abspath(p)))


class FileNameInDirFilterProxy(QSortFilterProxyModel):
    def __init__(self, filename="id.json", parent=None):
        super().__init__(parent)
        self.filename = filename
        self._root_path = None
        # see how this works for QComboBox, could be more resource-intense as well
        self.setDynamicSortFilter(True)

    def setRootPath(self, path: str):
        self._root_path = norm(path)
        self.invalidateFilter()

    def _is_ancestor_of_root(self, path: str) -> bool:
        if not self._root_path:
            return False

        # accept the root and its ancestors so mapFromSource(root) stays valid
        rp = self._root_path
        return path == rp or rp.startswith(path + os.sep)

    # override
    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex) -> bool:
        src = self.sourceModel()
        if not src:
            return False

        idx = src.index(source_row, 0, source_parent)
        if not idx.isValid():
            return False

        path = norm(src.filePath(idx))

        # never filter out the root (or its ancestors); otherwise view root goes invalid.
        if self._is_ancestor_of_root(path):
            return True

        # only show directories that contain id.json
        if not getattr(src, "isDir", lambda i: False)(idx) or not src.isDir(idx):
            return False

        return os.path.exists(os.path.join(path, self.filename))
