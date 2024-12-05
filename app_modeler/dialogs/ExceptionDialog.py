import traceback

from PySide6.QtGui import QFontDatabase
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QTextEdit, QPushButton
from PySide6.QtCore import Qt
from selenium.common import WebDriverException


class ExceptionDialog(QDialog):
    def __init__(self, exception: Exception, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Error")
        self.setMinimumSize(400, 300)
        self.setModal(True)

        # Create the layout
        layout = QVBoxLayout(self)

        # Exception type
        exception_type_label = QLabel(f"<b>Type:</b> {type(exception).__name__}")
        layout.addWidget(exception_type_label)

        # Exception message

        message = str(exception)
        if isinstance(exception, WebDriverException):
            message = exception.msg
        exception_message_label = QLabel(f"<b>Message:</b> {message}")
        exception_message_label.setWordWrap(True)
        layout.addWidget(exception_message_label)

        # Exception stack trace
        stack_trace = "".join(traceback.format_exception(type(exception), exception, exception.__traceback__))
        stack_trace_edit = QTextEdit()
        stack_trace_edit.setReadOnly(True)
        stack_trace_edit.setText(stack_trace)
        # mono font for stack trace
        font = QFontDatabase.systemFont(QFontDatabase.FixedFont)
        font.setPointSize(10)
        stack_trace_edit.setFont(font)

        layout.addWidget(stack_trace_edit)

        # Close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button)

        # Center the dialog contents
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)


# Example usage
if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)

    try:
        # Example exception
        raise WebDriverException("This is a test error", stacktrace="This is a test stack trace")
    except Exception as ex:
        dialog = ExceptionDialog(ex)
        dialog.exec()
