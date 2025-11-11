from typing import Callable

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait

from amzsc.utils import CustomTypes

CONDITION_TYPE = Callable[[tuple[str, str]], Callable[[WebDriver], WebElement | bool]]


class ChromeManipulator:
    def __init__(self, driver: CustomTypes.DRIVER_TYPE) -> None:
        self.driver = driver

    def __str__(self) -> str:
        return "DriverManipulator"

    def get(self, url: str) -> None:
        self.driver.get(url)

    def refresh(self) -> None:
        self.driver.refresh()

    def quit(self) -> None:
        self.driver.quit()

    def wait(self, timeout: int = 10) -> WebDriverWait:
        return WebDriverWait(self.driver, timeout)
