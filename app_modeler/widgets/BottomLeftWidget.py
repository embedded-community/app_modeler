from time import sleep

from PySide6.QtWidgets import QVBoxLayout, QGroupBox, QHBoxLayout, QPushButton, QCheckBox

from app_modeler.models.ModelerState import ModelerState
from app_modeler.widgets.ImageWidget import ImageWidget
from app_modeler.widgets.SettingsWidget import SettingsWidget

class BottomLeftWidget(SettingsWidget):
    def __init__(self, state: ModelerState):
        super().__init__()
        self.state = state
        self._setup_ui()
        self._connect_signals()
        self.init_settings(state.settings)

    def _connect_signals(self):
        self.state.signals.screenshot.connect(self.image.update_image)
        self.state.signals.connected.connect(self.on_connected)
        self.state.signals.executed.connect(self.on_executed)
        self.state.signals.disconnected.connect(lambda :self.analyse_button.setEnabled(False))
        self.auto_analyse_checkbox.stateChanged.connect(self.analyse_button.setDisabled)

    def _setup_ui(self):
        layout = QVBoxLayout()
        self.image = ImageWidget(self)
        layout.addWidget(self.image)
        self.setLayout(layout)

        operate_box = QGroupBox()
        operate_layout = QHBoxLayout()

        self.auto_analyse_checkbox = QCheckBox("Auto analyse")
        self.auto_analyse_checkbox.setObjectName("auto_analyse_checkbox")
        operate_layout.addWidget(self.auto_analyse_checkbox)

        self.analyse_button = QPushButton("Analyse")
        self.analyse_button.setEnabled(False)
        self.analyse_button.clicked.connect(self.state.signals.analyse.emit)
        operate_layout.addWidget(self.analyse_button)


        operate_box.setLayout(operate_layout)
        layout.addWidget(operate_box)

    def on_connected(self):
        if self.auto_analyse_checkbox.isChecked():
            # wait a bit to ensure the view is updated
            sleep(1)
            self.state.signals.analyse.emit()
        else:
            self.analyse_button.setEnabled(True)

    def on_executed(self, _):
        if self.auto_analyse_checkbox.isChecked():
            self.state.signals.analyse.emit()
