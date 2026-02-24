from __future__ import annotations

from langchain_openai import ChatOpenAI
from pcq.llm.prompts import DECIDE_SYSTEM, VERIFY_SYSTEM
from pcq.llm.schemas import DecideOut, parse_decide_out


def get_llm(model: str = "gpt-4.1-mini", temperature: float = 0.0) -> ChatOpenAI:
    # Vision-capable model required (we send screenshots)
    return ChatOpenAI(model=model, temperature=temperature)


def llm_decide(*, llm: ChatOpenAI, goal: str, screenshot_b64: str, last_result: str, step: int, max_steps: int) -> DecideOut:
    user = f"""Goal: {goal}
Step: {step}/{max_steps}
Last tool result: {last_result}

Look at the screenshot and choose the next single action.
Return only JSON.
"""
    msg = llm.invoke(
        [
            ("system", DECIDE_SYSTEM),
            (
                "human",
                [
                    {"type": "text", "text": user},
                    {"type": "image_url", "image_url": f"data:image/png;base64,{screenshot_b64}"},
                ],
            ),
        ]
    )
    return parse_decide_out(msg.content)


def llm_verify(*, llm: ChatOpenAI, goal: str, screenshot_b64: str) -> bool:
    user = f"Goal: {goal}\nIs the goal achieved?"
    msg = llm.invoke(
        [
            ("system", VERIFY_SYSTEM),
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