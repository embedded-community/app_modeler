from dataclasses import dataclass

from appium.options.common import AppiumOptions

from app_modeler.models.AppSettings import AppSettings


@dataclass
class StartOptions:
    app_settings: AppSettings
    appium_options: AppiumOptions
    appium_server_url: str = 'http://localhost:4723'
