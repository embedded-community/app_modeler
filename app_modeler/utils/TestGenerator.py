from pathlib import Path
import logging

from app_modeler.models.FunctionCall import FunctionCall
from app_modeler.models.StartOptions import StartOptions
from app_modeler.models.TestSession import TestSession, ClassData


logger = logging.getLogger(__name__)


class TestGenerator:
    def __init__(self, start_options: StartOptions, session: TestSession):
        self._start_options = start_options
        self._session = session

    def generate(self, output_path: str):
        generated_files = []
        # copy appium interface file
        appium_iface_file = Path(__file__).parent.parent / "appium_helpers" / "AppiumInterface.py"
        output = Path(output_path) / appium_iface_file.name
        iface_file_content = appium_iface_file.read_text().replace(
            "from app_modeler.appium_helpers.AppiumInterface import AppiumInterface",
            "from .AppiumInterface import AppiumInterface")
        output.write_text(iface_file_content)
        generated_files.append(str(output))

        # create __init__.py
        init_file = Path(output_path) / "__init__.py"
        init_file.touch()

        class_list = self._session.classes
        history_list = self._session.call_history
        for call in history_list:
            class_name = call.view
            the_class: ClassData = next((c for c in class_list if c.name == class_name), None)
            if the_class is None:
                logger.warning(f"Class {class_name} not found")
                continue

            class_filename = Path(output_path) / f'{class_name}.py'
            with class_filename.open('w') as file:
                file.write(the_class.class_str)
            generated_files.append(str(class_filename))

            screenshot_filename = Path(output_path) / f'{class_name}.png'
            with screenshot_filename.open('wb') as file:
                file.write(the_class.screenshot)
            generated_files.append(str(screenshot_filename))

        pytest_script = self.generate_pytest_case(history_list)
        pytest_filename = Path(output_path) / "test_sample.py"
        pytest_filename.write_text(pytest_script)
        generated_files.append(str(pytest_filename))
        return generated_files

    def generate_pytest_case(self, calls: list[FunctionCall]):

        view_names = set()
        for call in calls:
            view_names.add(call.view)
        view_imports = "\n".join([f"from .{view} import {view}" for view in view_names])

        calls_code = ""
        for index, call in enumerate(calls):
            calls_code += f"{' '*4}# Step #{index}\n"
            calls_code += f"{' '*4}view = {call.view}(appium_driver)\n"
            calls_code += f"{' '*4}view.{call}\n"
            calls_code += "\n"

        driver_imports = {
            "Mac2Options": "from appium.options.mac import Mac2Options",
            "UiAutomator2Options": "from appium.options.android import UiAutomator2Options",
            "EspressoOptions": "from appium.options.android import EspressoOptions",
            "XCUITestOptions": "from appium.options.ios import XCUITestOptions",
            "SafariOptions": "from appium.options.ios import SafariOptions",
            "WindowsOptions": "from appium.options.windows import WindowsOptions"
        }
        driver_import = driver_imports.get(self._start_options.appium_options.__class__.__name__, "")

        template_file = Path(__file__).parent / "pytest_template.tmpl"
        template = template_file.read_text()
        print(template)
        pytest_test_template = template.format(driver_import=driver_import,
                                               appium_class=self._start_options.appium_options.__class__.__name__,
                                               capabilities=self._start_options.appium_options.to_capabilities(),
                                               appium_url=self._start_options.appium_server_url,
                                               view_imports=view_imports,
                                               calls_code=calls_code)
        return pytest_test_template

