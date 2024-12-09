from typing import Union

from appium.webdriver import WebElement
from appium.webdriver.webdriver import WebDriver
from selenium.webdriver.common.by import By

from app_modeler.appium_helpers.elements.element_type_mapping_android import element_type_mapping_android
from app_modeler.appium_helpers.elements.element_type_mapping_mac import xcui_element_type_mapping, \
    element_type_mapping_mac


def resolve_root(driver: WebDriver) -> Union[WebDriver, WebElement]:
    """ Resolve the root element for the driver """
    platform = driver.capabilities.get('platformName')
    if platform == 'android':
        return driver
    if platform == 'mac':
        window = driver.find_elements(By.XPATH, "//XCUIElementTypeWindow")[0]
        return window
    raise ValueError(f"Unknown platform: {platform}")

def get_element_details(automationName: str, element: WebElement) -> dict:
    """
    Get element details in a dict format based on the driver type.
    :param driver: Appium driver instance.
    :param element: WebElement object.
    """

    resolve_method = _get_resolve_method(automationName.lower())
    details = resolve_method(element)
    return details

def _get_resolve_method(automationName: str):
    """
    Map driver type to the appropriate attribute resolver method.
    :param driver_type: Driver type as a string.
    :return: Callable method to resolve element attributes.
    """
    resolvers = {
        "uiautomator2": _resolve_android_uiautomator2,
        "expresso": _resolve_android_espresso,
        "xcuitest": _resolve_ios_xcuitest,
        "ios": _resolve_ios_safari,
        "mac2": _resolve_mac,
        "windows": _resolve_windows,
    }
    if automationName not in resolvers:
        raise ValueError(f"No resolver defined for automation name: {automationName}")
    return resolvers[automationName]


def _resolve_android_uiautomator2(element: WebElement) -> dict:
    return _resolve_common_android_attributes(element)


def _resolve_android_espresso(element: WebElement) -> dict:
    return _resolve_common_android_attributes(element)


def _resolve_common_android_attributes(element: WebElement) -> dict:
    element_class = element.get_dom_attribute("class")
    element_type = element_type_mapping_android.get(element_class)
    if not element_type:
        raise ValueError(f"Unknown element class: {element_class}")
    return {
        "type": element_type,
        "tag": element.tag_name,
        "resource_id": element.get_dom_attribute("resource-id"),
        "clickable": element.get_attribute("clickable") == "true",
        "checked": element.get_attribute("checked") == "true",
        "long_clickable": element.get_attribute("long-clickable") == "true",
        "scrollable": element.get_attribute("scrollable") == "true",
        "password": element.get_attribute("password") == "true",
        "content_desc": element.get_attribute("content-desc"),
        "focusable": element.get_attribute("focusable") == "true",
    }


def _resolve_ios_xcuitest(element: WebElement) -> dict:
    element_xcui_type = element.get_attribute("elementType")
    xcui_type = xcui_element_type_mapping.get(element_xcui_type)
    element_type = element_type_mapping_mac.get(xcui_type),
    if not element_type:
        raise ValueError(f"Unknown element type: {element_xcui_type}")
    return {
        "type": element_type,
        "label": element.get_attribute("label"),
        "value": element.get_attribute("value"),
    }


def _resolve_ios_safari(element: WebElement) -> dict:
    return {
        "type": "web_element",
        "tag": element.tag_name,
    }

def _resolve_mac(element: WebElement) -> dict:
    element_xcui_type = element.get_attribute("elementType")
    xcui_type = xcui_element_type_mapping.get(element_xcui_type)
    element_type = element_type_mapping_mac.get(xcui_type)
    if not element_type:
        raise ValueError(f"Unknown element type: {element_xcui_type}")
    label = element.get_attribute("label")
    xpath = f"//{xcui_type}[@label='{label}']"
    return {
        "type": element_type,
        "xpath": xpath,
        "label": label,
    }


def _resolve_windows(element: WebElement) -> dict:
    return {
        "type": element.get_attribute("ControlType"),
        "automation_id": element.get_attribute("AutomationId"),
        "name": element.get_attribute("Name"),
    }

if __name__ == "__main__":
    from appium.options.mac import Mac2Options
    options = Mac2Options()
    options.platform_name = "macOS"
    options.automation_name = "Mac2"
    options.app = "com.google.Chrome"
    print(options.to_capabilities())
