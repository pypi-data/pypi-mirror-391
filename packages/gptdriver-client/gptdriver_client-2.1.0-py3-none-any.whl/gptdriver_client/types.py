import time
from typing import Optional, List, Any, Literal, Callable, Awaitable, Union, Dict
from pydantic import BaseModel
from appium.webdriver.webdriver import WebDriver


class Command(BaseModel):
    method: Literal['GET', 'DELETE', 'POST'] = ""
    url: Optional[str] = None
    data: Any


class ExecuteResponse(BaseModel):
    commands: List[Command]
    status: Literal['inProgress', 'success', 'failed']
    gptCommands: List[str]


class DeviceSize(BaseModel):
    width: int
    height: int


AppiumHandler = Callable[[WebDriver], Awaitable[Any]]
PlatformLiteral = Literal['iOS', 'Android', 'ios', 'android']
LocatorValue = Union[str, Dict, None]


class SessionConfig(BaseModel):
    id: Optional[str] = None
    platform: Optional[PlatformLiteral] = None
    device_name: Optional[str] = None
    platform_version: Optional[str] = None
    size: Optional[DeviceSize] = None
    server_url: str


class ServerSessionInitConfig(BaseModel):
    platform: Optional[PlatformLiteral] = None
    device_name: Optional[str] = None
    platform_version: Optional[str] = None


class ServerConfig(BaseModel):
    url: Optional[str] = None
    device: Optional[ServerSessionInitConfig] = None


class GptDriverConfig(BaseModel):
    driver: Optional[WebDriver] = None
    server_config: Optional[ServerConfig] = None

    class Config:
        arbitrary_types_allowed = True


class GptDriverException(Exception):
    def __init__(
        self,
        exception: Exception,
        custom_error_message: Optional[str] = "",
        additional_context: Optional[str] = ""
    ):
        super().__init__(custom_error_message or str(exception))

        self.timestamp = time.time()
        self.custom_error_message = custom_error_message
        self.additional_context = additional_context
        self.__cause__ = exception
