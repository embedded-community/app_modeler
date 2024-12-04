import datetime
from typing import get_type_hints, get_origin, get_args, Union, NewType
import logging


from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit, QCheckBox, QGroupBox,
    QFormLayout, QScrollArea, QHBoxLayout, QTextEdit, QComboBox, QSizePolicy
)
from PySide6.QtGui import QIntValidator, QDoubleValidator
from PySide6.QtCore import Qt

MultilineStr = NewType('MultilineStr', str)
SecretStr = NewType('SecretStr', str)


logger = logging.getLogger(__name__)


class FormGenerator(QWidget):
    """
    Generates a form UI based on a given instance's properties.
    """
    def __init__(self, instance, parent=None):
        super().__init__(parent)
        self.instance = instance
        self.widgets = {}  # Store widgets and their types
        self._setup_ui()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)

        # Use a scroll area in case the form is large
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)

        class_properties = self._get_class_properties(type(self.instance))

        for base_cls, properties in class_properties.items():
            group_box = QGroupBox(base_cls.__name__)
            form_layout = QFormLayout()
            form_layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)

            has_fields = False

            for name, (prop, type_hint) in properties.items():

                if name in self.widgets:
                    logger.debug(f"Skipping duplicate property: {name}")
                    continue

                widget_pair = self._create_widget_for_type(type_hint)
                if widget_pair:
                    has_fields = True
                    widget, none_checkbox, actual_type = widget_pair

                    # Initialize widget value from the instance
                    value = getattr(self.instance, name, None)
                    self._set_widget_value(widget, value, actual_type)

                    # Connect signals to update the instance's properties
                    self._connect_widget_signal(widget, name, actual_type)

                    # Get docstring for tooltip
                    docstring = prop.fget.__doc__
                    if docstring:
                        widget.setToolTip(docstring)
                        if none_checkbox:
                            none_checkbox.setToolTip(docstring)
                    widget.setObjectName(name)

                    # Handle the 'Set to None' checkbox if the field is optional
                    if none_checkbox:
                        none_checkbox.setObjectName(f"{name}_none")
                        # Set the checkbox state based on whether the value is None
                        none_checkbox.setChecked(value is None)
                        self._connect_none_checkbox(none_checkbox, widget, name, actual_type)
                        # Create a horizontal layout for the widget and checkbox
                        h_layout = QHBoxLayout()
                        h_layout.addWidget(widget)
                        h_layout.addWidget(none_checkbox)
                        form_layout.addRow(name, h_layout)
                    else:
                        form_layout.addRow(name, widget)

                    self.widgets[name] = (widget, actual_type)  # Store widget and type
            if has_fields:
                group_box.setLayout(form_layout)
                scroll_layout.addWidget(group_box)

        scroll_content.setLayout(scroll_layout)
        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)
        self.setLayout(main_layout)

    def _get_class_properties(self, cls):
        """
        Retrieves properties with getter and setter methods, grouped by declaring class.
        """
        class_properties = {}
        for base in cls.__mro__:
            if base is object:
                continue
            base_properties = {}
            for name, member in vars(base).items():
                if isinstance(member, property) and member.fget and member.fset:
                    # Get type hint from the getter method
                    type_hints = get_type_hints(member.fget)
                    type_hint = type_hints.get('return', None)
                    base_properties[name] = (member, type_hint)
            if base_properties:
                class_properties[base] = base_properties
        return class_properties

    def _create_widget_for_type(self, type_hint):
        """
        Creates a widget based on the provided type hint.
        Returns a tuple of (widget, none_checkbox, actual_type) if the field is optional.
        """
        is_optional = False
        origin = get_origin(type_hint)
        args = get_args(type_hint)

        if origin is Union and type(None) in args:
            is_optional = True
            # Get the actual type (e.g., int from Optional[int])
            non_none_types = [arg for arg in args if arg is not type(None)]
            actual_type = non_none_types[0] if non_none_types else None
        else:
            actual_type = type_hint

        if actual_type is None:
            return None  # Unsupported type

        if actual_type == str:
            widget = QLineEdit()
        elif actual_type == bool:
            widget = QCheckBox()
        elif actual_type in [int, datetime.timedelta]:
            widget = QLineEdit()
            validator = QIntValidator()
            widget.setValidator(validator)
        elif actual_type == float:
            widget = QLineEdit()
            validator = QDoubleValidator()
            validator.setNotation(QDoubleValidator.StandardNotation)
            widget.setValidator(validator)
        elif actual_type == MultilineStr:
            widget = QTextEdit()
            widget.setPlaceholderText("Multiline string")
        elif actual_type == SecretStr:
            widget = QLineEdit()
            widget.setEchoMode(QLineEdit.EchoMode.Password)
        else:
            # Handle other types or return None to skip
            return None

        if is_optional:
            none_checkbox = QCheckBox("Set to None")
            return widget, none_checkbox, actual_type
        else:
            return widget, None, actual_type

    def _set_widget_value(self, widget, value, actual_type):
        """
        Sets the initial value of the widget.
        """
        if value is None:
            # Handled by the 'Set to None' checkbox
            return

        if isinstance(widget, QLineEdit):
            if actual_type in (int, float):
                widget.setText(str(value))
            else:
                widget.setText(value)
        elif isinstance(widget, QTextEdit):
            widget.setPlainText(value)
        elif isinstance(widget, QCheckBox):
            widget.setChecked(bool(value))

    def _connect_widget_signal(self, widget, property_name, actual_type):
        """
        Connects widget signals to update the instance's properties.
        """
        def update_property():
            # Only update if the widget is enabled
            if not widget.isEnabled():
                return
            if isinstance(widget, QLineEdit):
                text = widget.text()
                if actual_type in [int, datetime.timedelta]:
                    try:
                        value = int(text)
                    except ValueError:
                        value = 0
                elif actual_type == float:
                    try:
                        value = float(text)
                    except ValueError:
                        value = 0.0
                else:
                    value = text
            elif isinstance(widget, QTextEdit):
                value = widget.toPlainText()
            elif isinstance(widget, QComboBox):
                value = widget.currentText()
            elif isinstance(widget, QCheckBox):
                value = widget.isChecked()
            else:
                value = None
            try:
                setattr(self.instance, property_name, value)
                # @todo: revert to previous value if error occurs
                # self.instance.setProperty(f'prev_{property_name}', value)
            except ValueError as error:
                logger.warning(f"Error setting property: {error}, reverting to old value")
                # prev_value = self.instance.property(f'prev_{property_name}')
                # revert to previous value to widget
                #widget.

        if isinstance(widget, (QLineEdit, QTextEdit)):
            widget.textChanged.connect(update_property)
        elif isinstance(widget, QComboBox):
            widget.currentTextChanged.connect(update_property)
        elif isinstance(widget, QCheckBox):
            # For the main widget, not the 'Set to None' checkbox
            widget.stateChanged.connect(update_property)

    def _connect_none_checkbox(self, none_checkbox, widget, property_name, actual_type):
        """
        Connects the 'Set to None' checkbox to enable/disable the widget and update the property.
        """
        def on_checkbox_state_changed(state):
            is_none = state == Qt.CheckState.Checked.value
            widget.setEnabled(not is_none)
            if is_none:
                setattr(self.instance, property_name, None)
            else:
                # Reset the property to the widget's current value
                self._update_property_from_widget(widget, property_name, actual_type)

        none_checkbox.stateChanged.connect(on_checkbox_state_changed)
        # Initialize widget state
        widget.setEnabled(not none_checkbox.isChecked())

    def _update_property_from_widget(self, widget, property_name, actual_type):
        """
        Updates the property value from the widget's current value.
        """
        if isinstance(widget, QLineEdit):
            text = widget.text()
            if actual_type in [int, datetime.timedelta]:
                try:
                    value = int(text)
                except ValueError:
                    value = 0
            elif actual_type == float:
                try:
                    value = float(text)
                except ValueError:
                    value = 0.0
            else:
                value = text
        elif isinstance(widget,QTextEdit):
            value = widget.toPlainText()
        elif isinstance(widget, QCheckBox):
            value = widget.isChecked()
        else:
            value = None
        setattr(self.instance, property_name, value)

    def get_values(self):
        """
        Retrieves the current values from the form widgets.
        """
        values = {}
        for name, (widget, actual_type) in self.widgets.items():
            if isinstance(widget, QLineEdit):
                text = widget.text()
                if actual_type in [int, datetime.timedelta]:
                    try:
                        values[name] = int(text)
                    except ValueError:
                        values[name] = 0
                elif actual_type == float:
                    try:
                        values[name] = float(text)
                    except ValueError:
                        values[name] = 0.0
                else:
                    values[name] = text
            elif isinstance(widget, (MultilineStr, SecretStr)):
                values[name] = widget.text()
            elif isinstance(widget, QCheckBox):
                values[name] = widget.isChecked()
        return values

if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication, QMainWindow

    from appium.options.android.uiautomator2.uiautomator2_server_read_timeout_option import \
        Uiautomator2ServerReadTimeoutOption

    conf = Uiautomator2ServerReadTimeoutOption()
    app = QApplication(sys.argv)
    window = QMainWindow()
    window.setWindowTitle("Form Generator Example")
    widget = FormGenerator(conf)
    window.setCentralWidget(widget)
    window.show()

    sys.exit(app.exec())
