import json
import logging
from typing import Optional

from PySide6.QtCore import QObject, Signal, QSettings
from appium import webdriver
from selenium.common import NoSuchDriverException, InvalidSessionIdException
from selenium.webdriver.common.by import By

from app_modeler.ai.OpenAiAssistant import OpenAIAssistant
from app_modeler.ai.AppiumClassGenerator import AppiumClassGenerator
from app_modeler.ai.TesterAi import TesterAi
from app_modeler.appium_helpers.drivers.create import create_driver
from app_modeler.appium_helpers.elements.ElementsDiscover import ElementsDiscover
from app_modeler.appium_helpers.elements.utils import resolve_root
from app_modeler.models.AppSettings import AppSettings
from app_modeler.models.FunctionCall import FunctionCall
from app_modeler.models.StartOptions import StartOptions
from app_modeler.models.TestSession import TestSession, ClassData
from app_modeler.models.WorkerThread import WorkerThread
from app_modeler.utils.utils import load_module_from_code, generate_class_json_from_code

logger = logging.getLogger(__name__)


class Signals(QObject):
    connect = Signal(StartOptions)
    connected = Signal()
    disconnect = Signal()
    disconnected = Signal()
    analyse = Signal()
    execute = Signal(FunctionCall)
    executed = Signal(FunctionCall)


    status_message = Signal(str)

    processing = Signal(bool)
    screenshot = Signal(bytearray)
    tokens_spend = Signal(int)
    class_propose = Signal(str)
    elements_propose = Signal(str)
    import_module = Signal()
    module_imported = Signal()
    next_func_candidates = Signal()


class ModelerState(QObject):
    error_signal = Signal(Exception)
    def __init__(self, app_settings: AppSettings):
        super().__init__()
        self._app_settings = app_settings
        self._appium_options: Optional[StartOptions] = None
        self.ai_assistant: Optional[OpenAIAssistant] = None
        self.signals = Signals()
        self.session = TestSession()
        self.worker_thread = None
        self.driver: webdriver = None
        self.settings = QSettings("app_modeler.ini", QSettings.Format.IniFormat)
        self._current_view: Optional[ClassData] = None
        self._view_index = 0
        self._connect_signals()

    def _connect_signals(self):
        self.signals.connect.connect(self.on_connect)
        self.signals.disconnect.connect(self.on_disconnect)
        self.signals.analyse.connect(self.on_analyse)
        self.signals.import_module.connect(self.on_import_module)
        self.signals.execute.connect(self.on_execute)
        self.signals.executed.connect(self.session.call_history.append)

    @property
    def current_view(self) -> Optional[ClassData]:
        return self._current_view

    @property
    def app_settings(self) -> AppSettings:
        return self._app_settings

    @property
    def appium_options(self) -> StartOptions:
        return self._appium_options

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
        self.signals.status_message.emit('Connecting to appium server')
        self._appium_options = start_options
        self.driver = create_driver(start_options)
        token = start_options.app_settings.token
        base_url = start_options.app_settings.base_url
        model = start_options.app_settings.model
        self.ai_assistant = OpenAIAssistant(api_key=token, base_url=base_url, model=model)
        return self.get_screenshot()

    def get_screenshot(self):
        root = resolve_root(self.driver)
        if isinstance(root, webdriver.Remote):
            return root.get_screenshot_as_png()
        return root.screenshot_as_png

    def on_connected(self, screenshot: bytes):
        self.signals.screenshot.emit(screenshot)
        self.signals.connected.emit()

    @wait_for_thread
    def on_disconnect(self):
        if self.driver is not None:
            try:
                self.driver.quit()
            except InvalidSessionIdException:
                pass
        self.driver = None
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

        self.signals.status_message.emit('Capturing screenshot')
        screenshot = self.get_screenshot()
        self.signals.screenshot.emit(bytearray(screenshot))

        logger.debug('Discover elements')
        self.signals.status_message.emit('Discovering elements')
        discover = ElementsDiscover(self.driver)
        elements_data = discover.scan_view()
        elements_str = json.dumps([elem.asdict_custom() for elem in elements_data], indent=4)
        self.signals.elements_propose.emit(elements_str)

        # look if we have a previous class
        class_data: ClassData = next((cd for cd in self.session.classes
                                      if cd.elements == elements_data),  # compare elements
                                     None)
        if class_data:
            logger.debug('Found previous class, reuse it')
            self._current_view = class_data
            class_name = class_data.name
            class_str = class_data.class_str
        else:
            logger.debug('Generate class code')
            self.signals.status_message.emit('Generating class code')
            class_name = f'View{self._view_index}'
            self._view_index += 1
            class_generator = AppiumClassGenerator(self.ai_assistant, prompt_template=self.app_settings.class_generator_prompt)
            class_str = class_generator.generate(class_name=class_name, elements=elements_data)
            self.signals.tokens_spend.emit(self.ai_assistant.used_tokens)

        self.signals.class_propose.emit(class_str)

        logger.debug('Ask next functions')
        self.signals.status_message.emit('Asking next functions')
        tester = TesterAi(self.ai_assistant, prompt_template=self.app_settings.tester_prompt)

        class_docstring = generate_class_json_from_code(class_str, class_name)
        previous_steps = [str(func_call) for func_call in self.session.call_history]
        logger.debug(f"Previous steps: {previous_steps}")
        next_functions: [FunctionCall] = tester.ask_next_step(class_docstring, previous_steps=previous_steps)
        logger.debug(f"Next functions: {next_functions}")
        self.signals.tokens_spend.emit(self.ai_assistant.used_tokens)

        if not class_data:
            # create new class
            class_data = ClassData(name=class_name,
                                   screenshot=screenshot,
                                   elements=elements_data,
                                   class_str=class_str,
                                   function_candidates=next_functions)
            self.session.classes.append(class_data)
            self._current_view = class_data
        else:
            # update new next function candidates
            class_data.function_candidates = next_functions

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
    def on_execute(self, function_call: FunctionCall):
        logger.debug(f'Execute function: {function_call}')
        self.worker_thread = WorkerThread(self.do_execute, function_call)
        self.worker_thread.busy.connect(self.signals.processing.emit)
        self.worker_thread.result_signal.connect(self.signals.executed.emit)
        self.worker_thread.error_signal.connect(self.on_error)
        # append function call to call history even if it fails
        self.worker_thread.error_signal.connect(lambda _: self.session.call_history.append(function_call))
        self.worker_thread.start()

    def do_execute(self, function_call: FunctionCall) -> FunctionCall:
        function_call.call(self._current_view.view)
        return function_call





