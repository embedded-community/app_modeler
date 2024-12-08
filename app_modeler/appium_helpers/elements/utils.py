from typing import Union

from appium.webdriver import WebElement
from appium.webdriver.webdriver import WebDriver
from selenium.webdriver.common.by import By

from app_modeler.appium_helpers.elements.element_type_mapping_android import element_type_mapping_android
from app_modeler.appium_helpers.elements.element_type_mapping_mac import xcui_element_type_mapping, \
    element_type_mapping_mac
from selenium.common.exceptions import InvalidArgumentException


def resolve_root(driver: WebDriver) -> Union[WebDriver, WebElement]:
    """ Resolve the root element for the driver """
    platform = driver.capabilities.get('platformName')
    if platform == 'android':
        return driver
    if platform == 'mac':
        window = driver.find_elements(By.XPATH, "//XCUIElementTypeWindow")[0]
        return window
    raise ValueError(f"Unknown platform: {platform}")


def get_element_details(platform: str, element: WebElement) -> dict:
    """
    Get element details in a dict format.
    :param platform: platform name
    :param element: WebElement object
    """

    is_clickable = None
    is_accessible = None
    xpath = None
    tag = None
    resource_id = None

    try:
        if platform == 'android':
            element_type_org = element.get_dom_attribute("class")
            element_type = element_type_mapping_android[element_type_org]
            resource_id = element.get_dom_attribute('resource-id')
            tag = element.tag_name
            is_clickable = element.get_attribute('clickable') == 'true'

        elif platform == 'mac':
            element_type_org = element.get_attribute("elementType")
            xcui_type = xcui_element_type_mapping.get(element_type_org)
            element_type = element_type_mapping_mac.get(xcui_type)

            #attributes = ['elementType', 'enabled', 'focused', 'frame', 'hittable', 'identifier', 'label',
            #              'placeholderValue', 'selected', 'title', 'value']
            #def get_attribute(attr):
            #    try:
            #        return element.get_attribute(attr)
            #    except Exception as error:
            #        return f'N/A: {error}'
            #for attr in attributes:
            #    value = get_attribute(attr)
            #    print(f"{attr}: {value}")


            label = element.get_attribute('label')
            xpath = f"//{xcui_type}[@label='{label}']"

            print(f'tag: {element.tag_name}') if element.tag_name else None
            print(f'xpath: {xpath}') if xpath else None
        else:
            raise ValueError(f"Unknown platform: {platform}")

    except InvalidArgumentException:
        raise ValueError("Error getting element details")

    if not element_type:
        # logger.debug(f'Element type not known: {element.get_dom_attribute("class")}')
        raise ValueError(f"Element type not known: {xpath}")

    if not (tag or resource_id or xpath):
        raise ValueError("No tag or resource_id")


    out = {
        "type": element_type,
        "tag": tag,
        "resource_id": resource_id,
        "is_clickable": is_clickable,
        "is_accessible": is_accessible,
        "xpath": xpath
    }
    # cleanup None values
    return {k: v for k, v in out.items() if v is not None}


if __name__ == "__main__":
    from appium.options.mac import Mac2Options
    options = Mac2Options()
    options.platform_name = "macOS"
    options.automation_name = "Mac2"
    options.app = "com.google.Chrome"
    print(options.to_capabilities())
