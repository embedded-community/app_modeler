import textwrap
from time import sleep

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QVBoxLayout, QGroupBox, QHBoxLayout, QPushButton, QCheckBox, QLabel

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
        self.image.setVisible(False)
        from PySide6.QtWidgets import QPlainTextEdit
        self.help_label = QLabel(textwrap.dedent(f"""
        Instructions:
        
        0. Verify that the <a href="https://appium.io">appium</a> server is running with selected drivers.
        1. Configure the appium settings using statusbar appium icon.
        2. Connect to the device using the connection status button.
        3. Click on the analyse button to start the analysis.
        4. Click on the import button to import the generated class
        5. Double-click on the one suggested function that you want execute
        
        NOTE: 
          * openAI token and used prompts is configured in the application settings.
          * auto analyse will automatically start the analysis after 
            connecting to the device or after executing a function.
          * auto import will automatically import the generated  
            class after class generation.
          * auto execute will automatically execute the suggested 
            function after importing the generated class.
        
        """).strip().replace("\n", "<br>"))
        self.help_label.setOpenExternalLinks(True)
        self.help_label.setTextFormat(Qt.RichText)
        layout.addWidget(self.help_label, stretch=1)
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
        self.help_label.setVisible(False)
        self.image.setVisible(True)
        if self.auto_analyse_checkbox.isChecked():
            # wait a bit to ensure the view is updated
            sleep(1)
            self.state.signals.analyse.emit()
        else:
            self.analyse_button.setEnabled(True)

    def on_executed(self, _):
        if self.auto_analyse_checkbox.isChecked():
            self.state.signals.analyse.emit()
