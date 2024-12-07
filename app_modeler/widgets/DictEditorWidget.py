from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QMessageBox,
)

class DictEditorWidget(QWidget):
    """Widget to edit a dictionary (Dict[str, str]) with inline editing."""
    def __init__(self, parent=None):
        super().__init__(parent)

        # Table for displaying and editing the dictionary
        self.table = QTableWidget(0, 2, self)  # Initially 0 rows, 2 columns
        self.table.setHorizontalHeaderLabels(["Key", "Value"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setEditTriggers(QTableWidget.DoubleClicked | QTableWidget.EditKeyPressed)

        # Buttons for managing dictionary entries
        self.add_button = QPushButton("Add")
        self.remove_button = QPushButton("Remove Selected")
        self.clear_button = QPushButton("Clear All")

        # Layout for buttons
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.remove_button)
        button_layout.addWidget(self.clear_button)

        # Main layout
        layout = QVBoxLayout(self)
        layout.addWidget(self.table)
        layout.addLayout(button_layout)

        # Connect button signals
        self.add_button.clicked.connect(self.add_entry)
        self.remove_button.clicked.connect(self.remove_selected)
        self.clear_button.clicked.connect(self.clear_all)

    def add_entry(self):
        """Add a new key-value pair to the dictionary."""
        row_position = self.table.rowCount()
        self.table.insertRow(row_position)
        self.table.setItem(row_position, 0, QTableWidgetItem("New Key"))
        self.table.setItem(row_position, 1, QTableWidgetItem("New Value"))
        self.table.editItem(self.table.item(row_position, 0))  # Start editing the new key

    def remove_selected(self):
        """Remove the currently selected row."""
        selected_items = self.table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select a row to remove.")
            return
        for item in selected_items:
            self.table.removeRow(item.row())

    def clear_all(self):
        """Clear all rows in the table."""
        self.table.setRowCount(0)

    def get_dict(self):
        """Retrieve the dictionary as Dict[str, str]."""
        result = {}
        for row in range(self.table.rowCount()):
            key_item = self.table.item(row, 0)
            value_item = self.table.item(row, 1)
            key = key_item.text().strip() if key_item else ""
            value = value_item.text().strip() if value_item else ""
            if key:  # Only include non-empty keys
                result[key] = value
        return result

    def set_dict(self, data):
        """Set the table's content from a dictionary."""
        self.table.setRowCount(0)  # Clear existing rows
        for key, value in data.items():
            row_position = self.table.rowCount()
            self.table.insertRow(row_position)
            self.table.setItem(row_position, 0, QTableWidgetItem(key))
            self.table.setItem(row_position, 1, QTableWidgetItem(value))


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    widget = DictEditorWidget()
    widget.set_dict({"Key1": "Value1", "Key2": "Value2"})
    widget.show()
    sys.exit(app.exec())
