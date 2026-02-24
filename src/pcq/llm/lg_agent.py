from __future__ import annotations

import base64
from io import BytesIO
from typing import Literal, Optional, TypedDict, Union

import pyautogui
from PIL import Image

from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.05


# -------------------- Actions schema --------------------

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

class DecideOut(BaseModel):
    action: Action
    confidence: float = Field(ge=0.0, le=1.0)
    note: str = Field(default="", description="Short note for logs. No long reasoning.")


# -------------------- Graph state --------------------

class PCQState(TypedDict, total=False):
    goal: str
    step: int
    max_steps: int
    screenshot_b64: str
    last_result: str
    last_action: dict
    done: bool


# -------------------- Tools --------------------

def _screenshot_b64() -> str:
    img: Image.Image = pyautogui.screenshot()
    bio = BytesIO()
    img.save(bio, format="PNG")
    return base64.b64encode(bio.getvalue()).decode("utf-8")


def _execute_action(action: Action) -> str:
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


# -------------------- LLM --------------------
# Needs vision-capable model
llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0)


def _llm_decide(goal: str, screenshot_b64: str, last_result: str, step: int, max_steps: int) -> DecideOut:
    system = (
        "You are a Windows desktop control agent. "
        "You choose ONE action per step from: click/type/hotkey/wait/done. "
        "Prefer typing via the Start menu search when opening apps. "
        "Avoid risky clicks: only click when you clearly see the target. "
        "If uncertain, use hotkey('win') then type the app name. "
        "Return ONLY valid JSON matching the schema."
    )

    user = f"""Goal: {goal}
Step: {step}/{max_steps}
Last tool result: {last_result}

Look at the screenshot and choose the next single action.
Return only JSON.
"""

    msg = llm.invoke(
        [
            ("system", system),
            (
                "human",
                [
                    {"type": "text", "text": user},
                    {"type": "image_url", "image_url": f"data:image/png;base64,{screenshot_b64}"},
                ],
            ),
        ]
    )

    # LangChain returns text; parse with Pydantic
    return DecideOut.model_validate_json(msg.content)


def _llm_verify(goal: str, screenshot_b64: str) -> bool:
    system = (
        "You are a verifier. Decide if the goal is achieved in the screenshot. "
        "Answer ONLY 'YES' or 'NO'."
    )
    user = f"Goal: {goal}\nIs the goal achieved?"
    msg = llm.invoke(
        [
            ("system", system),
            (
                "human",
                [
                    {"type": "text", "text": user},
                    {"type": "image_url", "image_url": f"data:image/png;base64,{screenshot_b64}"},
                ],
            ),
        ]
    )
    return msg.content.strip().upper().startswith("YES")


# -------------------- Graph nodes --------------------

def sense_node(state: PCQState) -> PCQState:
    state["screenshot_b64"] = _screenshot_b64()
    state["step"] = state.get("step", 0) + 1
    return state


def think_node(state: PCQState) -> PCQState:
    out = _llm_decide(
        goal=state["goal"],
        screenshot_b64=state["screenshot_b64"],
        last_result=state.get("last_result", ""),
        step=state["step"],
        max_steps=state["max_steps"],
    )
    state["last_action"] = out.action.model_dump()
    return state


def act_node(state: PCQState) -> PCQState:
    action = DecideOut(action=state["last_action"], confidence=0.5).action  # placeholder cast
    # The above line is a hack; better: re-validate into Action union:
    action = (Click | TypeText | Hotkey | Wait | Done).model_validate(state["last_action"])  # type: ignore

    state["last_result"] = _execute_action(action)
    state["done"] = isinstance(action, Done)
    return state


def verify_node(state: PCQState) -> PCQState:
    # If model already said done, accept. Otherwise verify by screenshot.
    if state.get("done"):
        return state
    state["screenshot_b64"] = _screenshot_b64()
    achieved = _llm_verify(state["goal"], state["screenshot_b64"])
    state["done"] = achieved
    return state


def router(state: PCQState) -> str:
    if state.get("done"):
        return "end"
    if state["step"] >= state["max_steps"]:
        return "end"
    return "loop"


# -------------------- Build graph --------------------

def build_graph():
    g = StateGraph(PCQState)
    g.add_node("sense", sense_node)
    g.add_node("think", think_node)
    g.add_node("act", act_node)
    g.add_node("verify", verify_node)

    g.set_entry_point("sense")
    g.add_edge("sense", "think")
    g.add_edge("think", "act")
    g.add_edge("act", "verify")

    g.add_conditional_edges("verify", router, {"loop": "sense", "end": END})
    return g.compile()


def run(goal: str, max_steps: int = 12) -> PCQState:
    app = build_graph()
    init: PCQState = {"goal": goal, "max_steps": max_steps, "step": 0, "last_result": ""}
    return app.invoke(init)