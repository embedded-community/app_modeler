import logging

from PySide6.QtWidgets import QVBoxLayout, QTabWidget, QPushButton, QHBoxLayout, QCheckBox, QGroupBox

from app_modeler.models.ModelerState import ModelerState
from app_modeler.widgets.CodeWidget import CodeWidget
from app_modeler.widgets.SettingsWidget import SettingsWidget

logger = logging.getLogger(__name__)


class BottomMiddleWidget(SettingsWidget):

    def __init__(self, state: ModelerState):
        super().__init__()
        self.state = state
        self._setup_ui()

        self.state.signals.class_propose.connect(self.class_code.setPlainText)
        self.state.signals.elements_propose.connect(self.elements_json.setPlainText)
        self.state.signals.next_func_candidates.connect(self.on_next_func_candidates)
        self.auto_import_checkbox.stateChanged.connect(self.import_button.setDisabled)
        #self.state.signals.execute.connect(self.on_execute)
        self.init_settings(state.settings)

    def _setup_ui(self):
        layout = QVBoxLayout()

        tab = QTabWidget()
        self.class_code = CodeWidget()
        self.elements_json = CodeWidget()
        tab.addTab(self.class_code, "Class")
        tab.addTab(self.elements_json, "Elements")
        layout.addWidget(tab)

        operate_box = QGroupBox()
        operate_layout = QHBoxLayout()

        self.auto_import_checkbox = QCheckBox("Auto import")
        self.auto_import_checkbox.setObjectName("auto_import_checkbox")
        self.import_button = QPushButton("Import")
        self.import_button.clicked.connect(self.on_import)
        operate_layout.addWidget(self.auto_import_checkbox)
        operate_layout.addWidget(self.import_button)

        operate_box.setLayout(operate_layout)

        layout.addWidget(operate_box)

        self.setLayout(layout)

    def on_import(self):
        self.import_module()

    def on_next_func_candidates(self):
        logger.debug("Next function candidates available")
        if self.auto_import_checkbox.isChecked():
            logger.debug("Auto import enabled, importing module")
            self.import_module()

    def import_module(self):
        self.state.signals.import_module.emit()

    def on_execute(self):
        self.class_code.clear()
        self.elements_json.clear()
