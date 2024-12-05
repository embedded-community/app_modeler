from typing import Optional

from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QComboBox, QVBoxLayout, QLabel, QLineEdit, QGroupBox
from appium.options.mac import Mac2Options
from appium.options.android import UiAutomator2Options, EspressoOptions
from appium.options.ios import XCUITestOptions, SafariOptions
from appium.options.windows import WindowsOptions

from app_modeler.widgets.FormGenerator import FormGenerator
from app_modeler.widgets.SettingsWidget import SettingsWidget
from app_modeler.widgets.utils.QUrlValidator import QUrlValidator


class AppiumOptionsWidget(SettingsWidget):

    def __init__(self, settings: QSettings):
        super().__init__()
        self._options = None
        self.settings = settings
        self.form_generator: Optional[FormGenerator] = None
        self._appium_options = {
            "Mac2Options": Mac2Options,
            "AndroidOptions": UiAutomator2Options,
            "EspressoOptions": EspressoOptions,
            "IOSOptions": XCUITestOptions,
            "SafariOptions": SafariOptions,
            "WindowsOptions": WindowsOptions
        }
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        self.appium_group_box = QGroupBox("Appium Selection")

        self.appium_group_box_layout = QVBoxLayout()
        self.appium_group_box.setLayout(self.appium_group_box_layout)

        self.appium_server_title = QLabel("Appium Server")
        self.appium_group_box_layout.addWidget(self.appium_server_title)
        self.appium_server_line_edit = QLineEdit()
        self.appium_server_line_edit.setObjectName('appium_server')
        self.appium_server_line_edit.setText('http://localhost:4723')
        self.appium_server_line_edit.setValidator(QUrlValidator())
        self.appium_group_box_layout.addWidget(self.appium_server_line_edit)

        self.driver_combo = QComboBox()
        self.driver_combo.setObjectName('appium_driver_selector')
        self.driver_combo.addItems(self._appium_options.keys())
        self.driver_combo.currentTextChanged.connect(self.on_option_changed)
        self.appium_group_box_layout.addWidget(self.driver_combo)
        layout.addWidget(self.appium_group_box)

        self.appium_options_box = QGroupBox("Appium Options")
        self.appium_options_layout = QVBoxLayout()
        self.appium_options_box.setLayout(self.appium_options_layout)
        layout.addWidget(self.appium_options_box)

        self.setLayout(layout)

        self.on_option_changed(self.driver_combo.currentText())

    @property
    def selected_driver(self):
        return self.driver_combo.currentText()

    @property
    def appium_server(self):
        return self.appium_server_line_edit.text()

    def to_dict(self):
        return {
            'appium_server': self.appium_server,
            'driver': self.selected_driver,
            'capabilities': self.options.to_capabilities()
        }

    def from_dict(self, data):
        self.appium_server_line_edit.setText(data['appium_server'])
        self.driver_combo.setCurrentText(data['driver'])
        self.on_option_changed(data['driver'])
        self.options.load_capabilities(data['capabilities'])

    def on_option_changed(self, text):
        if self.form_generator:
            self.appium_options_layout.removeWidget(self.form_generator)
            self.form_generator.deleteLater()
        self._options = self._appium_options[text]()
        if text == 'Mac2Options':
            self._options.platform_name = 'mac'
            self._options.automation_name = 'mac2'
        elif text == 'AndroidOptions':
            self._options.platform_name = 'android'
            self._options.automation_name = 'uiautomator2'
        self.form_generator = FormGenerator(self._options, self)
        self.appium_options_layout.addWidget(self.form_generator)
        self.init_settings(self.settings)

    @property
    def options(self):
        return self._options



if __name__ == "__main__":
    # main.py
    import sys
    from PySide6.QtWidgets import QApplication, QMainWindow


    class MainWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Form Generator Example")
            self.widget = AppiumOptionsWidget(QSettings())
            self.setCentralWidget(self.widget)

        def print_form_values(self):
            values = self.widget.options
            print("Form Values:", values)



    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
