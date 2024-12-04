import logging

from PySide6.QtWidgets import QGridLayout, QLineEdit, QPushButton, QDialog, QLabel, QStyle, QFileDialog
from selenium.webdriver.common.options import BaseOptions

from app_modeler.models.ModelerState import ModelerState
from app_modeler.models.StartOptions import StartOptions
from app_modeler.dialogs.AppiumConfigDialog import AppiumConfigDialog
from app_modeler.widgets.ProgressWidget import InfiniteProgressBar
from app_modeler.widgets.SettingsWidget import SettingsWidget

logger = logging.getLogger(__name__)


class TopWidget(SettingsWidget):
    def __init__(self, state: ModelerState):
        super().__init__()
        self.state = state
        self._setup_ui()
        self.appium_options: BaseOptions = AppiumConfigDialog(self.state.settings).options
        self.init_settings(state.settings)

    def _setup_ui(self):
        layout = QGridLayout()

        self.output_path_label = QLabel("Output Path")
        self.output_path_edit = QLineEdit()
        self.output_path_edit.setPlaceholderText("Output path")
        self.output_path_button = QPushButton()
        self.output_path_button.setIcon(self.style().standardPixmap(QStyle.SP_DirOpenIcon))
        self.output_path_button.clicked.connect(self.on_output_path_button_clicked)

        layout.addWidget(self.output_path_label, 0, 0)
        layout.addWidget(self.output_path_edit, 0, 1, 1, 2)
        layout.addWidget(self.output_path_button, 0, 3)

        self.config_button = QPushButton("Appium Config")
        self.config_button.clicked.connect(self.on_config)
        layout.addWidget(self.config_button, 0, 4)

        self.spend_label = QLabel("Spend tokens")
        self.spend_value = QLabel("0")
        self.spend_value.setToolTip("Used OpenAI tokens")

        self.connect_button = QPushButton("Connect")
        self.connect_button.clicked.connect(self.on_connect)

        self.disconnect_button = QPushButton("Disconnect")
        self.disconnect_button.setEnabled(False)
        self.disconnect_button.clicked.connect(self.state.signals.disconnect.emit)

        self.state.signals.processing.connect(self.on_processing)
        self.state.signals.connected.connect(lambda :self.disconnect_button.setEnabled(True))
        self.state.signals.disconnected.connect(lambda :self.disconnect_button.setEnabled(False))
        self.state.signals.disconnected.connect(lambda :self.connect_button.setEnabled(True))
        self.state.signals.disconnected.connect(lambda :self.output_path_edit.setEnabled(True))
        self.state.signals.disconnected.connect(lambda :self.config_button.setEnabled(True))
        self.output_path_edit.textChanged.connect(self.on_output_path_text_changed)

        self.progress_widget = InfiniteProgressBar(self.state.signals.processing, self)

        layout.addWidget(self.spend_label, 1, 0)
        layout.addWidget(self.spend_value, 1, 1)
        layout.addWidget(self.progress_widget, 1, 2)
        layout.addWidget(self.connect_button, 1, 3)
        layout.addWidget(self.disconnect_button, 1, 4)

        self.setLayout(layout)

    def on_processing(self, processing: bool):
        if not processing and self.state.ai_assistant:
            self.spend_value.setText(f'{self.state.ai_assistant.used_tokens}')

    def on_connect(self):
        options = StartOptions(app_settings=self.state.app_settings,
                               appium_options=self.appium_options)
        self.state.signals.connect.emit(options)
        self.connect_button.setDisabled(True)
        self.output_path_edit.setDisabled(True)
        self.config_button.setDisabled(True)

    def on_config(self):
        dialog = AppiumConfigDialog(self.state.settings)
        retval = dialog.exec()
        if retval == QDialog.DialogCode.Accepted:
            self.appium_options = dialog.options

    def on_output_path_button_clicked(self):
        new_dir = QFileDialog.getExistingDirectory(self, "Select Directory")
        self.output_path_edit.setText(new_dir)

    def on_output_path_text_changed(self):
        self.state.app_settings.output_path = self.output_path_edit.text()
