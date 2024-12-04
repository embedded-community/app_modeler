from PySide6.QtCore import Qt, QModelIndex, QAbstractTableModel, QObject
from typing import List, Any

from app_modeler.models.FunctionCall import FunctionCall


class FunctionCallModel(QAbstractTableModel):

    def __init__(self, parent: QObject = None):
        super().__init__(parent)
        self.functions: List[FunctionCall] = []

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self.functions)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return 3  # Function Name, Args, Kwargs, Operate

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:
        if not index.isValid():
            return None
        func = self.functions[index.row()]
        column = index.column()

        if role == Qt.ItemDataRole.UserRole:
            return func

        if role == Qt.DisplayRole:
            if column == 0:
                return func.function_name
            elif column == 1:
                return func.args
            elif column == 2:
                return func.kwargs
            elif column == 3:
                return ""  # The Operate column will contain a button
        elif role == Qt.EditRole:
            if column == 1:
                return func.args
            elif column == 2:
                return func.kwargs
        return None

    def setData(self, index: QModelIndex, value: Any, role: int = Qt.EditRole) -> bool:
        if not index.isValid():
            return False
        func = self.functions[index.row()]
        column = index.column()

        if role == Qt.EditRole:
            if column == 1:
                func.args = value
            elif column == 2:
                func.kwargs = value
            self.dataChanged.emit(index, index, [role])
            return True
        return False

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        if not index.isValid():
            return Qt.NoItemFlags
        column = index.column()
        if column == 0 or column == 3:
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable  # Read-only
        elif column == 1 or column == 2:
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable
        return Qt.NoItemFlags

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole) -> Any:
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            headers = ['Function Name', 'Args', 'Kwargs']
            if 0 <= section < len(headers):
                return headers[section]
        return super().headerData(section, orientation, role)

    def clear(self):
        self.beginResetModel()
        self.functions = []
        self.endResetModel()

    def update_items(self, functions: List[FunctionCall]):
        self.beginResetModel()
        self.functions = functions
        self.endResetModel()

    def append(self, function: FunctionCall):
        self.beginInsertRows(QModelIndex(), len(self.functions), len(self.functions))
        self.functions.append(function)
        self.endInsertRows()
