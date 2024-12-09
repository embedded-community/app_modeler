import json
import logging
from pathlib import Path

from PySide6.QtWidgets import QVBoxLayout, QGroupBox, QHBoxLayout, QCheckBox, QWidget, QTabWidget, QPushButton, \
    QFileDialog, QMessageBox

from app_modeler.models.FunctionCall import FunctionCall
from app_modeler.models.ModelerState import ModelerState
from app_modeler.utils.TestGenerator import TestGenerator
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
        self.load_default_injects()

    def _setup_ui(self):
        layout = QVBoxLayout()

        tab = QTabWidget()
        self.choices = QWidget()
        self.choices_layout = QVBoxLayout()
        self.choices.setLayout(self.choices_layout)
        self.history = QWidget()
        self.history_layout = QVBoxLayout()
        self.history.setLayout(self.history_layout)


        self.inject = QWidget()
        self.inject_layout = QVBoxLayout()
        self.inject.setLayout(self.inject_layout)

        tab.addTab(self.choices, "Choices")
        tab.addTab(self.inject, "Inject")
        tab.addTab(self.history, "Call History")
        layout.addWidget(tab)

        # Choices tab
        self.api_list = FunctionListWidget()
        self.choices_layout.addWidget(self.api_list)
        choises_operate_box = QGroupBox()
        choises_operate_layout = QHBoxLayout()
        self.inject_now_button = QPushButton("Inject")
        self.inject_now_button.setToolTip("Inject arguments from the Inject tab")
        choises_operate_layout.addWidget(self.inject_now_button)
        choises_operate_box.setLayout(choises_operate_layout)
        self.choices_layout.addWidget(choises_operate_box)

        # Inject tab
        self.inject_list = FunctionListWidget(allow_add_behaviour=True)
        self.inject_layout.addWidget(self.inject_list)
        inject_operate_box = QGroupBox()
        inject_operate_layout = QHBoxLayout()
        self.injects_import_button = QPushButton("Import")
        self.injects_export_button = QPushButton("Export")
        inject_operate_layout.addWidget(self.injects_import_button)
        inject_operate_layout.addWidget(self.injects_export_button)
        inject_operate_box.setLayout(inject_operate_layout)
        self.inject_layout.addWidget(inject_operate_box)


        # Call history tab
        self.history_list = FunctionListWidget()
        self.history_layout.addWidget(self.history_list)
        history_operate_box = QGroupBox()
        history_operate_layout = QHBoxLayout()
        self.history_export_button = QPushButton("Export test scenario")
        self.history_export_button.setToolTip("Export reproducible pytest test project")
        self.clean_history_button = QPushButton("Clean history")
        history_operate_layout.addWidget(self.clean_history_button)
        history_operate_layout.addWidget(self.history_export_button)
        history_operate_box.setLayout(history_operate_layout)
        self.history_layout.addWidget(history_operate_box)

        # Operate
        operate_box = QGroupBox()
        operate_layout = QHBoxLayout()

        self.auto_inject_checkbox = QCheckBox("Auto inject")
        self.auto_inject_checkbox.setToolTip("Automatically inject the pre-defined function arguments")
        self.auto_inject_checkbox.setObjectName("auto_inject_checkbox")
        operate_layout.addWidget(self.auto_inject_checkbox)

        self.auto_select_checkbox = QCheckBox("Auto execute")
        self.auto_select_checkbox.setToolTip("Execute the first function. Sorted by AI with given prompt")
        self.auto_select_checkbox.setObjectName("auto_select_checkbox")
        operate_layout.addWidget(self.auto_select_checkbox)
        operate_box.setLayout(operate_layout)

        layout.addWidget(operate_box)

        self.setLayout(layout)

    def _connect_signals(self):
        self.state.signals.next_func_candidates.connect(self.on_next_function_candidates_available)
        self.state.signals.module_imported.connect(self.on_module_imported)
        self.state.signals.executed.connect(self.history_list.append)
        self.api_list.execute_signal.connect(self.on_execute)
        self.injects_export_button.clicked.connect(self.on_injects_export)
        self.injects_import_button.clicked.connect(self.on_injects_import)
        self.auto_inject_checkbox.stateChanged.connect(self.inject_now_button.setDisabled)
        self.inject_now_button.clicked.connect(self.on_inject)
        self.history_export_button.clicked.connect(self.on_history_export)
        self.clean_history_button.clicked.connect(self.history_list.clear)

    def on_next_function_candidates_available(self):
        logger.debug("Updating function candidates")
        self.update_list()

    def on_module_imported(self):
        # enable app_list execute functionality
        logger.debug("on_module_imported:Module imported")
        self.update_list()
        if self.auto_inject_checkbox.isChecked():
            logger.debug("Auto import and inject enabled, injecting first function")
            self.on_inject()
        if self.auto_select_checkbox.isChecked():
            logger.debug("Auto select and execute enabled, executing first function")
            self.on_execute(self.api_list.model.functions[0])

    def on_execute(self, function_call: FunctionCall):
        logger.debug(f"Executing function: {function_call}")
        self.state.signals.execute.emit(function_call)

    def update_list(self):
        view = self.state.current_view
        self.api_list.clear()
        self.api_list.update_items(view.function_candidates)

    def on_injects_export(self):
        data_to_save = self.inject_list.to_dict()
        # open file dialog for save json file
        file_path, _ = QFileDialog.getSaveFileName(self, "Export JSON File", "", "JSON Files (*.json)")
        if file_path:
            with open(file_path, 'w') as file:
                json.dump(data_to_save, file, indent=4)
                self.store_inject_filename(file_path)

    @staticmethod
    def get_inject_settings_key():
        return "AppModeler/BottomRightWidget/inject_filename"

    def store_inject_filename(self, file_path):
        self.state.settings.setValue(self.get_inject_settings_key(), file_path)

    def load_default_injects(self):
        file_path = self.state.settings.value(self.get_inject_settings_key())
        if not file_path:
            return

        if not Path(file_path).exists():
            return

        self.inject_file(file_path)

    def on_injects_import(self):
        # open file dialog for open json file
        file_path, _ = QFileDialog.getOpenFileName(self, "Import JSON File", "", "JSON Files (*.json)")
        if file_path:
            self.inject_file(file_path)
            self.store_inject_filename(file_path)

    def inject_file(self, file_path):
        with open(file_path, 'r') as file:
            data = json.load(file)
            self.inject_list.from_dict(data)

    def on_inject(self):
        logger.debug("Injecting functions")
        self.api_list.inject_many(self.inject_list)

    def on_history_export(self):
        # open file dialog for save json file
        output_path = QFileDialog.getExistingDirectory(self, "Export History")
        if not output_path:
            return

        tg = TestGenerator(start_options=self.state.appium_options,
                      session=self.state.session)
        files = tg.generate(output_path)
        logger.info(f"Generated files: {files}")
        names = [Path(f).name for f in files]

        QMessageBox.information(self,
                                "Export success",
                                f"Exported to {output_path:}\n* {'\n* '.join(names)}")
