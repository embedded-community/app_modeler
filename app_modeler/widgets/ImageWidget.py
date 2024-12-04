import logging

from PySide6.QtGui import QPixmap, QPainter, QColor, QPen
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
        self._draw_template_graph()

    def _draw_template_graph(self):
        """Draws a template graph with a large cross mark and borders."""
        # Create a placeholder pixmap to fill the widget
        pixmap = QPixmap(self.size())
        pixmap.fill(Qt.white)

        painter = QPainter(pixmap)
        pen = QPen(QColor("red"), 5)
        painter.setPen(pen)

        # Draw the cross
        width, height = pixmap.width(), pixmap.height()
        painter.drawLine(0, 0, width, height)  # Top-left to bottom-right
        painter.drawLine(0, height, width, 0)  # Bottom-left to top-right

        # Draw the border
        pen.setColor(Qt.black)
        painter.setPen(pen)
        painter.drawRect(0, 0, width - 1, height - 1)  # Add a border

        painter.end()
        self.original_pixmap = pixmap
        self._scale_and_set_pixmap()

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


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication, QVBoxLayout, QWidget

    app = QApplication([])

    widget = QWidget()
    widget.setContentsMargins(0, 0, 0, 0)
    layout = QVBoxLayout(widget)
    image_widget = ImageWidget(widget)
    layout.addWidget(image_widget)
    widget.show()
    app.exec()
