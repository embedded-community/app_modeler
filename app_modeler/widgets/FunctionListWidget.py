from PySide6.QtWidgets import QWidget, QTableView, QVBoxLayout, QHeaderView
from PySide6.QtCore import Signal, QModelIndex, Qt
from typing import List
import logging

from app_modeler.models.FunctionCall import FunctionCall
from app_modeler.models.FunctionCallModel import FunctionCallModel

logger = logging.getLogger(__name__)


class FunctionListWidget(QWidget):
    execute_signal = Signal(FunctionCall)
    def __init__(self, allow_execute_behaviour=True):
        super().__init__()
        self.model = FunctionCallModel()
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

        self._allow_execute_behaviour = allow_execute_behaviour

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
        if index.column() == 0 and self._allow_execute_behaviour:
            func = index.data(Qt.ItemDataRole.UserRole)
            logger.debug(f"Editing function '{func.function_name}' with args: {func.args} and kwargs: {func.kwargs}")
            self.execute_signal.emit(func)

    def clear(self):
        self.model.clear()

    def update_items(self, functions: List[FunctionCall]):
        self.model.update_items(functions)

    def append(self, function: FunctionCall):
        self.model.append(function)

    def inject(self, function_call: FunctionCall):
        """Find function name from table and, if found, update args and kwargs for given function call."""
        for idx, func in enumerate(self.model.functions):
            if func.function_name == function_call.function_name:
                function_call.args = func.args
                function_call.kwargs = func.kwargs
                break


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication

    app = QApplication([])
    function_list = [
        FunctionCall(view='view1', function_name="click_tab1", args='"arg1"', kwargs=''),
        FunctionCall(view='view18973498573457346', function_name="click_tab2", args='"arg1"', kwargs='key1="value1"')
    ]
    print([str(func) for func in function_list])
    widget = FunctionListWidget()
    widget.setMinimumSize(600, 400)

    widget.update_items(function_list)
    widget.model.append(FunctionCall(view='view3', function_name="click_tab3273648962387946", args='"arg1"', kwargs='key'))

    widget.show()
    app.exec()
    print('after')
    print([str(func) for func in function_list])
