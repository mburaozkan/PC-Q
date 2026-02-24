from __future__ import annotations
from dotenv import load_dotenv

import argparse
from pcq.graph import build_graph, PCQState

load_dotenv()

def main():
    p = argparse.ArgumentParser()
    p.add_argument("goal", nargs="+", help='Example: open "League of Legends"')
    p.add_argument("--max-steps", type=int, default=12)
    p.add_argument("--model", type=str, default="gpt-4.1-mini")
    p.add_argument("--dry-run", action="store_true", help="Print actions, do not execute.")
    args = p.parse_args()

    app = build_graph()

    init: PCQState = {
        "goal": " ".join(args.goal),
        "max_steps": args.max_steps,
        "step": 0,
        "last_result": "",
        "model_name": args.model,
        "dry_run": args.dry_run,
    }

    final_state = app.invoke(init)
    print("done =", final_state.get("done"), "steps =", final_state.get("step"))


if __name__ == "__main__":
    main()