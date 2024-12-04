import logging

from PySide6.QtWidgets import QLabel, QVBoxLayout, QGroupBox, QHBoxLayout, QCheckBox, QWidget, QTabWidget

from app_modeler.models.FunctionCall import FunctionCall
from app_modeler.models.ModelerState import ModelerState
from app_modeler.widgets.FunctionListWidget import FunctionListWidget
from app_modeler.widgets.SettingsWidget import SettingsWidget

logger = logging.getLogger(__name__)


class BottomRightWidget(SettingsWidget):
    def __init__(self, state: ModelerState):
        super().__init__()
        self.state = state
        self._setup_ui()
        self._connect_signals()
        self.init_settings(state.settings)

    def _setup_ui(self):
        layout = QVBoxLayout()

        tab = QTabWidget()
        self.choices = QWidget()
        self.choices_layout = QVBoxLayout()
        self.choices.setLayout(self.choices_layout)
        self.history = QWidget()
        self.history_layout = QVBoxLayout()
        self.history.setLayout(self.history_layout)

        tab.addTab(self.choices, "Choices")
        tab.addTab(self.history, "History")
        layout.addWidget(tab)

        self.api_list = FunctionListWidget()
        self.choices_layout.addWidget(self.api_list)

        self.history_list = FunctionListWidget()
        self.history_layout.addWidget(self.history_list)

        operate_box = QGroupBox()
        operate_layout = QHBoxLayout()
        self.auto_select_checkbox = QCheckBox("Auto select and execute")
        self.auto_select_checkbox.setObjectName("auto_select_checkbox")
        operate_layout.addWidget(self.auto_select_checkbox)
        operate_box.setLayout(operate_layout)
        layout.addWidget(operate_box)

        self.setLayout(layout)

    def _connect_signals(self):
        self.state.signals.next_func_candidates.connect(self.on_next_function_candidates_available)
        self.state.signals.module_imported.connect(self.on_module_imported)
        self.api_list.execute_signal.connect(self.on_execute)

    def on_next_function_candidates_available(self):
        logger.debug("Updating function candidates")
        self.update_list()

    def on_module_imported(self):
        # enable app_list execute functionality
        logger.debug("on_module_imported:Module imported")
        self.update_list()
        if self.auto_select_checkbox.isChecked():
            logger.debug("Auto select and execute enabled, executing first function")
            self.on_execute(self.api_list.model.functions[0])

    def on_execute(self, function_call: FunctionCall):
        logger.debug(f"Executing function: {function_call}")
        self.state.signals.execute.emit(str(function_call))
        self.history_list.append(function_call)
        #self.api_list.clear()

    def update_list(self):
        view = self.state.current_view
        self.api_list.clear()
        self.api_list.update_items(view.function_candidates)
