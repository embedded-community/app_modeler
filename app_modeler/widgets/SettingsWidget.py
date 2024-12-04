from typing import Optional
import logging

from PySide6.QtWidgets import QWidget, QCheckBox, QLineEdit, QSlider, QComboBox
from PySide6.QtCore import QSettings, Qt

logger = logging.getLogger(__name__)


class SettingsWidget(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings: Optional[QSettings] = None

    def init_settings(self, settings: QSettings):
        """
        Initializes settings by either using a provided QSettings instance or creating a new one.
        Also connects widget signals to save settings on change.

        :param settings: An optional QSettings instance to use for saving and loading settings.
        :param group: The group name to use for saving and loading settings.
        """
        # Use provided QSettings or create a default one
        self.settings = settings
        logger.debug(f'Setting filename: {self.settings.fileName()}')

        # Load saved settings and connect signals
        self.load_settings()
        self.connect_settings_signals()

    def get_setting_name(self, widget: QWidget) -> str:
        """
        Returns the setting name for a widget based on its objectName and parent objectName.
        """
        return f"AppModeler/{self.objectName()}/{widget.objectName()}"

    def connect_settings_signals(self):
        # Loop through all widgets and connect relevant signals
        for widget in self.findChildren(QWidget):
            if not widget.objectName():
                continue
            if isinstance(widget, QCheckBox):
                widget.stateChanged.connect(self.save_settings)
            elif isinstance(widget, QLineEdit):
                widget.textChanged.connect(self.save_settings)
            elif isinstance(widget, QSlider):
                widget.valueChanged.connect(self.save_settings)
            elif isinstance(widget, QComboBox):
                widget.currentIndexChanged.connect(self.save_settings)

    def save_settings(self):
        """
        Saves the state of each widget to QSettings.
        """
        self.settings: QSettings
        for widget in self.findChildren(QWidget):
            if not widget.objectName():
                continue
            key = self.get_setting_name(widget)

            if isinstance(widget, QCheckBox):
                self.settings.setValue(key, widget.isChecked())
                logger.debug(f'Saving setting: {key}={widget.isChecked()}')
            elif isinstance(widget, QLineEdit):
                self.settings.setValue(key, widget.text())
                logger.debug(f'Saving setting: {key}={widget.text()}')
            elif isinstance(widget, QSlider):
                self.settings.setValue(key, widget.value())
                logger.debug(f'Saving setting: {key}={widget.value()}')
            elif isinstance(widget, QComboBox):
                self.settings.setValue(key, widget.currentIndex())
                logger.debug(f'Saving setting: {key}={widget.currentIndex()}')

    def load_settings(self):
        """
        Loads the state of each widget from QSettings.
        """
        self.settings: QSettings
        for widget in self.findChildren(QWidget):
            if not widget.objectName():
                continue
            key = self.get_setting_name(widget)
            if isinstance(widget, QCheckBox):
                widget.setChecked(self.settings.value(key, False, type=bool))
                logger.debug(f'Loading setting: {key}={widget.isChecked()}')
            elif isinstance(widget, QLineEdit):
                widget.setText(self.settings.value(key, "", type=str))
                logger.debug(f'Loading setting: {key}={widget.text()}')
            elif isinstance(widget, QSlider):
                min_value = widget.minimum()
                widget.setValue(self.settings.value(key, min_value, type=int))
                logger.debug(f'Loading setting: {key}={widget.value()}')
            elif isinstance(widget, QComboBox):
                widget.setCurrentIndex(self.settings.value(key, 0, type=int))
                logger.debug(f'Loading setting: {key}={widget.currentIndex()}')
