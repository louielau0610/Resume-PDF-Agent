"""CLI tests for M22 LLM review UI render-llm-review-ui command."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from resume_pdf_agent.cli import app
from resume_pdf_agent.models.llm import (
    LLMProviderType,
    LLMRewriteCandidate,
    LLMRewriteMode,
    LLMRewriteResult,
    LLMRewriteStatus,
)


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


def _write_mock_result(path: Path) -> None:
    result = LLMRewriteResult(
        status=LLMRewriteStatus.REWRITTEN,
        provider=LLMProviderType.MOCK,
        candidates=[
            LLMRewriteCandidate(
                candidate_id="c1",
                original_text="Original bullet.",
                rewritten_text="Rewritten bullet.",
                provider=LLMProviderType.MOCK,
                mode=LLMRewriteMode.CONSERVATIVE_POLISH,
                status=LLMRewriteStatus.REWRITTEN,
            ),
        ],
        candidates_generated=1,
        candidates_requiring_confirmation=0,
        summary="Mock.",
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(result.model_dump_json(indent=2), encoding="utf-8")


# ---------------------------------------------------------------------------
# render-llm-review-ui command
# ---------------------------------------------------------------------------

def test_render_llm_review_ui_command_exists():
    """render-llm-review-ui command is registered."""
    commands = [cmd.name for cmd in app.registered_commands]
    assert "render-llm-review-ui" in commands


def test_render_llm_review_ui_exits_successfully(runner: CliRunner, tmp_path: Path):
    """render-llm-review-ui exits with code 0."""
    result_path = tmp_path / "llm_rewrite_result.json"
    _write_mock_result(result_path)
    output_path = tmp_path / "llm_review.html"

    result = runner.invoke(app, [
        "render-llm-review-ui",
        "--result", str(result_path),
        "--output", str(output_path),
    ])
    assert result.exit_code == 0, f"CLI failed: {result.output}"
    assert output_path.is_file()
    assert output_path.stat().st_size > 0


def test_render_llm_review_ui_output_contains_candidate_text(runner: CliRunner, tmp_path: Path):
    """Output contains candidate text."""
    result_path = tmp_path / "llm_rewrite_result.json"
    _write_mock_result(result_path)
    output_path = tmp_path / "llm_review.html"

    runner.invoke(app, [
        "render-llm-review-ui",
        "--result", str(result_path),
        "--output", str(output_path),
    ])
    html = output_path.read_text(encoding="utf-8")
    assert "Original bullet." in html
    assert "Rewritten bullet." in html


def test_render_llm_review_ui_output_contains_safety_notice(runner: CliRunner, tmp_path: Path):
    """Output contains safety notice."""
    result_path = tmp_path / "llm_rewrite_result.json"
    _write_mock_result(result_path)
    output_path = tmp_path / "llm_review.html"

    runner.invoke(app, [
        "render-llm-review-ui",
        "--result", str(result_path),
        "--output", str(output_path),
    ])
    html = output_path.read_text(encoding="utf-8").lower()
    assert "suggestions" in html


def test_render_llm_review_ui_missing_result_file(runner: CliRunner, tmp_path: Path):
    """render-llm-review-ui fails gracefully with missing result file."""
    result = runner.invoke(app, [
        "render-llm-review-ui",
        "--result", str(tmp_path / "nonexistent.json"),
        "--output", str(tmp_path / "review.html"),
    ])
    assert result.exit_code == 1


def test_render_llm_review_ui_invalid_json(runner: CliRunner, tmp_path: Path):
    """render-llm-review-ui fails gracefully with invalid JSON."""
    bad_path = tmp_path / "bad.json"
    bad_path.write_text("not json", encoding="utf-8")
    result = runner.invoke(app, [
        "render-llm-review-ui",
        "--result", str(bad_path),
        "--output", str(tmp_path / "review.html"),
    ])
    assert result.exit_code == 1


# ---------------------------------------------------------------------------
# existing commands
# ---------------------------------------------------------------------------

def test_existing_commands_still_present():
    """All existing CLI commands are still registered."""
    commands = {cmd.name for cmd in app.registered_commands}
    expected = {
        "run-sample", "run", "list-criteria", "list-templates",
        "render-page", "render-confirmation-ui", "render-jd-upload-ui",
        "render-llm-review-ui", "check-pdf-backend",
    }
    missing = expected - commands
    assert not missing, f"Missing commands: {missing}"
