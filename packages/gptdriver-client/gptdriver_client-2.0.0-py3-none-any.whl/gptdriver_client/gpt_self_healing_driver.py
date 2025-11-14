import time
from typing import List, Union

from appium import webdriver
from appium.options.common import AppiumOptions
from appium.webdriver import WebElement as MobileWebElement
from appium.webdriver.appium_connection import AppiumConnection
from appium.webdriver.common.appiumby import AppiumBy
from selenium.common import WebDriverException

from .gpt_driver_core import GptDriverCore
from .helpers import get_api_from_capabilities, get_improved_locator
from .logging_config import logger
from .types import LocatorValue, GptDriverException


class GptSelfHealingDriver(webdriver.Remote):
    _NUMBER_OF_HEALING_RETRIES = 2

    def __init__(
        self,
        command_executor: Union[str, AppiumConnection],
        options: Union[AppiumOptions, List[AppiumOptions], None],
        **kwargs
    ):
        # TODO pass additionalUserContext: Optional[str] = None,
        super().__init__(command_executor=command_executor, options=options, **kwargs)

        api_key = get_api_from_capabilities(options)
        self._gpt_driver_core: GptDriverCore = GptDriverCore(api_key=api_key, driver=self)

    def _super_find_element_or_elements(
        self,
        by: str = AppiumBy.ID,
        value: LocatorValue = None,
        singular: bool = True
    ) -> Union[MobileWebElement, List[MobileWebElement]]:
        return super().find_element(by, value) if singular else super().find_elements(by, value)

    def _wait_for_element_displayed(
        self,
        by: str = AppiumBy.ID,
        value: LocatorValue = None,
        timeout: int = 5
    ) -> bool:
        logger().info(f">>\t Waiting {timeout}s for element to be displayed...")
        end_time = time.time() + timeout
        while time.time() < end_time:
            try:
                elements = super().find_elements(by, value)
                if elements and elements[0].is_displayed():
                    logger().info(f">>\t Element is displayed: {by}='{value}'")
                    return True
            except Exception:
                pass
            time.sleep(0.5)
        return False

    def _perform_self_healing_loop(
        self,
        by: str,
        value: LocatorValue,
        command: str,
        original_exception: Exception,
        find_single_element: bool
    ):
        gptdriver_exception = GptDriverException(original_exception)

        logger().info(f">>\t Attempting self-healing...")
        element_found = self._wait_for_element_displayed(by, value, timeout=5)
        if element_found:
            logger().info(f"\t Element found after waiting")
            self._gpt_driver_core._log_code_execution(command)
            return self._super_find_element_or_elements(by, value, find_single_element)
        else:
            logger().info(">>\t Element not found within timeout period")
            already_tried_locators = []
            for i in range(self._NUMBER_OF_HEALING_RETRIES + 1):
                if len(already_tried_locators) > 0:
                    additional_context = f" The following locators were already tried and did not work: {already_tried_locators}"
                    gptdriver_exception.additional_context = additional_context
                try:
                    improved_command = self._gpt_driver_core._perform_agentic_loop(command, True, gptdriver_exception)
                except WebDriverException as wde:
                    raise GptDriverException(wde, "Element not found after self-healing attempts")

                improved_by, improved_value = get_improved_locator(improved_command)
                logger().info(f">>\t Trying improved locator: by.{improved_by}='{improved_value}'")
                found_elements = super().find_elements(improved_by, improved_value)
                already_tried_locators.append(f"by.'{improved_by}', value='{improved_value}'")
                if found_elements:
                    logger().info(f">>\t Element found with the improved locator.")
                    return found_elements[0] if find_single_element else found_elements
                elif i < self._NUMBER_OF_HEALING_RETRIES:
                    logger().info(
                        f">>\t No elements found with the improved locator. Retrying ({i + 1}/{self._NUMBER_OF_HEALING_RETRIES})...")

            error_msg = f"Couldn't find a self-healing locator for: by='{by}', value='{value}'"
            gptdriver_exception.custom_error_message = error_msg
            self._gpt_driver_core._log_code_execution(command, original_exception=gptdriver_exception)
            self._gpt_driver_core.set_session_status("failed")
            raise GptDriverException(original_exception, error_msg)

    def _self_healing_find_element_or_elements(
        self,
        by: str = AppiumBy.ID,
        value: LocatorValue = None,
        singular: bool = True
    ) -> Union[MobileWebElement, List[MobileWebElement]]:
        command = "findElement" + ("" if singular else "s") + f"(by='{by}', value='{value}')"
        logger().info(f">> Executing command: {command}")
        try:
            element_or_elements = self._super_find_element_or_elements(by, value, singular)
            self._gpt_driver_core._log_code_execution(command)
            return element_or_elements
        except Exception as e:
            return self._perform_self_healing_loop(by, value, command, e, singular)

    def find_element(
        self,
        by: str = AppiumBy.ID,
        value: LocatorValue = None,
        enable_self_healing: bool = True
    ) -> MobileWebElement:
        if enable_self_healing:
            return self._self_healing_find_element_or_elements(by, value, singular=True)
        else:
            return super().find_element(by, value)

    def find_elements(
        self,
        by: str = AppiumBy.ID,
        value: LocatorValue = None,
        enable_self_healing: bool = True
    ) -> List[MobileWebElement]:
        if enable_self_healing:
            return self._self_healing_find_element_or_elements(by, value, singular=False)
        else:
            return super().find_elements(by, value)
