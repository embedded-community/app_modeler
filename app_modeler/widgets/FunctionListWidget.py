from PySide6.QtWidgets import QWidget, QTableView, QVBoxLayout, QHeaderView, QMenu
from PySide6.QtCore import Signal, QModelIndex, Qt
from typing import List
import logging

from app_modeler.models.FunctionCall import FunctionCall
from app_modeler.models.FunctionCallModel import FunctionCallModel

logger = logging.getLogger(__name__)

class FunctionListWidget(QWidget):
    execute_signal = Signal(FunctionCall)
    def __init__(self, allow_add_behaviour: bool=False):
        super().__init__()
        self.model = FunctionCallModel(all_editable=allow_add_behaviour)
        self.view = QTableView()
        self.view.setModel(self.model)
        self.view.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.view.setEditTriggers(QTableView.EditTrigger.DoubleClicked |
                                  QTableView.EditTrigger.SelectedClicked |
                                  QTableView.EditTrigger.EditKeyPressed)

        # Extend the last column to fill the remaining table width
        header = self.view.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)  # Default mode for all columns
        header.setSectionResizeMode(self.model.columnCount() - 1, QHeaderView.Stretch)  # Last column stretches

        # Connect model signals to adjust column widths dynamically
        self.model.dataChanged.connect(self.view.resizeColumnsToContents)
        self.model.layoutChanged.connect(self.view.resizeColumnsToContents)
        self.model.rowsInserted.connect(self.view.resizeColumnsToContents)
        self.model.layoutResetFinished.connect(self.view.resizeColumnsToContents)

        self._allow_add_behaviour = allow_add_behaviour
        if allow_add_behaviour:
            self.view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            self.view.customContextMenuRequested.connect(self.on_custom_context_menu)

        # row double click event
        self.view.doubleClicked.connect(self.on_double_clicked)

        layout = QVBoxLayout(self)
        layout.addWidget(self.view)

    def execute_function(self, row: int):
        func = self.model.functions[row]
        logger.debug(f"Executing function '{func.function_name}' with args: {func.args} and kwargs: {func.kwargs}")
        self.execute_signal.emit(func)

    def on_double_clicked(self, index: QModelIndex):
        logger.debug(f"Double clicked on row {index.row()}")
        if index.column() == 0:
            func = index.data(Qt.ItemDataRole.UserRole)
            logger.debug(f"Double click function '{func.function_name}' with args: {func.args} and kwargs: {func.kwargs}")
            self.execute_signal.emit(func)

    def on_custom_context_menu(self, pos):
        menu = QMenu()
        add_row_action = menu.addAction("Add")
        remove_row_action = menu.addAction("Remove")

        action = menu.exec_(self.view.viewport().mapToGlobal(pos))
        if action == add_row_action:
            func = FunctionCall(view='view', function_name='function_name', args='', kwargs='')
            self.model.append(func)
            self.model.layoutResetFinished.emit()
        elif action == remove_row_action:
            selected_rows = self.view.selectionModel().selectedRows()
            for row in selected_rows:
                self.model.functions.pop(row.row())
            self.model.layoutResetFinished.emit()

    def clear(self):
        self.model.clear()

    def update_items(self, functions: List[FunctionCall]):
        self.model.update_items(functions)

    def append(self, function: FunctionCall):
        self.model.append(function)

    def to_dict(self):
        return [func.model_dump() for func in self.model.functions]

    def from_dict(self, data: List[dict]):
        funcs = [FunctionCall(**func) for func in data]
        self.update_items(funcs)

    def inject_many(self, function_list_widget: 'FunctionListWidget'):
        """Inject all functions from given function list widget."""
        for function in function_list_widget.model.functions:
            self.model.update_args(function)

if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication

    app = QApplication([])
    function_list = [
        FunctionCall(view='view1', function_name="click_tab1", args='"arg1"', kwargs=''),
        FunctionCall(view='view18973498573457346', function_name="click_tab2", args='"arg1"', kwargs='key1="value1"')
    ]
    print([str(func) for func in function_list])
    widget = FunctionListWidget(allow_add_behaviour=True)
    widget.setMinimumSize(600, 400)

    widget.update_items(function_list)
    widget.model.append(FunctionCall(view='view3', function_name="click_tab3273648962387946", args='"arg1"', kwargs='key'))

    widget.show()
    app.exec()
    print('after')
    print([str(func) for func in function_list])
