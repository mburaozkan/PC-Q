from __future__ import annotations

import pyautogui
from pcq.llm.schemas import Action, Click, TypeText, Hotkey, Wait, Done

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.05


def execute_action(action: Action) -> str:
    if isinstance(action, Click):
        pyautogui.click(x=action.x, y=action.y, clicks=action.clicks, button=action.button)
        return f"clicked({action.x},{action.y})"

    if isinstance(action, TypeText):
        pyautogui.write(action.text, interval=0.01)
        if action.enter:
            pyautogui.press("enter")
        return f"typed('{action.text}', enter={action.enter})"

    if isinstance(action, Hotkey):
        pyautogui.hotkey(*action.keys)
        return f"hotkey({action.keys})"

    if isinstance(action, Wait):
        pyautogui.sleep(action.seconds)
        return f"wait({action.seconds}s)"

    if isinstance(action, Done):
        return f"done({action.note})"

    return "unknown_action"