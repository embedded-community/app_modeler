import logging
from dataclasses import dataclass, field, fields
from typing import Optional

from selenium.common import StaleElementReferenceException, NoSuchAttributeException
from selenium.webdriver.common.by import By

from app_modeler.appium_helpers.elements.utils import get_element_details, resolve_root

logger  = logging.getLogger(__name__)

@dataclass
class ElementData:
    """ Pre-extracted element data"""
    element: object = field(repr=False, metadata={'exclude': True})
    text: str
    location: dict
    type: str
    tag: Optional[str] = None
    resource_id: Optional[str] = None
    is_clickable: Optional[bool] = None
    is_accessible: Optional[bool] = None
    xpath: Optional[str] = None
    is_visible: Optional[bool] = True

    def asdict_custom(self):
        result = {}
        for f in fields(self):
            if f.metadata.get('exclude'):
                continue
            result[f.name] = getattr(self, f.name)
        return result


class ElementsDiscover:
    def __init__(self, driver):
        self.driver = driver

    def scan_view(self) -> [ElementData]:
        """ Scan the current view and return elements data as json """
        platform = self.driver.capabilities.get('platformName')

        elements_data = []

        root = resolve_root(self.driver)
        elements = root.find_elements(by=By.XPATH, value='//*')
        for element in elements:
            try:
                elem_data = self.detect_element(platform, element)
            except ValueError as error:
                logger.warning(f"Error detecting element: {error}")
                continue
            elements_data.append(elem_data)

        if not elements_data:
            raise StopIteration("No elements found in the view")
        return elements_data

    @staticmethod
    def detect_element(platform: str, element) -> ElementData:
        """ Detect element data. Raise ValueError if element is not visible or enabled or if details are not found """
        assert platform in ['android', 'mac'], f"Unknown platform: {platform}"

        try:
            is_enabled = element.get_attribute('enabled') == 'true'
            if not element.is_displayed() and not is_enabled:
                raise ValueError("Element is not displayed or enabled")
        except StaleElementReferenceException as error:
            logger.warning(f"Error checking if element is displayed: {error}")
            # assume no more elements are visible
            raise ValueError("Element is not displayed or enabled")

        try:
            details = get_element_details(platform=platform, element=element)
        except (StaleElementReferenceException, NoSuchAttributeException, KeyError) as error:
            raise ValueError(str(error)) from error

        return ElementData( element=element,
                            text=element.text,
                            location=element.location,
                            **details)


