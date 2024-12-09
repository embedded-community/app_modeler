import logging

from PySide6.QtWidgets import QApplication

from app_modeler.MainWindow import MainWindow

class MainApp(QApplication):
    def __init__(self, *args):
        super().__init__(*args)
        MainApp.configure_logging()
        self.widget = MainWindow()
        self.widget.show()

    @staticmethod
    def configure_logging():
        logging.basicConfig(level=logging.DEBUG)
        # disable: httpcore, openai._base_client
        logging.getLogger('httpx').setLevel(logging.WARNING)
        logging.getLogger('urllib3').setLevel(logging.WARNING)
        logging.getLogger('httpcore').setLevel(logging.WARNING)
        logging.getLogger('openai._base_client').setLevel(logging.WARNING)
        logging.getLogger('selenium.webdriver.remote.remote_connection').setLevel(logging.WARNING)
        logging.getLogger('app_modeler.widgets.SettingsWidget').setLevel(logging.WARNING)

