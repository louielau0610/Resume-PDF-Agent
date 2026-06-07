"""CLI tests for M23 LLM review decision summaries."""

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


def _write_result(path: Path, candidate_ids: list[str] | None = None) -> None:
    ids = candidate_ids or ["c1", "c2"]
    result = LLMRewriteResult(
        status=LLMRewriteStatus.REWRITTEN,
        provider=LLMProviderType.MOCK,
        candidates=[
            LLMRewriteCandidate(
                candidate_id=cid,
                original_text=f"Original {cid}.",
                rewritten_text=f"Rewrite {cid}.",
                provider=LLMProviderType.MOCK,
                mode=LLMRewriteMode.CONSERVATIVE_POLISH,
                status=LLMRewriteStatus.REWRITTEN,
            )
            for cid in ids
        ],
        candidates_generated=len(ids),
        candidates_requiring_confirmation=len(ids),
        summary="Mock.",
    )
    path.write_text(result.model_dump_json(indent=2), encoding="utf-8")


def _write_decisions(path: Path, decisions: list[dict] | None = None) -> None:
    path.write_text(
        json.dumps(
            {
                "reviewer_name": "tester",
                "reviewed_at": "2026-06-08T00:00:00Z",
                "decisions": decisions
                or [
                    {"candidate_id": "c1", "decision": "approve_candidate"},
                    {"candidate_id": "c2", "decision": "ignore_for_now"},
                ],
            },
            indent=2,
        ),
        encoding="utf-8",
    )


def test_command_appears_in_help():
    runner = CliRunner()
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "summarize-llm-review-decisions" in result.output


def test_valid_decisions_generate_json_and_markdown(tmp_path: Path):
    runner = CliRunner()
    result_path = tmp_path / "llm_rewrite_result.json"
    decisions_path = tmp_path / "llm_rewrite_review_decisions.json"
    output_json = tmp_path / "summary.json"
    output_md = tmp_path / "summary.md"
    _write_result(result_path)
    _write_decisions(decisions_path)

    result = runner.invoke(
        app,
        [
            "summarize-llm-review-decisions",
            "--result", str(result_path),
            "--decisions", str(decisions_path),
            "--output-json", str(output_json),
            "--output-md", str(output_md),
        ],
    )

    assert result.exit_code == 0, result.output
    assert output_json.is_file()
    assert output_md.is_file()
    summary = json.loads(output_json.read_text(encoding="utf-8"))
    assert summary["approved_count"] == 1
    assert summary["ignored_count"] == 1


def test_missing_decision_file_fails_clearly(tmp_path: Path):
    runner = CliRunner()
    result = runner.invoke(
        app,
        ["summarize-llm-review-decisions", "--decisions", str(tmp_path / "missing.json")],
    )
    assert result.exit_code == 1
    assert "File not found" in result.output


def test_invalid_json_fails_clearly(tmp_path: Path):
    runner = CliRunner()
    decisions_path = tmp_path / "bad.json"
    decisions_path.write_text("not json", encoding="utf-8")
    result = runner.invoke(
        app,
        ["summarize-llm-review-decisions", "--decisions", str(decisions_path)],
    )
    assert result.exit_code == 1
    assert "Invalid JSON" in result.output


def test_result_cross_check_reports_unknown_candidate(tmp_path: Path):
    runner = CliRunner()
    result_path = tmp_path / "result.json"
    decisions_path = tmp_path / "decisions.json"
    output_json = tmp_path / "summary.json"
    _write_result(result_path, ["c1"])
    _write_decisions(decisions_path, [{"candidate_id": "unknown", "decision": "approve_candidate"}])
    result = runner.invoke(
        app,
        [
            "summarize-llm-review-decisions",
            "--result", str(result_path),
            "--decisions", str(decisions_path),
            "--output-json", str(output_json),
        ],
    )
    assert result.exit_code == 0
    summary = json.loads(output_json.read_text(encoding="utf-8"))
    assert summary["unknown_candidate_ids"] == ["unknown"]


def test_no_result_mode_warns_but_succeeds(tmp_path: Path):
    runner = CliRunner()
    decisions_path = tmp_path / "decisions.json"
    output_json = tmp_path / "summary.json"
    _write_decisions(decisions_path)
    result = runner.invoke(
        app,
        [
            "summarize-llm-review-decisions",
            "--decisions", str(decisions_path),
            "--output-json", str(output_json),
        ],
    )
    assert result.exit_code == 0
    summary = json.loads(output_json.read_text(encoding="utf-8"))
    assert summary["total_candidates"] == 0
    assert any("cross-checking was skipped" in w for w in summary["warnings"])
