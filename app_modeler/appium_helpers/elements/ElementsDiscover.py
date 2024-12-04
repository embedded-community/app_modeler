import logging
from dataclasses import dataclass, field, fields

from selenium.common import StaleElementReferenceException, NoSuchAttributeException
from selenium.webdriver.common.by import By

from app_modeler.appium_helpers.elements.element_type import get_type

logger  = logging.getLogger(__name__)

@dataclass
class ElementData:
    """ Pre-extracted element data"""
    element: object = field(repr=False, metadata={'exclude': True})
    text: str
    location: dict
    type: str
    tag: str
    resource_id: str
    is_clickable: bool
    is_visible: bool = True

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

    def scan_view(self, by: By = By.XPATH, value: str = "//*") -> [ElementData]:
        """ Scan the current view and return elements data as json """
        platform = self.driver.capabilities.get('platformName')

        elements_data = []
        elements = self.driver.find_elements(by, value)
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
        assert platform in ['android', 'mac'], f"Unknown platform: {platform}"
        try:
            element_type = get_type(platform=platform, element=element)
        except (StaleElementReferenceException, NoSuchAttributeException, KeyError):
            raise ValueError(f"Error getting element type: {element.get_dom_attribute('class')}")

        if not element_type:
            # logger.debug(f'Element type not known: {element.get_dom_attribute("class")}')
            raise ValueError(f"Element type not known: {element.get_dom_attribute('class')}")

        resource_id = element.get_dom_attribute('resource-id')
        tag = element.tag_name

        if not (tag or resource_id):
            raise ValueError("No tag or resource_id")

        is_enabled = element.get_attribute('enabled') == 'true'
        try:
            if not element.is_displayed() or not is_enabled:
                raise ValueError("Element is not displayed or enabled")
        except StaleElementReferenceException as error:
            logger.warning(f"Error checking if element is displayed: {error}")
            # assume no more elements are visible
            raise ValueError("Element is not displayed or enabled")

        is_clickable = element.get_attribute('clickable') == 'true'
        return ElementData( element=element,
                            text=element.text,
                            location=element.location,
                            type=element_type,
                            tag=tag,
                            resource_id=resource_id,
                            is_clickable=is_clickable)


