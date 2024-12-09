import logging
from dataclasses import dataclass, field, fields
from typing import Optional, Dict, Any

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

    # Android-specific fields
    tag: Optional[str] = None
    resource_id: Optional[str] = None
    clickable: Optional[bool] = None
    checked: Optional[bool] = None
    long_clickable: Optional[bool] = None
    scrollable: Optional[bool] = None
    password: Optional[bool] = None
    content_desc: Optional[str] = None
    focusable: Optional[bool] = None
    # iOS/XCUITest-specific fields
    label: Optional[str] = None
    value: Optional[str] = None
    # macOS-specific fields
    xpath: Optional[str] = None
    # Windows-specific fields
    automation_id: Optional[str] = None
    name: Optional[str] = None

    def asdict_custom(self):
        result = {}
        for f in fields(self):
            if f.metadata.get('exclude'):
                continue
            value = getattr(self, f.name)
            if value is None or value == 'null':
                continue
            result[f.name] = value
        return result


class ElementsDiscover:
    def __init__(self, driver):
        self.driver = driver

    def scan_view(self, progress_callback) -> [ElementData]:
        """ Scan the current view and return elements data as json """
        elements_data = []
        root = resolve_root(self.driver)
        elements = root.find_elements(by=By.XPATH, value='//*')
        for element in elements:
            try:
                elem_data = self.detect_element(element)
            except ValueError as error:
                logger.warning(f"Error detecting element: {error}")
                continue
            elements_data.append(elem_data)
            progress_callback(len(elements_data))

        if not elements_data:
            raise StopIteration("No elements found in the view")
        return elements_data

    def detect_element(self, element) -> ElementData:
        """ Detect element data. Raise ValueError if element is not visible or enabled or if details are not found """
        try:
            is_enabled = element.get_attribute('enabled') == 'true'
            if not (element.is_displayed() or is_enabled):
                raise ValueError("Element is not displayed or enabled")
        except StaleElementReferenceException as error:
            logger.warning(f"Error checking if element is displayed: {error}")
            # assume no more elements are visible
            raise ValueError("Element is not displayed or enabled")

        try:
            automationName = self.driver.capabilities.get("automationName")
            details = get_element_details(automationName=automationName, element=element)
        except (StaleElementReferenceException, NoSuchAttributeException, KeyError) as error:
            raise ValueError(str(error)) from error

        return ElementData( element=element,
                            text=element.text,
                            location=element.location,
                            **details)


