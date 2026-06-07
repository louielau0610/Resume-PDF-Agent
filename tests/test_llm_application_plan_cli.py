"""CLI tests for M24 application planning."""

from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from resume_pdf_agent.cli import app
from resume_pdf_agent.models.llm import (
    LLMProviderType,
    LLMRewriteCandidate,
    LLMRewriteMode,
    LLMRewriteResult,
    LLMRewriteStatus,
)


def _write_result(path: Path) -> None:
    result = LLMRewriteResult(
        status=LLMRewriteStatus.REWRITTEN,
        provider=LLMProviderType.MOCK,
        candidates=[
            LLMRewriteCandidate(
                candidate_id="c1",
                source_experience_id="exp1",
                original_text="Original.",
                rewritten_text="Rewrite.",
                provider=LLMProviderType.MOCK,
                mode=LLMRewriteMode.CONSERVATIVE_POLISH,
                status=LLMRewriteStatus.REWRITTEN,
                needs_confirmation=False,
            )
        ],
        candidates_generated=1,
        candidates_requiring_confirmation=0,
        summary="Mock.",
    )
    path.write_text(result.model_dump_json(indent=2), encoding="utf-8")


def _write_decisions(path: Path) -> None:
    path.write_text(
        json.dumps({"decisions": [{"candidate_id": "c1", "decision": "approve_candidate"}]}, indent=2),
        encoding="utf-8",
    )


def test_command_appears_in_help():
    result = CliRunner().invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "plan-llm-candidate-application" in result.output


def test_valid_inputs_generate_json_and_markdown(tmp_path: Path):
    result_path = tmp_path / "result.json"
    decisions_path = tmp_path / "decisions.json"
    output_json = tmp_path / "plan.json"
    output_md = tmp_path / "plan.md"
    _write_result(result_path)
    _write_decisions(decisions_path)
    result = CliRunner().invoke(
        app,
        [
            "plan-llm-candidate-application",
            "--result", str(result_path),
            "--decisions", str(decisions_path),
            "--output-json", str(output_json),
            "--output-md", str(output_md),
        ],
    )
    assert result.exit_code == 0, result.output
    assert "plan-only" in result.output
    assert "No candidates were applied" in result.output
    assert output_json.is_file()
    assert output_md.is_file()
    assert json.loads(output_json.read_text(encoding="utf-8"))["plan_only"] is True


def test_missing_result_file_fails_clearly(tmp_path: Path):
    decisions_path = tmp_path / "decisions.json"
    _write_decisions(decisions_path)
    result = CliRunner().invoke(
        app,
        [
            "plan-llm-candidate-application",
            "--result", str(tmp_path / "missing.json"),
            "--decisions", str(decisions_path),
        ],
    )
    assert result.exit_code == 1
    assert "File not found" in result.output


def test_missing_decisions_file_fails_clearly(tmp_path: Path):
    result_path = tmp_path / "result.json"
    _write_result(result_path)
    result = CliRunner().invoke(
        app,
        [
            "plan-llm-candidate-application",
            "--result", str(result_path),
            "--decisions", str(tmp_path / "missing.json"),
        ],
    )
    assert result.exit_code == 1
    assert "File not found" in result.output


def test_no_summary_mode_works_with_warning(tmp_path: Path):
    result_path = tmp_path / "result.json"
    decisions_path = tmp_path / "decisions.json"
    output_json = tmp_path / "plan.json"
    _write_result(result_path)
    _write_decisions(decisions_path)
    result = CliRunner().invoke(
        app,
        [
            "plan-llm-candidate-application",
            "--result", str(result_path),
            "--decisions", str(decisions_path),
            "--output-json", str(output_json),
        ],
    )
    assert result.exit_code == 0
    plan = json.loads(output_json.read_text(encoding="utf-8"))
    assert any("No M23 decision summary" in w for w in plan["warnings"])
