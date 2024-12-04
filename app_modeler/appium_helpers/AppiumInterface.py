from appium.webdriver.webdriver import WebDriver
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.remote.webelement import WebElement
from typing import Tuple

class AppiumInterface:
    def __init__(self, driver: WebDriver):
        """
        Initialize the interface with an Appium WebDriver instance.
        :param driver: The WebDriver instance for Appium.
        """
        self.driver: WebDriver = driver

    def click(self, locator: Tuple[AppiumBy, str]) -> None:
        """
        Click on an element located by the specified locator.
        :param locator: Tuple with (AppiumBy, value) e.g., (AppiumBy.ID, 'element_id')
        """
        element: WebElement = self.driver.find_element(*locator)
        element.click()

    def enter_text(self, locator: Tuple[AppiumBy, str], text: str) -> None:
        """
        Enter text into an input field located by the specified locator.
        :param locator: Tuple with (AppiumBy, value) e.g., (AppiumBy.ID, 'element_id')
        :param text: The text to enter into the input field.
        """
        element: WebElement = self.driver.find_element(*locator)
        element.send_keys(text)

    def get_text(self, locator: Tuple[AppiumBy, str]) -> str:
        """
        Retrieve the text of an element located by the specified locator.
        :param locator: Tuple with (AppiumBy, value) e.g., (AppiumBy.ID, 'element_id')
        :return: The text of the element.
        """
        element: WebElement = self.driver.find_element(*locator)
        return element.text

    def is_displayed(self, locator: Tuple[AppiumBy, str]) -> bool:
        """
        Check if an element located by the specified locator is displayed on the screen.
        :param locator: Tuple with (AppiumBy, value) e.g., (AppiumBy.ID, 'element_id')
        :return: True if the element is displayed, False otherwise.
        """
        element: WebElement = self.driver.find_element(*locator)
        return element.is_displayed()

    def swipe(self, start_x: int, start_y: int, end_x: int, end_y: int, duration: int = 800) -> None:
        """
        Swipe from one point to another on the screen.
        :param start_x: Starting X coordinate
        :param start_y: Starting Y coordinate
        :param end_x: Ending X coordinate
        :param end_y: Ending Y coordinate
        :param duration: Duration of the swipe in milliseconds (default is 800ms)
        """
        # For mac2 driver, using the `touch_action` might not be directly applicable.
        # Instead, using execute_script for desktop context interactions.
        self.driver.execute_script("mobile: swipe", {
            "startX": start_x,
            "startY": start_y,
            "endX": end_x,
            "endY": end_y,
            "duration": duration
        })

    def scroll_to_element(self, locator: Tuple[AppiumBy, str]) -> None:
        """
        Scroll to an element if it's not currently visible on the screen.
        :param locator: Tuple with (AppiumBy, value) e.g., (AppiumBy.ID, 'element_id')
        """
        element: WebElement = self.driver.find_element(*locator)
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)

    def wait_for_element(self, locator: Tuple[AppiumBy, str], timeout: int = 10) -> WebElement:
        """
        Wait for an element to be present and visible on the screen.
        :param locator: Tuple with (AppiumBy, value) e.g., (AppiumBy.ID, 'element_id')
        :param timeout: Maximum time to wait for the element in seconds (default is 10 seconds).
        :return: The found element if present within timeout.
        """
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC

        return WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_element_located(locator)
        )
