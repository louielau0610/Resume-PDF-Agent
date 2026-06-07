"""Regression tests for M24 application planning."""

from __future__ import annotations

import json
from pathlib import Path

from resume_pdf_agent.llm_application_plan import plan_llm_candidate_application_to_files
from resume_pdf_agent.llm_review_decisions import summarize_llm_review_decisions_to_files
from resume_pdf_agent.llm_review_ui.renderer import _create_env, render_llm_review_ui_page
from resume_pdf_agent.models import ExportFormat
from resume_pdf_agent.models.llm import (
    LLMProviderType,
    LLMRewriteCandidate,
    LLMRewriteMode,
    LLMRewriteResult,
    LLMRewriteStatus,
)


def _result() -> LLMRewriteResult:
    return LLMRewriteResult(
        status=LLMRewriteStatus.REWRITTEN,
        provider=LLMProviderType.MOCK,
        candidates=[
            LLMRewriteCandidate(
                candidate_id="c1",
                source_experience_id="exp1",
                original_text="Original.",
                rewritten_text="Rewrite should not be applied.",
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


def test_m16_behavior_unchanged():
    candidate = LLMRewriteCandidate(
        candidate_id="c1",
        original_text="Original.",
        rewritten_text="Rewrite.",
        provider=LLMProviderType.MOCK,
        mode=LLMRewriteMode.CONSERVATIVE_POLISH,
        status=LLMRewriteStatus.REWRITTEN,
    )
    assert candidate.needs_confirmation is True


def test_m22_ui_still_renders(tmp_path: Path):
    rendered = render_llm_review_ui_page(_result(), tmp_path / "llm_review.html")
    assert rendered.output_path
    assert Path(rendered.output_path).is_file()


def test_m22_1_autoescape_remains_enabled():
    env = _create_env()
    assert env.from_string("{{ value }}").render(value="<script>") == "&lt;script&gt;"


def test_m23_summary_still_works(tmp_path: Path):
    result_path = tmp_path / "result.json"
    decisions_path = tmp_path / "decisions.json"
    result_path.write_text(_result().model_dump_json(indent=2), encoding="utf-8")
    decisions_path.write_text(
        json.dumps({"decisions": [{"candidate_id": "c1", "decision": "approve_candidate"}]}, indent=2),
        encoding="utf-8",
    )
    summary = summarize_llm_review_decisions_to_files(
        result_path=result_path,
        decisions_path=decisions_path,
        output_json_path=tmp_path / "summary.json",
    )
    assert summary.approved_count == 1


def test_application_plan_does_not_apply_candidates(tmp_path: Path):
    resume_html = tmp_path / "resume.html"
    resume_html.write_text("<html>Original.</html>", encoding="utf-8")
    before = resume_html.read_text(encoding="utf-8")
    result_path = tmp_path / "result.json"
    decisions_path = tmp_path / "decisions.json"
    result_path.write_text(_result().model_dump_json(indent=2), encoding="utf-8")
    decisions_path.write_text(
        json.dumps({"decisions": [{"candidate_id": "c1", "decision": "approve_candidate"}]}, indent=2),
        encoding="utf-8",
    )
    plan_llm_candidate_application_to_files(
        result_path=result_path,
        decisions_path=decisions_path,
        output_json_path=tmp_path / "plan.json",
        output_md_path=tmp_path / "plan.md",
    )
    assert resume_html.read_text(encoding="utf-8") == before
    plan_text = (tmp_path / "plan.json").read_text(encoding="utf-8")
    assert "applied_candidates" not in plan_text


def test_export_format_still_only_pdf():
    assert [x.value for x in ExportFormat] == ["pdf"]


def test_no_word_jpg_png_export():
    formats = [x.value for x in ExportFormat]
    assert "word" not in formats
    assert "jpg" not in formats
    assert "png" not in formats


def test_no_forbidden_framework_or_llm_sdk_dependency():
    text = (Path(__file__).resolve().parent.parent / "pyproject.toml").read_text(encoding="utf-8").lower()
    core = text.split("[project.optional-dependencies]")[0]
    for forbidden in ["fastapi", "flask", "streamlit", "react", "vite", "next.js", "vue", "svelte", "openai", "anthropic"]:
        assert forbidden not in core


def test_no_network_calls_in_application_plan_package():
    package_dir = Path(__file__).resolve().parent.parent / "src" / "resume_pdf_agent" / "llm_application_plan"
    text = "\n".join(p.read_text(encoding="utf-8").lower() for p in package_dir.glob("*.py"))
    for forbidden in ["fetch(", "xmlhttprequest", "sendbeacon", "websocket", "http://", "https://"]:
        assert forbidden not in text
