"""Tests for M24 application plan IO."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from resume_pdf_agent.llm_application_plan.io import plan_llm_candidate_application_to_files
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


def test_writes_json_and_markdown_creating_parent_dirs(tmp_path: Path):
    result_path = tmp_path / "result.json"
    decisions_path = tmp_path / "decisions.json"
    output_json = tmp_path / "deep" / "plan.json"
    output_md = tmp_path / "deep" / "plan.md"
    _write_result(result_path)
    _write_decisions(decisions_path)

    plan = plan_llm_candidate_application_to_files(
        result_path=result_path,
        decisions_path=decisions_path,
        output_json_path=output_json,
        output_md_path=output_md,
    )

    assert plan.plan_only is True
    assert output_json.is_file()
    assert output_md.is_file()
    assert json.loads(output_json.read_text(encoding="utf-8"))["plan_only"] is True


def test_missing_result_file_fails_clearly(tmp_path: Path):
    decisions_path = tmp_path / "decisions.json"
    _write_decisions(decisions_path)
    with pytest.raises(FileNotFoundError):
        plan_llm_candidate_application_to_files(
            result_path=tmp_path / "missing.json",
            decisions_path=decisions_path,
        )


def test_missing_decisions_file_fails_clearly(tmp_path: Path):
    result_path = tmp_path / "result.json"
    _write_result(result_path)
    with pytest.raises(FileNotFoundError):
        plan_llm_candidate_application_to_files(
            result_path=result_path,
            decisions_path=tmp_path / "missing.json",
        )
