import textwrap
from typing import Optional

from PySide6.QtCore import QObject

from app_modeler.widgets.FormGenerator import MultilineStr, SecretStr


class AppSettings(QObject):
    def __init__(self):
        super().__init__()
        self._appium_server: str = None
        #self._ai_service: str = "openai"
        self._token: SecretStr = SecretStr("")
        self._base_url: Optional[str] = None
        self._model: Optional[str] = 'gpt-4o-mini'

        self._class_generator_prompt: MultilineStr = MultilineStr(textwrap.dedent("""
            Generate a Python class {class_name} with best practises, inheriting from AppiumInterface for an Appium-based view model.
            Include the following elements and output only the class code without any comments or additional text.
            Do not include any prefixes or suffixes like ```python."
            
            Create a class that inherits from ‘AppiumInterface’. 
            The ‘AppiumInterface’ base class has the following methods:
                •click(locator: Tuple[AppiumBy, str]) -> None
                •enter_text(locator: Tuple[AppiumBy, str], text: str) -> None
                •get_text(locator: Tuple[AppiumBy, str]) -> str
                •is_displayed(locator: Tuple[AppiumBy, str]) -> bool
                •swipe(start_x: int, start_y: int, end_x: int, end_y: int, duration: int = 800) -> None
                •scroll_to_element(locator: Tuple[AppiumBy, str]) -> None
                •wait_for_element(locator: Tuple[AppiumBy, str], timeout: int = 10) -> WebElement
            
            Elements: {elements_json}
            
            Include methods that call the base class methods for each actionable element, 
            using the element name as the function name and type as prefix. 
             e.g. 'def button_press_start(self)` or `def textbox_enter_email(self, email: str)`.
            
            Use the following method signature for the constructor:
            
            def __init__(self, driver):
                super().init(driver)
            
            Define locators as tuples of (AppiumBy, value), for example:
            (AppiumBy.ACCESSIBILITY_ID, ‘’) or (AppiumBy.ID, ‘<resource_id>’). Prefer using the resource_id if available.
            
            Include the following imports:
            from appium.webdriver.common.appiumby import AppiumBy
            from app_modeler.appium_helpers.AppiumInterface import AppiumInterface
            """).strip())

        self._tester_prompt = MultilineStr(textwrap.dedent("""
                Be as tester, who test UI application happy scenario and
                provide options for next steps to perform on the view.
                Give multiple options, sorted by most likely to least likely.
                Prefer button_press or textbox_enter methods.
                Give only the method call as a string, e.g. click_tab1.
                Do not include parenthesis ("()").
                Do not include anything else in response.
                Previous steps was: {previous_steps}, do not repeat unless it's only option.
                please review the following class content: {class_docstring}
              """).strip())

    #@property
    #def ai_service(self) -> str:
    #    """ Get the AI service, default is openai """
    #    return self._ai_service

    #@ai_service.setter
    #def ai_service(self, value: str):
    #    """ Set the AI service """
    #    self._ai_service = value

    @property
    def base_url(self) -> Optional[str]:
        """ Get the base url """
        return self._base_url

    @base_url.setter
    def base_url(self, value: Optional[str]):
        """ Set the base url """
        self._base_url = value

    @property
    def token(self) -> SecretStr:
        """ Get the openapi token secret """
        return self._token

    @token.setter
    def token(self, value: SecretStr):
        """ Set the openapi toke secret """
        self._token = value

    @property
    def model(self) -> Optional[str]:
        """ Get the model. Default is gpt-4o-mini """
        return self._model

    @model.setter
    def model(self, value: Optional[str]):
        """ Set the model """
        self._model = value

    def update(self, settings: 'AppSettings'):
        """ Update the settings """
        self._appium_server = settings._appium_server
        #self.ai_service = settings.ai_service
        self.token = settings.token
        self.base_url = settings.base_url
        self.model = settings.model
        self.class_generator_prompt = settings.class_generator_prompt

    @property
    def class_generator_prompt(self) -> MultilineStr:
        """ Get the class generator prompt """
        return self._class_generator_prompt

    @class_generator_prompt.setter
    def class_generator_prompt(self, value: MultilineStr):
        """ Set the class generator prompt """
        self._class_generator_prompt = value

    @property
    def tester_prompt(self) -> MultilineStr:
        """ Get the tester prompt """
        return self._tester_prompt

    @tester_prompt.setter
    def tester_prompt(self, value: MultilineStr):
        """ Set the tester prompt """
        self._tester_prompt = value
