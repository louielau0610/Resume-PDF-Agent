"""CLI tests for M25 application preview UI."""

from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from resume_pdf_agent.cli import app
from resume_pdf_agent.models.llm_application_plan import (
    LLMApplicationPlanStatus,
    LLMCandidateApplicationPlan,
    LLMCandidateApplicationPlanItem,
)


def _write_plan(path: Path) -> None:
    plan = LLMCandidateApplicationPlan(
        total_candidates=1,
        planned_count=1,
        items=[
            LLMCandidateApplicationPlanItem(
                candidate_id="c1",
                source_action="approve_candidate",
                plan_status=LLMApplicationPlanStatus.PLANNED,
                target_section="experience",
                target_item_id="exp1",
                original_text="Original.",
                candidate_text="Rewrite.",
                needs_confirmation=False,
                application_instruction="Inspect manually.",
            )
        ],
        safety_notice="Plan only; no candidates were applied.",
        summary="Plan summary.",
    )
    path.write_text(plan.model_dump_json(indent=2), encoding="utf-8")


def test_command_appears_in_help():
    result = CliRunner().invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "render-llm-application-preview-ui" in result.output


def test_valid_plan_generates_html(tmp_path: Path):
    plan_path = tmp_path / "plan.json"
    output = tmp_path / "preview.html"
    _write_plan(plan_path)
    result = CliRunner().invoke(
        app,
        [
            "render-llm-application-preview-ui",
            "--plan", str(plan_path),
            "--output", str(output),
        ],
    )
    assert result.exit_code == 0, result.output
    assert output.is_file()
    assert "plan-only" in result.output
    assert "No candidates were applied" in result.output
    assert "Candidates:" in result.output


def test_missing_plan_file_fails_clearly(tmp_path: Path):
    result = CliRunner().invoke(
        app,
        [
            "render-llm-application-preview-ui",
            "--plan", str(tmp_path / "missing.json"),
            "--output", str(tmp_path / "preview.html"),
        ],
    )
    assert result.exit_code == 1
    assert "not found" in result.output.lower()


def test_invalid_json_fails_clearly(tmp_path: Path):
    bad = tmp_path / "bad.json"
    bad.write_text("not json", encoding="utf-8")
    result = CliRunner().invoke(
        app,
        [
            "render-llm-application-preview-ui",
            "--plan", str(bad),
            "--output", str(tmp_path / "preview.html"),
        ],
    )
    assert result.exit_code == 1
    assert "invalid json" in result.output.lower()


def test_invalid_plan_schema_fails_clearly(tmp_path: Path):
    bad = tmp_path / "bad_schema.json"
    bad.write_text(json.dumps({"plan_only": False}), encoding="utf-8")
    result = CliRunner().invoke(
        app,
        [
            "render-llm-application-preview-ui",
            "--plan", str(bad),
            "--output", str(tmp_path / "preview.html"),
        ],
    )
    assert result.exit_code == 1
    assert "invalid llm application plan" in result.output.lower()
