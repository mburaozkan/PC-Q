from __future__ import annotations

from typing import Literal, Union
from pydantic import BaseModel, Field, TypeAdapter


class Click(BaseModel):
    type: Literal["click"] = "click"
    x: int
    y: int
    clicks: int = 1
    button: Literal["left", "right"] = "left"


class TypeText(BaseModel):
    type: Literal["type"] = "type"
    text: str
    enter: bool = False


class Hotkey(BaseModel):
    type: Literal["hotkey"] = "hotkey"
    keys: list[str]


class Wait(BaseModel):
    type: Literal["wait"] = "wait"
    seconds: float = 0.4


class Done(BaseModel):
    type: Literal["done"] = "done"
    note: str = ""


Action = Union[Click, TypeText, Hotkey, Wait, Done]

_action_adapter = TypeAdapter(Action)

class DecideOut(BaseModel):
    action: Action
    confidence: float = Field(ge=0.0, le=1.0)
    note: str = Field(default="", description="Short note for logs; no long reasoning.")


def parse_decide_out(json_text: str) -> DecideOut:
    return DecideOut.model_validate_json(json_text)


def parse_action_dict(d: dict) -> Action:
    # Re-validate into the union
    return _action_adapter.validate_python(d)