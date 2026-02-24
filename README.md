# PC-Q

Agentic PC Control System.

PC-Q is a LangGraph-powered AI system that:
- Understands user commands (e.g., "open league of legends")
- Plans execution steps
- Uses screenshot, click, and typing tools
- Optionally integrates object detection (YOLO/DETR)

## Architecture
- LLM (OpenAI API)
- LangGraph planning
- Screenshot tool
- Mouse/keyboard control
- Vision model (future)

## Roadmap
- [X] Step printing before execution
- [X] Vision grounding
- [ ] Safety constraints
- [ ] Multi-app generalization