import base64
import io
import time
from dataclasses import dataclass

import requests
from PIL import Image, ImageChops
from typing import Optional

from gptdriver_client.types import GptDriverException


@dataclass
class Size:
    width: int
    height: int


@dataclass
class StabilityResult:
    stable: bool
    original_screenshot_base64: Optional[str] = None

    @property
    def original_screenshot(self) -> Optional[Image.Image]:
        if not self.original_screenshot_base64:
            return None
        decoded = base64.b64decode(self.original_screenshot_base64)
        return Image.open(io.BytesIO(decoded))


class ScreenStabilityDetector:
    def __init__(self, appium_session_config):
        self.appium_session_config = appium_session_config

    def _get_screenshot(self) -> str:
        config = self.appium_session_config
        url = f"{config.server_url}/session/{config.id}/screenshot"

        screenshot_response = requests.get(url).json()
        screenshot = screenshot_response["value"]

        if config.platform.lower() == "ios":
            image_bytes = base64.b64decode(screenshot)
            buffered_image = Image.open(io.BytesIO(image_bytes))
            resized_image = buffered_image.resize(
                (config.size.width, config.size.height)
            )
            buffer = io.BytesIO()
            resized_image.save(buffer, format="PNG")
            screenshot = base64.b64encode(buffer.getvalue()).decode("utf-8")

        return screenshot

    def wait_for_stable_screenshot(
        self,
        max_timeout_sec: float,
        interval_sec: float,
        tolerance: float,
        pixel_threshold: int,
        downscale_width: int,
        downscale_height: int,
    ) -> StabilityResult:
        start_time = time.time()
        max_timeout = max_timeout_sec
        interval = interval_sec

        prev_downsampled = None
        last_screenshot_base64 = None
        downscale_size = Size(downscale_width, downscale_height)

        while (time.time() - start_time) < max_timeout:
            try:
                screenshot_base64 = self._get_screenshot()
                last_screenshot_base64 = screenshot_base64

                decoded = base64.b64decode(screenshot_base64)
                screenshot = Image.open(io.BytesIO(decoded))

                downsampled = screenshot.resize(
                    (downscale_size.width, downscale_size.height)
                )

                if prev_downsampled:
                    similar = self._are_images_similar(
                        prev_downsampled, downsampled, tolerance, pixel_threshold
                    )
                    if similar:
                        return StabilityResult(True, screenshot_base64)

                prev_downsampled = downsampled

            except Exception as e:
                raise GptDriverException(e)
            finally:
                time.sleep(interval)

        return StabilityResult(False, last_screenshot_base64)

    def get_stable_screenshot(self) -> StabilityResult:
        return self.wait_for_stable_screenshot(
            max_timeout_sec=5.0,
            interval_sec=0.01,
            tolerance=0.00001,
            pixel_threshold=0,
            downscale_width=600,
            downscale_height=600,
        )

    @staticmethod
    def _are_images_similar(
        img1: Image.Image, img2: Image.Image, tolerance: float, pixel_threshold: int
    ) -> bool:
        if img1.size != img2.size:
            return False

        width, height = img1.size
        total_pixels = width * height

        diff = ImageChops.difference(img1, img2)
        diff_data = diff.getdata()

        different_pixels = 0
        for pixel in diff_data:
            if isinstance(pixel, int):  # grayscale
                if abs(pixel) > pixel_threshold:
                    different_pixels += 1
            else:
                if any(abs(c) > pixel_threshold for c in pixel[:3]):
                    different_pixels += 1

        diff_ratio = different_pixels / total_pixels
        return diff_ratio <= tolerance
