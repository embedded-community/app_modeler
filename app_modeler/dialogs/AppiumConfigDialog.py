from PySide6.QtWidgets import QDialog, QVBoxLayout, QPushButton

from app_modeler.widgets.AppiumOptionsWidget import AppiumOptionsWidget

class AppiumConfigDialog(QDialog):
    def __init__(self, settings):
        super().__init__()

        self.setWindowTitle("Appium Config")
        layout = QVBoxLayout()
        self.appium_options_widget = AppiumOptionsWidget(settings)
        layout.addWidget(self.appium_options_widget)
        self.setLayout(layout)

        # accept button
        self.accept_button = QPushButton("Close")
        layout.addWidget(self.accept_button)
        self.accept_button.clicked.connect(self.accept)

    @property
    def options(self):
        return self.appium_options_widget.options
