import json

from PySide6.QtWidgets import QDialog, QVBoxLayout, QPushButton, QGroupBox, QHBoxLayout, QFileDialog

from app_modeler.widgets.AppiumOptionsWidget import AppiumOptionsWidget

class AppiumConfigDialog(QDialog):
    def __init__(self, settings):
        super().__init__()

        self.setWindowTitle("Appium Config")
        layout = QVBoxLayout()
        self.appium_options_widget = AppiumOptionsWidget(settings)
        layout.addWidget(self.appium_options_widget)
        self.setLayout(layout)

        mport_groupbox = QGroupBox("Import/Export")
        layout.addWidget(mport_groupbox)
        mpoert_layout = QHBoxLayout()
        mport_groupbox.setLayout(mpoert_layout)
        self.export_button = QPushButton("Export")
        self.import_button = QPushButton("Import")
        mpoert_layout.addWidget(self.export_button)
        mpoert_layout.addWidget(self.import_button)

        # accept button
        self.accept_button = QPushButton("Close")
        layout.addWidget(self.accept_button)
        self._connect_signals()

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
        if file_path:
            with open(file_path, 'w') as file:
                json.dump(data_to_save, file, indent=4)

    def on_import(self):
        # open file dialog for open json file
        file_path, _ = QFileDialog.getOpenFileName(self, "Import JSON File", "", "JSON Files (*.json)")
        if file_path:
            with open(file_path, 'r') as file:
                data = json.load(file)
                self.appium_options_widget.from_dict(data)

if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import QSettings

    app = QApplication([])

    dialog = AppiumConfigDialog(QSettings())
    dialog.show()

    sys.exit(app.exec_())
