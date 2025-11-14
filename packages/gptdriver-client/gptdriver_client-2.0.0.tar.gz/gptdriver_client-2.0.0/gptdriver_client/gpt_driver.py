from typing import Optional, List, Literal, Dict, Any, Union

from appium.options.common import AppiumOptions
from appium.webdriver.appium_connection import AppiumConnection

from .gpt_self_healing_driver import GptSelfHealingDriver
from .types import AppiumHandler


class GptDriver(GptSelfHealingDriver):
    def __init__(
        self,
        command_executor: Union[str, AppiumConnection],
        options: Union[AppiumOptions, List[AppiumOptions], None],
        **kwargs
    ):
        """
        Initializes the GptDriver instance.

        Args:
            command_executor: The command executor URL or connection (e.g. http://localhost:4723).
            options: The Appium options. Requires 'gptdriver:apiKey' in capabilities.
            **kwargs: Additional keyword arguments passed to the driver initializer.
        """
        super().__init__(command_executor, options, **kwargs)

    def ai_execute(self, command: str, appium_handler: Optional[AppiumHandler] = None):
        """
        Executes a specified command within the WebDriver session, optionally using an Appium handler.

        If an `appiumHandler` is provided, it will be invoked to perform the command operations.
        If the handler execution fails or no handler is provided, the command gets executed by the GPTDriver using just natural language.

        Args:
            command (str): The natural language command to be executed by the GPTDriver.
            appium_handler (Optional[AppiumHandler]): An optional function that processes Appium-specific commands.
                                                     If provided, this handler is executed instead of calling the GPTDriver servers.
        """
        return self._gpt_driver_core.execute(command, appium_handler)

    def ai_assert(self, assertion: str):
        """
        Asserts a single condition using the GPT Driver.
        If the assertion fails, an error is thrown.

        Args:
            assertion (str): The condition to be asserted.
        """
        return self._gpt_driver_core.assert_condition(assertion)

    def ai_assert_bulk(self, assertions: List[str]):
        """
        Asserts multiple conditions using the GPT Driver.
        If any of the assertion fails, an error is thrown.

        Args:
            assertions (List[str]): An array of conditions to be asserted.
        """
        return self._gpt_driver_core.assert_bulk(assertions)

    def ai_check_bulk(self, conditions: List[str]) -> Dict[str, bool]:
        """
        Checks multiple conditions and returns their results using the GPT Driver.
        Does not throw an error if any of the conditions fail.

        Args:
            conditions (List[str]): An array of conditions to be checked.
        """
        return self._gpt_driver_core.check_bulk(conditions)

    def ai_extract(self, extractions: List[str]) -> Dict[str, Any]:
        """
        Extracts specified information using the GPT Driver.

        Args:
            extractions (List[str]): An array of extraction criteria.
        """
        return self._gpt_driver_core.extract(extractions)

    def ai_extract_remembered(self, key: str) -> Any:
        raise NotImplementedError("Method ai_extract_remembered is not implemented yet.")

    def set_session_status(self, status: Literal["failed", "success"]):
        """
        Stops the current GPTDriver session and updates its state.
        Args:
            status (Literal["failed", "success"]): Indicates the outcome of the session.
        """
        return self._gpt_driver_core.set_session_status(status)
