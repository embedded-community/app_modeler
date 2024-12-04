import sys
import logging
from PySide6.QtWidgets import QApplication
from app_modeler.MainWindow import MainWindow

def configure_logging():
    logging.basicConfig(level=logging.DEBUG)
    # disable: httpcore, openai._base_client
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('httpcore').setLevel(logging.WARNING)
    logging.getLogger('openai._base_client').setLevel(logging.WARNING)
    logging.getLogger('selenium.webdriver.remote.remote_connection').setLevel(logging.WARNING)


def main():
    configure_logging()
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
