import os
import operator

from PyQt5 import uic, QtCore
from PyQt5.QtCore import Qt, QAbstractTableModel, QVariant


path = os.path.dirname(os.path.abspath(__file__))
qt_file = os.path.join(path, "UI/RosterPlanner.ui")
form_class = uic.loadUiType(qt_file)[0]


class RecordModel(QAbstractTableModel):
    def __init__(self, parent=None, data=None, header=None):
        QAbstractTableModel.__init__(self, parent)
        self._data = data
        self.header = header

    def rowCount(self, parent=None, *args, **kwargs):
        return len(self._data)

    def columnCount(self, parent=None, *args, **kwargs):
        return len(self._data[0])

    def headerData(self, col, orientation, role=None):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.header[col]
        return QVariant()

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or not 0 <= index.row() < self.rowCount() or not 0 <= index.column() < self.columnCount():
            return QVariant()

        row = index.row()
        col = index.column()

        if role == Qt.DisplayRole:
            return str(self._data[row][col])

        if role == QtCore.Qt.TextAlignmentRole:
            return Qt.AlignHCenter | Qt.AlignVCenter

        return QVariant()

    def sort(self, col, order=None):
        if col != 0:
            self.emit("layoutAboutToBeChanged()")
            self._data = sorted(self._data, key=operator.itemgetter(col))
            if order == Qt.DescendingOrder:
                self._data.reverse()
            self.emit("layoutChanged()")