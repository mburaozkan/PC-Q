from __future__ import annotations

import base64
from io import BytesIO

import pyautogui
from PIL import Image

pyautogui.FAILSAFE = True


def screenshot_b64() -> str:
    img: Image.Image = pyautogui.screenshot()
    bio = BytesIO()
    img.save(bio, format="PNG")
    return base64.b64encode(bio.getvalue()).decode("utf-8")