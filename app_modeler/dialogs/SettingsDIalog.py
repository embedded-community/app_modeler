from PySide6.QtWidgets import QDialog, QVBoxLayout, QPushButton
from PySide6.QtCore import QSettings

from app_modeler.models.AppSettings import AppSettings
from app_modeler.widgets.FormGenerator import FormGenerator
from app_modeler.widgets.SettingsWidget import SettingsWidget


class AppSettingsWidget(SettingsWidget):
    def __init__(self, settings: QSettings, app_settings: AppSettings):
        super().__init__()
        layout = QVBoxLayout()
        self._app_settings = app_settings
        form = FormGenerator(self._app_settings, self)
        layout.addWidget(form)
        self.setLayout(layout)
        self.init_settings(settings)

class SettingsDialog(QDialog):

    def __init__(self, settings: QSettings, app_settings: AppSettings):
        super().__init__()
        self.setMinimumSize(600, 400)
        self.setWindowTitle("App Config")
        self.settings = settings
        self.app_settings = app_settings
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        self.settings_widget = AppSettingsWidget(self.settings, self.app_settings)
        layout.addWidget(self.settings_widget)
        # accept button
        self.accept_button = QPushButton("Close")
        layout.addWidget(self.accept_button)
        self.accept_button.clicked.connect(self.accept)
        self.setLayout(layout)

if __name__ == '__main__':
    from PySide6.QtWidgets import QApplication

    app = QApplication([])

    dialog = SettingsDialog(QSettings(), AppSettings())
    dialog.exec()
    print(dialog.settings)
    app.exec()
