from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QSplitter, QInputDialog

from app_modeler.dialogs.ExceptionDialog import ExceptionDialog
from app_modeler.dialogs.SettingsDIalog import SettingsDialog, AppSettingsWidget
from app_modeler.models.AppSettings import AppSettings
from app_modeler.models.ModelerState import ModelerState
from app_modeler.widgets.MainMiddleWidget import BottomMiddleWidget
from app_modeler.widgets.MainStatusBar import MainStatusBar
from app_modeler.widgets.MainLeftWidget import BottomLeftWidget
from app_modeler.widgets.MainRightWidget import BottomRightWidget
from app_modeler import __version__

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"App modeler v{__version__}")

        self._app_settings = AppSettings()
        self.state = ModelerState(self._app_settings)
        self.state.error_signal.connect(self.show_error)
        self._setup_ui()
        self.setMinimumSize(1000, 700)

        # just for restore values
        AppSettingsWidget(self.state.settings, self._app_settings)

        menu = self.menuBar()
        file_menu = menu.addMenu("File")
        settings_action = file_menu.addAction("Settings...")
        settings_action.triggered.connect(self.on_settings)
        exit_action = file_menu.addAction("Exit")
        exit_action.triggered.connect(self.close)

    def _setup_ui(self):
        central_widget = QWidget()
        main_layout = QVBoxLayout()

        # Bottom Section

        h_splitter = QSplitter(Qt.Horizontal)

        # Bottom Left Widget
        bottom_left_widget = BottomLeftWidget(self.state)
        h_splitter.addWidget(bottom_left_widget)
        # Bottom Middle Widget
        bottom_middle_widget = BottomMiddleWidget(self.state)
        h_splitter.addWidget(bottom_middle_widget)
        # Bottom Right Widget
        bottom_right_widget = BottomRightWidget(self.state)
        h_splitter.addWidget(bottom_right_widget)

        # Add Bottom Layout to Main Layout
        main_layout.addWidget(h_splitter)

        main_layout.setStretch(1, 4)

        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # add statusbar
        self.statusbar = MainStatusBar(self.state)
        self.setStatusBar(self.statusbar)

    def show_error(self, error: Exception):
        # Show error dialog
        ExceptionDialog(error, self).exec()

    def on_settings(self):
        dialog = SettingsDialog(self.state.settings, self._app_settings)
        dialog.exec()

    @Slot(str, result=str)
    def get_text_from_user(self, arg: str) -> str:
        value, ok = QInputDialog.getText(self, "Input", f"Enter input for {arg}:")
        return value if ok else ""
