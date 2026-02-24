from __future__ import annotations
from typing import TypedDict


class PCQState(TypedDict, total=False):
    goal: str
    step: int
    max_steps: int

    screenshot_b64: str

    last_result: str
    last_action: dict  # raw dict from DecideOut.action

    done: bool

    model_name: str

    dry_run: bool