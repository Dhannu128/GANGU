"""
GANGU end-to-end smoke test
---------------------------

Runs the LangGraph pipeline against a few canonical Hindi/Hinglish requests and
prints a per-agent ✅/❌ summary. No API server needed.

Usage:
    python test_full_pipeline.py

Exit codes:
    0  all cases produced a final decision
    1  one or more cases failed before reaching a decision
"""
from __future__ import annotations

import os
import sys
import time
from pathlib import Path
from typing import Any, Dict

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Make local imports work regardless of cwd
ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

# Silence LangSmith if the key looks fake (otherwise we'll be flooded with 403s)
def _placeholder(value: str | None) -> bool:
    if not value:
        return True
    v = value.strip().lower()
    return len(v) < 20 or any(t in v for t in ("your", "placeholder", "here", "xxxx", "replace"))

if _placeholder(os.getenv("LANGSMITH_API_KEY")):
    os.environ["LANGSMITH_TRACING"] = "false"
    os.environ["LANGCHAIN_TRACING_V2"] = "false"

from orchestration.gangu_graph import create_gangu_graph

CASES = [
    "doodh khatam ho gaya",
    "atta le aao",
    "white chane mangwao",
]

CHECKS = [
    ("intent",     lambda s: bool(s.get("item_name"))),
    ("planner",    lambda s: bool(s.get("execution_steps"))),
    ("search",     lambda s: bool(s.get("search_results", {}).get("results"))),
    ("comparison", lambda s: bool(s.get("ranked_products"))),
    ("decision",   lambda s: s.get("decision_type") not in (None, "", "unknown")),
    ("response",   lambda s: bool(s.get("ai_response"))),
]


def run_case(graph, request: str) -> Dict[str, Any]:
    print(f"\n{'=' * 70}\n🎙️  Request: {request!r}\n{'=' * 70}")
    started = time.perf_counter()
    final_state = graph.invoke({"user_input": request, "messages": []})
    elapsed = time.perf_counter() - started

    results: Dict[str, bool] = {}
    for name, check in CHECKS:
        try:
            results[name] = bool(check(final_state))
        except Exception:
            results[name] = False

    print()
    for name, ok in results.items():
        print(f"  {'✅' if ok else '❌'}  {name}")
    print(f"\n  ⏱  {elapsed:5.2f}s   selected={final_state.get('selected_option', {}).get('platform') if final_state.get('selected_option') else '—'}")
    return {"request": request, "checks": results, "elapsed": elapsed, "state": final_state}


def main() -> int:
    print("🧪 GANGU pipeline smoke test")
    graph = create_gangu_graph()

    overall_ok = True
    for request in CASES:
        outcome = run_case(graph, request)
        if not all(outcome["checks"].values()):
            overall_ok = False

    print(f"\n{'=' * 70}")
    print("✅ All cases passed" if overall_ok else "❌ Some cases failed — see above")
    print(f"{'=' * 70}")
    return 0 if overall_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
