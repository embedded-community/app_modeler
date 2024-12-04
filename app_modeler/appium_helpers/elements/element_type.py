from app_modeler.appium_helpers.elements.element_type_mapping_android import element_type_mapping_android
from app_modeler.appium_helpers.elements.mac_element_type_mapping import xcui_element_type_mapping, \
    element_type_mapping_mac


def get_type(platform: str, element):
    """ Get standardized element type """
    if platform == 'android':
        element_type_org = element.get_dom_attribute("class")
        element_type = element_type_mapping_android[element_type_org]
    elif platform == 'mac':
        element_type_org = element.get_dom_attribute("class")
        xcui_type = xcui_element_type_mapping[element_type_org]
        element_type = element_type_mapping_mac[xcui_type]
    else:
        raise KeyError(f"Unknown platform: {platform}")
    return element_type
