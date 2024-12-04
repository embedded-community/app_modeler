import json
import logging
from dataclasses import dataclass
from typing import Optional

from PySide6.QtCore import QObject, Signal, QSettings
from appium import webdriver
from selenium.common import NoSuchDriverException, InvalidSessionIdException

from app_modeler.ai.OpenAiAssistant import OpenAIAssistant
from app_modeler.ai.AppiumClassGenerator import AppiumClassGenerator
from app_modeler.ai.TesterAi import TesterAi
from app_modeler.appium_helpers.AppiumInterface import AppiumInterface
from app_modeler.appium_helpers.drivers.create import create_driver
from app_modeler.appium_helpers.elements.ElementsDiscover import ElementsDiscover, ElementData
from app_modeler.models.AppSettings import AppSettings
from app_modeler.models.FunctionCall import NextFunctionList, FunctionCall
from app_modeler.models.StartOptions import StartOptions
from app_modeler.models.WorkerThread import WorkerThread
from app_modeler.utils.utils import load_module_from_code, generate_class_json_from_code

logger = logging.getLogger(__name__)


class Signals(QObject):
    connect = Signal(StartOptions)
    connected = Signal()
    disconnect = Signal()
    disconnected = Signal()
    analyse = Signal()
    execute = Signal(str)


    processing = Signal(bool)
    screenshot = Signal(bytearray)
    class_propose = Signal(str)
    elements_propose = Signal(str)
    import_module = Signal()
    module_imported = Signal()
    next_func_candidates = Signal()

@dataclass
class CurrentView:
    name: str
    screenshot_as_png: bytes
    elements_data: [ElementData]
    class_str: str
    view: Optional[AppiumInterface] = None
    function_candidates: Optional[NextFunctionList] = None


class ModelerState(QObject):
    error_signal = Signal(Exception)
    def __init__(self, app_settings: AppSettings):
        super().__init__()
        self._app_settings = app_settings
        self.ai_assistant: Optional[OpenAIAssistant] = None
        self.signals = Signals()
        self.signals.connect.connect(self.on_connect)
        self.signals.disconnect.connect(self.on_disconnect)
        self.signals.analyse.connect(self.on_analyse)
        self.signals.import_module.connect(self.on_import_module)
        self.signals.execute.connect(self.on_execute)
        self.worker_thread = None
        self.driver: webdriver = None
        self.settings = QSettings("app_modeler.ini", QSettings.Format.IniFormat)
        self._current_view: Optional[CurrentView] = None
        self._view_index = 0

    @property
    def current_view(self) -> Optional[CurrentView]:
        return self._current_view

    @property
    def app_settings(self) -> AppSettings:
        return self._app_settings

    def wait_for_thread(func):
        """ Decorator to wait for the thread to finish before calling the function """
        def wrapper(self, *args, **kwargs):
            if self.worker_thread is not None and self.worker_thread.isRunning():
                logger.debug('Waiting for thread to finish')
                self.worker_thread.wait()
                logger.debug('Thread finished')
            logger.debug(f'Calling {func.__name__}')
            return func(self, *args, **kwargs)
        return wrapper

    def on_connect(self, start_options: StartOptions):
        self.worker_thread = WorkerThread(self.do_connect, start_options)
        self.worker_thread.busy.connect(self.signals.processing.emit)
        self.worker_thread.result_signal.connect(self.on_connected)
        self.worker_thread.error_signal.connect(self.on_error)
        self.worker_thread.error_signal.connect(lambda _: self.signals.disconnected.emit())
        self.worker_thread.start()

    def do_connect(self, start_options: StartOptions) -> bytes:
        self.driver = create_driver(start_options)
        assert start_options.app_settings.ai_service == 'openai', "Only OpenAI is supported"
        token = start_options.app_settings.token
        base_url = start_options.app_settings.base_url
        model = start_options.app_settings.model
        self.ai_assistant = OpenAIAssistant(api_key=token, base_url=base_url, model=model)
        return self.driver.get_screenshot_as_png()

    def on_connected(self, screenshot: bytes):
        self.signals.screenshot.emit(screenshot)
        self.signals.connected.emit()

    @wait_for_thread
    def on_disconnect(self):
        if self.driver is not None:
            self.driver.quit()
        self.signals.disconnected.emit()

    @wait_for_thread
    def on_analyse(self):
        self.worker_thread = WorkerThread(self.do_analyse)
        self.worker_thread.busy.connect(self.signals.processing.emit)
        self.worker_thread.result_signal.connect(self.on_analyse_ready)
        self.worker_thread.error_signal.connect(self.on_error)
        self.worker_thread.start()

    def on_analyse_ready(self, _):
        logger.debug('Analyse ready')
        self.signals.next_func_candidates.emit()

    def on_error(self, error: Exception):
        if isinstance(error, (NoSuchDriverException, InvalidSessionIdException)):
            logger.error("Error: No driver found")
            self.signals.disconnected.emit()
        self.error_signal.emit(error)

    def do_analyse(self):
        """ Analyse the current view
        1. Capture screenshot
        2. Discover elements
        3. Generate class code
        """
        logger.debug('capture screenshot')
        screenshot = self.driver.get_screenshot_as_png()
        self.signals.screenshot.emit(bytearray(screenshot))

        logger.debug('Discover elements')
        discover = ElementsDiscover(self.driver)
        elements_data = discover.scan_view()
        elements_str = json.dumps([elem.asdict_custom() for elem in elements_data], indent=4)
        self.signals.elements_propose.emit(elements_str)

        logger.debug('Generate class code')

        class_name = f'View{self._view_index}'
        self._view_index += 1
        class_generator = AppiumClassGenerator(self.ai_assistant, prompt_template=self.app_settings.class_generator_prompt)
        class_str = class_generator.generate(class_name=class_name, elements=elements_data)

        self._current_view = CurrentView(name=class_name,
                                         screenshot_as_png=screenshot,
                                         elements_data=elements_data,
                                         class_str=class_str)
        self.signals.class_propose.emit(class_str)

        logger.debug('Ask next functions')
        tester = TesterAi(self.ai_assistant, prompt_template=self.app_settings.tester_prompt)

        class_docstring = generate_class_json_from_code(self._current_view.class_str, self._current_view.name)
        next_functions: [FunctionCall] = tester.ask_next_step(class_docstring, previous_steps=[])
        logger.debug(f"Next functions: {next_functions}")
        self._current_view.function_candidates = next_functions
        logger.debug('Next functions available')

    @wait_for_thread
    def on_import_module(self):
        logger.debug('Importing module')
        self.worker_thread = WorkerThread(self.do_import_module, self._current_view.name)
        self.worker_thread.busy.connect(self.signals.processing.emit)
        self.worker_thread.result_signal.connect(lambda _: self.signals.module_imported.emit())
        self.worker_thread.error_signal.connect(self.on_error)
        self.worker_thread.start()

    def do_import_module(self, class_name):
        logger.debug('Do import module')
        class_str = self._current_view.class_str
        self._current_view.view = load_module_from_code(class_str, class_name, self.driver)
        logger.debug(f'Imported module: {self._current_view.view}')

    @wait_for_thread
    def on_execute(self, function_str: str):
        logger.debug(f'Execute function: {function_str}')
        # get the function to execute
        selected_function = None
        for function in self._current_view.function_candidates:
            if function_str == str(function):
                selected_function = function
                break
        if selected_function is None:
            self.error_signal.emit(f"Function {function_str} not found")
            return
        self.worker_thread = WorkerThread(self.do_execute, selected_function)
        self.worker_thread.busy.connect(self.signals.processing.emit)
        self.worker_thread.result_signal.connect(lambda _: self.signals.connected.emit())
        self.worker_thread.error_signal.connect(self.on_error)
        self.worker_thread.start()

    def do_execute(self, selected_function: FunctionCall):
        logger.debug(f'Do Executing function: {selected_function}')
        selected_function.call(self._current_view.view)





