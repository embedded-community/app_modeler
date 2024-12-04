import logging
from appium import webdriver

from app_modeler.models.StartOptions import StartOptions

logger = logging.getLogger(__name__)

def create_driver(start_options: StartOptions):
    options = start_options.appium_options
    logger.debug(f'Creating driver with options: {options.to_capabilities()}')
    return webdriver.Remote(start_options.appium_server_url, options=options)
