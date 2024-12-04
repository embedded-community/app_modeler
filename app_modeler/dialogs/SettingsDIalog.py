from pathlib import Path
import logging

from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QDialog, QVBoxLayout, QPushButton
from PySide6.QtCore import QSettings, QUrl

from app_modeler.models.AppSettings import AppSettings
from app_modeler.widgets.FormGenerator import FormGenerator
from app_modeler.widgets.SettingsWidget import SettingsWidget

logger = logging.getLogger(__name__)


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
        self.setWindowTitle("App Settings")
        self.settings = settings
        self.app_settings = app_settings
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        self.settings_widget = AppSettingsWidget(self.settings, self.app_settings)
        layout.addWidget(self.settings_widget)

        app_config_folder_button = QPushButton("Open application config folder")
        app_config_folder_button.clicked.connect(self.on_open_config_folder)
        layout.addWidget(app_config_folder_button)
        # accept button
        self.accept_button = QPushButton("Close")
        layout.addWidget(self.accept_button)
        self.accept_button.clicked.connect(self.accept)
        self.setLayout(layout)

    def on_open_config_folder(self):
        absolute_path = Path(self.settings.fileName()).resolve().parent
        # open folder to OS file browser
        # Convert the path to a file URL
        url = QUrl.fromLocalFile(absolute_path)

        # Use QDesktopServices to open the folder
        if not QDesktopServices.openUrl(url):
            logger.warning(f"Failed to open folder: {absolute_path}")

if __name__ == '__main__':
    from PySide6.QtWidgets import QApplication

    app = QApplication([])

    dialog = SettingsDialog(QSettings(), AppSettings())
    dialog.exec()
    print(dialog.settings)
    app.exec()
