import re
from typing import List, Any
import logging

from PySide6.QtCore import Qt, QModelIndex, QAbstractTableModel, QObject, Signal

from app_modeler.models.FunctionCall import FunctionCall

logger = logging.getLogger(__name__)


class FunctionCallModel(QAbstractTableModel):
    layoutResetFinished = Signal()  # Custom signal to notify view

    def __init__(self, all_editable: bool = False, parent: QObject = None):
        super().__init__(parent)
        self._all_editable = all_editable
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

        if role in [Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole]:
            if column == 0:
                return func.view
            if column == 1:
                return func.function_name
            elif column == 2:
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
            if column == 0:
                try:
                    FunctionCall(view=value, function_name=func.function_name, args=func.args, kwargs=func.kwargs).test()
                except Exception as error:
                    logger.warning(f'invalid function args: {error}')
                    return False
                func.view = value
            if column == 1:
                try:
                    FunctionCall(view=func.view, function_name=value, args=func.args, kwargs=func.kwargs).test()
                except Exception as error:
                    logger.warning(f'invalid function args: {error}')
                    return False
                func.function_name = value
            if column == 2:
                try:
                    FunctionCall(view=func.view, function_name=func.function_name, args=value, kwargs=func.kwargs).test()
                except Exception as error:
                    logger.warning(f'invalid function args: {error}')
                    return False
                func.args = value
            elif column == 3:
                try:
                    FunctionCall(view=func.view, function_name=func.function_name, args=func.args, kwargs=value).test()
                except Exception as error:
                    logger.warning(f'invalid function kwargs: {error}')
                    return False
                func.kwargs = value
            self.dataChanged.emit(index, index, [role])
            return True
        return False

    def flags(self, index: QModelIndex) -> Qt.ItemFlag:
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags
        column = index.column()
        flags = Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable
        if column == 0 or column == 1:
            if self._all_editable:
                return flags | Qt.ItemFlag.ItemIsEditable
            return flags
        elif column == 2 or column == 3:
            flags |= Qt.ItemFlag.ItemIsEditable
            return flags
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
        assert isinstance(functions, list), f"Expected list, got {type(functions)}"
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

    def update_args(self, function_call: FunctionCall):
        self.beginResetModel()
        for idx, func in enumerate(self.functions):
            if function_call.function_name.startswith('/') and function_call.function_name.endswith('/'):
                is_right = re.match(function_call.function_name[1:-1], func.function_name)
            else:
                is_right = func.function_name == function_call.function_name

            if is_right:
                func.args = function_call.args
                func.kwargs = function_call.kwargs
                break
        self.endResetModel()
        self.layoutResetFinished.emit()
