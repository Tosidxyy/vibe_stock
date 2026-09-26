"""Evaluation dataset and deterministic scoring checks."""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "evals"))

from run_eval import grade, load_cases, main  # noqa: E402


def test_dataset_has_unique_cases_and_required_workflows() -> None:
    cases = load_cases().cases
    assert len(cases) == 24
    assert len({case.name for case in cases}) == 24
    assert any(len(case.metadata["tools"]) > 1 for case in cases)
    assert any(case.inputs.get("watchlist") for case in cases)
    assert any(case.name.startswith("compare_") for case in cases)


def test_scoring_uses_actual_tool_arguments_and_grounded_answer() -> None:
    expected = {
        "tools": [{"name": "get_stock_quote", "args": {"symbol": "300750"}}],
        "answer_contains": ["251.3"],
    }
    output = {
        "tools": [{"name": "get_stock_quote", "args": {"symbol": "300750"}, "status": "success"}],
        "answer": "价格 251.30 元", "error_status": None,
    }
    assert all(grade(expected, output).values())
    wrong_args = {**output, "tools": [{**output["tools"][0], "args": {"symbol": "002594"}}]}
    assert grade(expected, wrong_args) == {
        "tool_selection": True, "argument_accuracy": False, "task_success": False,
    }
    wrong_answer = {**output, "answer": "价格 999 元"}
    assert grade(expected, wrong_answer)["task_success"] is False


def test_unconfigured_eval_skips_without_scores(monkeypatch, capsys) -> None:
    monkeypatch.setenv("MODEL_NAME", "")
    monkeypatch.setenv("MODEL_API_KEY", "")
    monkeypatch.setattr(sys, "argv", ["run_eval.py"])
    assert main() == 0
    output = capsys.readouterr().out
    assert output.startswith("SKIP:")
    assert '"metrics"' not in output
