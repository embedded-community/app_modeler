import sys

from app_modeler.MainApp import MainApp


def main():
    app = MainApp(sys.argv)
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
