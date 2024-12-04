from PySide6.QtWidgets import (
    QWidget, QListWidget, QListWidgetItem, QPushButton, QHBoxLayout,
    QLabel, QVBoxLayout, QStyle, QApplication
)
from PySide6.QtCore import Signal, QSize
from typing import List, Callable


class CustomListWidgetItem(QWidget):
    """Custom widget item with a label and an execute button."""

    def __init__(self, text: str, button_enabled: bool = True):
        super().__init__()
        self.text: str = text
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        label = QLabel(text)
        layout.addWidget(label)

        self.button = QPushButton()
        icon = QApplication.style().standardIcon(QStyle.SP_ArrowRight)
        self.button.setIcon(icon)
        self.button.setEnabled(button_enabled)

        # Adjust the button to be minimal in size (icon only)
        self.button.setFixedSize(self.button.sizeHint())
        self.button.setMaximumSize(QSize(24, 24))  # Adjust size as needed
        self.button.setFlat(True)
        layout.addWidget(self.button)


class CustomListWidget(QWidget):
    """List widget that allows updating items and emits an execute signal."""

    execute_signal = Signal(str)

    def __init__(self, items: List[str], buttons_enabled: bool = True):
        super().__init__()
        self.list_widget = QListWidget()
        self.buttons_enabled = buttons_enabled
        self.update_items(items)

        layout = QVBoxLayout(self)
        layout.addWidget(self.list_widget)

    def clear(self):
        """Clear the list."""
        self.list_widget.clear()

    def update_items(self, new_items: List[str]):
        """Update the list with new items."""
        self.list_widget.clear()
        for item_text in new_items:
            item_widget = CustomListWidgetItem(item_text, button_enabled=self.buttons_enabled)
            list_item = QListWidgetItem()
            list_item.setSizeHint(item_widget.sizeHint())
            self.list_widget.addItem(list_item)
            self.list_widget.setItemWidget(list_item, item_widget)
            if self.buttons_enabled:
                item_widget.button.clicked.connect(self._create_execute_slot(item_text))

    def _create_execute_slot(self, text: str) -> Callable[[], None]:
        """Create a slot that emits the execute signal with the given text."""
        return lambda: self.execute_signal.emit(text)

    def get_selected_text(self) -> str:
        """Get the text of the selected item."""
        selected_items = self.list_widget.selectedItems()
        if selected_items:
            item_widget = self.list_widget.itemWidget(selected_items[0])
            return item_widget.text
        return ''

    def execute(self):
        """Emit the execute signal for the selected item."""
        text = self.get_selected_text()
        if text:
            self.execute_signal.emit(text)


# Example usage
if __name__ == '__main__':
    import sys

    class MainWindow(QWidget):
        def __init__(self):
            super().__init__()
            self.list_widget = CustomListWidget(['Item 1', 'Item 2', 'Item 3'], buttons_enabled=True)
            self.list_widget.execute_signal.connect(self.handle_execute)
            layout = QVBoxLayout(self)
            layout.addWidget(self.list_widget)

        def handle_execute(self, text: str):
            print(f'Execute action for: {text}')

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
