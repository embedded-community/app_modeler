from PySide6.QtWidgets import QStatusBar, QMenu, QLabel, QProgressBar, QToolButton, QStyle, QDialog, QFrame
from PySide6.QtGui import QIcon, QAction, Qt, QPixmap, QPainter, QColor
from selenium.webdriver.common.options import BaseOptions

from app_modeler.dialogs.AppiumConfigDialog import AppiumConfigDialog
from app_modeler.models.ModelerState import ModelerState
from app_modeler.models.StartOptions import StartOptions
from app_modeler.widgets.InfiniteProgressBar import InfiniteProgressBar


class MainStatusBar(QStatusBar):
    def __init__(self, state: ModelerState):
        super().__init__()
        self.appium_options: BaseOptions = AppiumConfigDialog(state.settings).options
        self.state = state
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        # Spend Tokens with Value
        self.token_label = QLabel("Used tokens: 0")
        self.token_label.setToolTip("Used OpenAI tokens that are deducted from your account.")
        self.addWidget(self.token_label)

        # add separator
        def create_separator():
            separator = QFrame()
            separator.setFrameShape(QFrame.Shape.VLine)
            return separator


        self.addWidget(create_separator())

        self.status_label = QLabel("Status: Idle")
        self.status_label.setMaximumWidth(200)
        self.addWidget(self.status_label)

        # Processing with Progress Bar (stretches to max)
        self.progress_bar = InfiniteProgressBar(self.state.signals.processing, self)
        self.addWidget(self.progress_bar, 1)  # Stretch factor = 1

        self.addWidget(create_separator())
        # Appium Config Button (no submenu)
        self.appium_button = QToolButton(self)
        self.appium_button.setIcon(self.style().standardIcon(QStyle.SP_FileDialogDetailedView))
        self.appium_button.setText("Appium")  # Replace with the path to your Appium icon
        self.appium_button.setToolTip("Appium Configuration")
        self.addWidget(self.appium_button)

        # Connection Status with Icon and Menu
        self.connection_button = QToolButton(self)
        self.connection_button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.connection_menu = QMenu("Connection Status", self)
        self.connect_action = QAction("Connect", self)
        self.connection_menu.addAction(self.connect_action)
        self.disconnect_action = QAction("Disconnect", self)
        self.connection_menu.addAction(self.disconnect_action)
        self.connection_button.setMenu(self.connection_menu)
        self.connection_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.addWidget(self.connection_button)

        self.update_connection_status(False)

    def _connect_signals(self):
        self.state.signals.connected.connect(self.on_connected)
        self.state.signals.disconnected.connect(self.on_disconnected)
        self.state.signals.tokens_spend.connect(self.set_token_value)
        self.state.signals.status_message.connect(self.on_status_message)

        self.connect_action.triggered.connect(self.on_connect_clicked)
        self.disconnect_action.triggered.connect(self.state.signals.disconnect.emit)
        self.appium_button.clicked.connect(self.on_appium_clicked)

    def on_connect_clicked(self):
        options = StartOptions(app_settings=self.state.app_settings,
                               appium_options=self.appium_options)
        self.state.signals.connect.emit(options)

    def on_appium_clicked(self):
        dialog = AppiumConfigDialog(self.state.settings)
        retval = dialog.exec()
        if retval == QDialog.DialogCode.Accepted:
            self.appium_options = dialog.options

    def on_connected(self):
        self.update_connection_status(True)
        self.connect_action.setEnabled(False)
        self.disconnect_action.setEnabled(True)

    def on_disconnected(self):
        self.update_connection_status(False)
        self.connect_action.setEnabled(True)
        self.disconnect_action.setEnabled(False)

    def on_status_message(self, message: str):
        self.status_label.setText(message)


    @staticmethod
    def create_status_icon(color: str) -> QIcon:
        """Create a circular icon with the given color."""
        pixmap = QPixmap(16, 16)
        pixmap.fill(Qt.transparent)  # Transparent background

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QColor(color))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(0, 0, 16, 16)
        painter.end()

        return QIcon(pixmap)

    def update_connection_status(self, state: bool):
        """Update the connection button's icon and text."""
        if state:
            self.connection_button.setIcon(self.create_status_icon("green"))
            self.connection_button.setText("Connected")
        else:
            self.connection_button.setIcon(self.create_status_icon("red"))
            self.connection_button.setText("Disconnected")

    def set_token_value(self, value):
        """Set the value of the tokens display."""
        self.token_label.setText(f"Tokens: {value}")


if __name__ == '__main__':
    from PySide6.QtWidgets import QApplication
    app = QApplication([])
    status_bar = MainStatusBar()
    status_bar.show()
    app.exec()
