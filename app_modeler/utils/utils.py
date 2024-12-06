import inspect
import os
import types
from pathlib import Path
from importlib import import_module
import logging
import ast
from typing import Type
import sys

from PySide6.QtGui import QIcon, QPixmap, Qt

from app_modeler.appium_helpers.AppiumInterface import AppiumInterface

logger = logging.getLogger(__name__)


def load_module_file(module_file: Path, *args) -> AppiumInterface:
    """Load a view module from a file and instantiate its main class.

    Args:
        module_file (Path): The path to the module file.
        *args: Arguments to pass to the class constructor.

    Returns:
        AppiumInterface: An instance of the main class from the module.

    Raises:
        ImportError: If the module cannot be imported.
        AttributeError: If the expected class is not found in the module.
        TypeError: If the class is not a subclass of AppiumInterface.
    """
    module_name = module_file.stem
    logger.debug(f'Loading module: {module_name}')

    try:
        module = import_module(f"views.{module_name}")
    except ImportError as e:
        logger.error(f"Failed to import module 'views.{module_name}': {e}")
        raise

    try:
        the_class: Type[AppiumInterface] = getattr(module, module_name)
    except AttributeError as e:
        logger.error(f"Class '{module_name}' not found in module 'views.{module_name}': {e}")
        raise

    if not issubclass(the_class, AppiumInterface):
        logger.error(f"Class '{module_name}' is not a subclass of AppiumInterface")
        raise TypeError(f"Class '{module_name}' must inherit from AppiumInterface")

    the_instance = the_class(*args)
    return the_instance

def load_module_from_code(module_code: str, class_name: str, *args, **kwargs) -> AppiumInterface:
    """Load a module from a code string and instantiate a class from it.

    Args:
        module_code (str): The code of the module as a string.
        class_name (str): The name of the class to instantiate from the module.
        *args: Arguments to pass to the class constructor.
        **kwargs: Keyword arguments to pass to the class constructor.

    Returns:
        AppiumInterface: An instance of the specified class.

    Raises:
        SyntaxError: If the module code contains syntax errors.
        AttributeError: If the class is not found in the module.
        TypeError: If the class is not a subclass of AppiumInterface.
        Exception: If an error occurs during module execution.
    """
    # Create a unique module name
    module_name = 'dynamic_module'

    # Create a new module object
    module = types.ModuleType(module_name)
    module.__file__ = '<string>'

    # Execute the module code in the module's namespace
    try:
        exec(module_code, module.__dict__)
    except Exception as e:
        logger.error(f"Error executing module code: {e}")
        raise

    # Add the module to sys.modules
    sys.modules[module_name] = module

    # Get the class from the module
    try:
        the_class: Type[AppiumInterface] = getattr(module, class_name)
    except AttributeError as e:
        logger.error(f"Class '{class_name}' not found in module code: {e}")
        raise

    # Check if the class is a subclass of AppiumInterface
    if not issubclass(the_class, AppiumInterface):
        logger.error(f"Class '{class_name}' is not a subclass of AppiumInterface")
        raise TypeError(f"Class '{class_name}' must inherit from AppiumInterface")

    # Instantiate the class
    instance = the_class(*args, **kwargs)
    return instance

def generate_class_json_from_file(filename: Path):
    """
    Generate a JSON object representing the API of a class from a Python file.
    Assumes the class name matches the filename (without the extension).

    Args:
        filename (Path): Path to the Python file.

    Returns:
        dict: JSON-like dictionary representing the class and its methods.
    """
    # Extract the class name from the filename (removing the extension)
    class_name = filename.stem

    # Read the source code from the file
    with filename.open('r') as file:
        source_code = file.read()
    return generate_class_json_from_code(source_code, class_name)

def generate_class_json_from_code(source_code: str, class_name: str) -> dict:
    """ Generate a JSON-like dictionary representing the API of a class from Python source code.

    Args:
        source_code (str): The source code of the class.
        class_name (str): The name of the class to analyze.

    Returns:
        dict: A JSON-like dictionary representing the class and its methods.

    Raises:
        ValueError: If the class is not found in the source code.
    """

    # Parse the source code into an AST
    tree = ast.parse(source_code)

    # Find the class node in the AST
    class_node = None
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            class_node = node
            break

    if not class_node:
        raise ValueError(f"Class '{class_name}' not given.")

    # Extract methods from the class
    methods = []
    for item in class_node.body:
        if isinstance(item, ast.FunctionDef):  # Look for method definitions
            method_name = item.name

            # Get parameters
            params = []
            for arg in item.args.args:
                if arg.arg != "self":  # Skip 'self'
                    params.append(arg.arg)

            # Add method info
            methods.append({
                "name": method_name,
                # "description": ast.get_docstring(item) or "No description provided.",
                "parameters": params,
                "returns": None  # AST doesn't provide type hints easily
            })

    # Build the class JSON representation
    class_api = {
        "class": class_name,
        "methods": methods
    }

    return class_api

def get_instance_methods(obj: object) -> [str]:
    cls = obj.__class__
    method_names = [name for name, func, arg in inspect.getmembers(cls, inspect.isfunction) if
            func.__qualname__.startwith(cls.__name__ + '.')]
    # filter out all _* methods
    method_names = [name for name in method_names]
    return method_names

if __name__ == "__main__":
    module_code = """
from app_modeler.appium_helpers.AppiumInterface import AppiumInterface

class MyView(AppiumInterface):
    def __init__(self, driver):
        super().__init__(driver)
        # Additional initialization code

    def click_button(self):
        # Implementation of a method
        pass
"""

    # Assuming 'driver' is defined elsewhere
    try:
        driver = object()
        instance = load_module_from_code(module_code, 'MyView', driver)
        print(instance)
    except Exception:
        logger.exception("An error occurred while loading the module.")
        # Handle exception as needed

def get_icon(name: str) -> QIcon:
    non_binary_root_path = Path(__file__).parent.parent.parent
    base_path = Path(getattr(sys, '_MEIPASS', non_binary_root_path))
    icon_path = base_path / "resources" /  name
    return QIcon(QPixmap(str(icon_path)))
