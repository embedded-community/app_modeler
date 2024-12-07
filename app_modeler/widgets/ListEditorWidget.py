from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QListWidget,
    QVBoxLayout,
    QWidget,
    QPushButton,
    QHBoxLayout,
    QMessageBox,
    QAbstractItemView, QListWidgetItem,
)


class ListEditorWidget(QWidget):
    """Widget to edit, add, and remove strings in a list."""
    def __init__(self, parent=None):
        super().__init__(parent)

        # List widget
        self.list_widget = QListWidget(self)
        self.list_widget.setSelectionMode(QListWidget.SingleSelection)
        self.list_widget.setEditTriggers(QAbstractItemView.DoubleClicked | QAbstractItemView.EditKeyPressed)

        # Buttons for list operations
        self.add_button = QPushButton("Add")
        self.remove_button = QPushButton("Remove")

        # Layout for buttons
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.remove_button)

        # Main layout
        layout = QVBoxLayout(self)
        layout.addWidget(self.list_widget)
        layout.addLayout(button_layout)

        # Connect button signals
        self.add_button.clicked.connect(self.new_item)
        self.remove_button.clicked.connect(self.remove_item)

    def new_item(self):
        """Add a new string to the list."""
        new_item = self.append("New Item")
        self.list_widget.editItem(new_item)  # Start inline editing immediately

    def remove_item(self):
        """Remove the selected string."""
        current_item = self.list_widget.currentItem()
        if current_item:
            row = self.list_widget.row(current_item)
            self.list_widget.takeItem(row)
        else:
            QMessageBox.warning(self, "No Selection", "Please select an item to remove.")

    def add_items(self, items):
        """Add a list of items to the list."""
        for string in items:
            self.append(string)

    def append(self, value: str):
        new_item = QListWidgetItem(value)
        new_item.setFlags(new_item.flags() | Qt.ItemIsEditable)
        self.list_widget.addItem(new_item)
        return new_item

    def edit_item(self, index):
        """Edit the item corresponding to the double-clicked index."""
        item = self.list_widget.itemFromIndex(index)
        if item:
            self.list_widget.editItem(item)

    def get_items(self):
        """Get all items in the list."""
        return [self.list_widget.item(i).text() for i in range(self.list_widget.count())]

    def set_items(self, items):
        """Set the list of items."""
        self.list_widget.clear()
        self.add_items(items)


if __name__ == "__main__":
    class MainWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("List Editor Example")
            self.list_editor = ListEditorWidget(self)
            self.list_editor.add_items(["Item 1", "Item 2", "Item 3"])
            self.setCentralWidget(self.list_editor)

    app = QApplication([])

    window = MainWindow()
    window.show()

    app.exec()
