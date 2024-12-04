import logging

from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QSizePolicy

logger = logging.getLogger(__name__)


class ImageWidget(QLabel):
    def __init__(self, parent):
        super().__init__(parent)
        self.setScaledContents(True)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setScaledContents(False)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.original_pixmap = None  # Store the original pixmap

    def update_image(self, image_data: bytes):
        logger.debug("Updating image")
        pixmap = QPixmap()
        pixmap.loadFromData(image_data)
        self.original_pixmap = pixmap
        self._scale_and_set_pixmap()

    def _scale_and_set_pixmap(self):
        if not self.original_pixmap:
            return

        label_size = self.size()
        scaled_pixmap = self.original_pixmap.scaled(
            label_size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.setPixmap(scaled_pixmap)

    def resizeEvent(self, event):
        self._scale_and_set_pixmap()
        super().resizeEvent(event)
