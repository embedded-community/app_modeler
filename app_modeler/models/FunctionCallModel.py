from PySide6.QtCore import Qt, QModelIndex, QAbstractTableModel, QObject, Signal
from typing import List, Any

from app_modeler.models.FunctionCall import FunctionCall


class FunctionCallModel(QAbstractTableModel):
    layoutResetFinished = Signal()  # Custom signal to notify view

    def __init__(self, parent: QObject = None):
        super().__init__(parent)
        self.functions: List[FunctionCall] = []
        self._headers = ['View', 'Function Name', 'Args', 'Kwargs']

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self.functions)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self._headers)

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if not index.isValid():
            return None
        func = self.functions[index.row()]
        column = index.column()

        if role == Qt.ItemDataRole.UserRole:
            return func

        if role == Qt.ItemDataRole.DisplayRole:
            if column == 0:
                return func.view
            if column == 1:
                return func.function_name
            elif column == 2:
                return func.args
            elif column == 3:
                return func.kwargs
        elif role == Qt.ItemDataRole.EditRole:
            if column == 2:
                return func.args
            elif column == 3:
                return func.kwargs
        return None

    def setData(self, index: QModelIndex, value: Any, role: int = Qt.ItemDataRole.EditRole) -> bool:
        if not index.isValid():
            return False
        func = self.functions[index.row()]
        column = index.column()

        if role == Qt.ItemDataRole.EditRole:
            if column == 2:
                func.args = value
            elif column == 3:
                func.kwargs = value
            self.dataChanged.emit(index, index, [role])
            return True
        return False

    def flags(self, index: QModelIndex) -> Qt.ItemFlag:
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags
        column = index.column()
        if column == 0 or column == 1:
            return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable  # Read-only
        elif column == 2 or column == 3:
            return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEditable
        return Qt.ItemFlag.NoItemFlags

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            if 0 <= section < len(self._headers):
                return self._headers[section]
        return super().headerData(section, orientation, role)

    def clear(self):
        self.beginResetModel()
        self.functions = []
        self.endResetModel()

    def update_items(self, functions: List[FunctionCall]):
        self.beginResetModel()
        self.functions = functions
        self.endResetModel()
        self.layoutResetFinished.emit()

    def append(self, function: FunctionCall):
        self.beginInsertRows(QModelIndex(), len(self.functions), len(self.functions))
        self.functions.append(function)
        self.endInsertRows()

    def get_data(self) -> List[FunctionCall]:
        return self.functions
