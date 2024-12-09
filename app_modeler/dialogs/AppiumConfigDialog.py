import json
import logging
from PySide6.QtWidgets import QDialog, QVBoxLayout, QPushButton, QGroupBox, QHBoxLayout, QFileDialog

from app_modeler.widgets.AppiumOptionsWidget import AppiumOptionsWidget

logger = logging.getLogger(__name__)


class AppiumConfigDialog(QDialog):
    def __init__(self, settings):
        super().__init__()

        self.setWindowTitle("Appium Config")
        self.appium_options_widget = AppiumOptionsWidget(settings)
        self.export_button = QPushButton("Export")
        self.import_button = QPushButton("Import")

        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(self.appium_options_widget)

        import_group = QGroupBox("Import/Export")
        layout.addWidget(import_group)
        import_layout = QHBoxLayout()
        import_group.setLayout(import_layout)
        import_layout.addWidget(self.export_button)
        import_layout.addWidget(self.import_button)

        # accept button
        self.accept_button = QPushButton("Close")
        layout.addWidget(self.accept_button)

        self.setLayout(layout)

    def _connect_signals(self):
        self.accept_button.clicked.connect(self.accept)
        self.export_button.clicked.connect(self.on_export)
        self.import_button.clicked.connect(self.on_import)

    @property
    def options(self):
        return self.appium_options_widget.options

    def on_export(self):
        data_to_save = self.appium_options_widget.to_dict()
        # open file dialog for save json file
        file_path, _ = QFileDialog.getSaveFileName(self, "Export JSON File", "", "JSON Files (*.json)")
        if not file_path:
            return

        with open(file_path, 'w') as file:
            json.dump(data_to_save, file, indent=4)

    def on_import(self):
        # open file dialog for open json file
        file_path, _ = QFileDialog.getOpenFileName(self, "Import JSON File", "", "JSON Files (*.json)")
        if not file_path:
            return
        with open(file_path, 'r') as file:
            data = json.load(file)
        try:
            self.appium_options_widget.from_dict(data)
        except Exception as error:
            logger.warning(f"Error: {error}")

if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import QSettings

    app = QApplication([])

    dialog = AppiumConfigDialog(QSettings())
    dialog.show()

    sys.exit(app.exec())
