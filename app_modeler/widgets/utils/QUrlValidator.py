from PySide6.QtCore import QUrl
from PySide6.QtGui import QValidator


class QUrlValidator(QValidator):
    def validate(self, input_str, pos):
        url = QUrl(input_str)
        if url.isValid():
            return (QValidator.State.Acceptable, input_str, pos)
        return (QValidator.State.Invalid, input_str, pos)
