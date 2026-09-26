"""Run repeatable StockPilot Tool evaluations with a real configured model."""

from __future__ import annotations

import argparse
import asyncio
from collections import Counter
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from typing import Any

from pydantic_evals import Dataset

BACKEND = Path(__file__).resolve().parents[1] / "backend"
sys.path.insert(0, str(BACKEND))

from app.agent.service import AgentExecutionError, StockAgentService  # noqa: E402
from app.agent.tools import AgentDependencies  # noqa: E402
from app.core.config import Settings  # noqa: E402
from app.database.session import create_database_engine, create_session_factory, init_db  # noqa: E402
from app.services.chat import ChatService  # noqa: E402
from app.services.market import MarketService  # noqa: E402
from app.services.stock import StockService  # noqa: E402
from app.services.trace import TraceService  # noqa: E402
from app.services.watchlist import WatchlistService  # noqa: E402
from fixtures import EvalProvider  # noqa: E402

DATASETS = ("tool_selection.yaml", "arguments.yaml", "workflow.yaml")


def load_cases() -> Dataset[dict[str, Any], dict[str, Any], dict[str, Any]]:
    cases = []
    for filename in DATASETS:
        dataset = Dataset[dict[str, Any], dict[str, Any], dict[str, Any]].from_file(
            Path(__file__).parent / "datasets" / filename
        )
        cases.extend(dataset.cases)
    if not 20 <= len(cases) <= 50 or len({case.name for case in cases}) != len(cases):
        raise ValueError("Evaluation requires 20–50 uniquely named cases")
    return Dataset(name="stockpilot_p0", cases=cases)


async def run_case(inputs: dict[str, Any], settings: Settings) -> dict[str, Any]:
    provider = EvalProvider()
    with TemporaryDirectory(prefix="stockpilot-eval-") as directory:
        engine = create_database_engine(f"sqlite:///{(Path(directory) / 'case.db').as_posix()}")
        try:
            init_db(engine)
            factory = create_session_factory(engine)
            watchlist = WatchlistService(factory)
            for symbol in inputs.get("watchlist", []):
                watchlist.add(symbol)
            traces = TraceService(factory)
            agent = StockAgentService(
                settings,
                AgentDependencies(StockService(provider), MarketService(provider), watchlist),
                ChatService(factory), traces,
            )
            try:
                session_id, answer = await agent.chat(inputs["prompt"])
                error_status = None
            except AgentExecutionError as error:
                session_id, answer, error_status = error.session_id, "", error.status_code
            steps = traces.for_session(session_id)
            return {
                "answer": answer,
                "error_status": error_status,
                "tools": [
                    {"name": step.tool_name, "args": step.tool_input, "status": step.status}
                    for step in steps
                ],
            }
        finally:
            engine.dispose()


def grade(expected: dict[str, Any], output: dict[str, Any]) -> dict[str, bool]:
    wanted = expected["tools"]
    actual = output["tools"]
    selection = Counter(tool["name"] for tool in wanted) == Counter(tool["name"] for tool in actual)
    arguments = selection and Counter(
        (tool["name"], json.dumps(tool["args"], sort_keys=True)) for tool in wanted
    ) == Counter(
        (tool["name"], json.dumps(tool["args"], sort_keys=True)) for tool in actual
    )
    answer = "".join(output["answer"].replace(",", "").split()).lower()
    grounded = all(
        "".join(str(token).split()).lower() in answer
        for token in expected["answer_contains"]
    )
    task = (
        arguments and grounded and output["error_status"] is None
        and all(tool["status"] == "success" for tool in actual)
        and "未能从行情 Tool 获取数据" not in output["answer"]
    )
    return {"tool_selection": selection, "argument_accuracy": arguments, "task_success": task}


async def evaluate(settings: Settings, *, limit: int | None = None) -> dict[str, Any]:
    dataset = load_cases()
    if limit is not None:
        dataset = Dataset(name=dataset.name, cases=dataset.cases[:limit])
    report = await dataset.evaluate(
        lambda inputs: run_case(inputs, settings), max_concurrency=1, progress=False
    )
    results = []
    for case in report.cases:
        scores = grade(case.metadata, case.output)
        results.append({
            "name": case.name, "scores": scores,
            "expected_tools": case.metadata["tools"], "observed_tools": case.output["tools"],
            "error_status": case.output["error_status"],
        })
    total = len(dataset.cases)
    metrics = {
        name: {"passed": sum(item["scores"][name] for item in results), "total": total}
        for name in ("tool_selection", "argument_accuracy", "task_success")
    }
    return {
        "model": settings.model_name, "cases": total, "metrics": metrics,
        "failed_cases": [item for item in results if not item["scores"]["task_success"]],
        "runner_failures": [failure.name for failure in report.failures],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, help="Run the first N cases for a smoke check")
    args = parser.parse_args()
    if args.limit is not None and args.limit < 1:
        parser.error("--limit must be positive")
    settings = Settings(_env_file=BACKEND / ".env")
    if not settings.model_name or not settings.model_api_key:
        print("SKIP: MODEL_NAME and MODEL_API_KEY must be configured in backend/.env")
        return 0
    result = asyncio.run(evaluate(settings, limit=args.limit))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if result["runner_failures"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
