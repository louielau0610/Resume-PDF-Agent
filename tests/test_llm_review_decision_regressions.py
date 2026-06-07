"""Regression tests for M23 LLM review decision summaries."""

from __future__ import annotations

import json
from pathlib import Path

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
from resume_pdf_agent.models.workflow import ResumeWorkflowInput
from resume_pdf_agent.sample_data import SAMPLE_RESUME_CONTENT, SAMPLE_USER_PROFILE
from resume_pdf_agent.workflow import run_resume_workflow


def _llm_result() -> LLMRewriteResult:
    return LLMRewriteResult(
        status=LLMRewriteStatus.REWRITTEN,
        provider=LLMProviderType.MOCK,
        candidates=[
            LLMRewriteCandidate(
                candidate_id="c1",
                original_text="Used Python.",
                rewritten_text="APPROVED TEXT SHOULD NOT APPEAR IN RESUME.",
                provider=LLMProviderType.MOCK,
                mode=LLMRewriteMode.CONSERVATIVE_POLISH,
                status=LLMRewriteStatus.REWRITTEN,
            )
        ],
        candidates_generated=1,
        candidates_requiring_confirmation=1,
        summary="Mock.",
    )


def test_default_workflow_remains_unchanged(tmp_path: Path):
    workflow_input = ResumeWorkflowInput(
        user_profile=SAMPLE_USER_PROFILE,
        resume_content=SAMPLE_RESUME_CONTENT,
        output_dir=str(tmp_path / "default"),
    )
    result = run_resume_workflow(workflow_input)
    assert result.status.value in ("completed", "completed_with_warnings")
    assert result.llm_review_decision_summary_json_path is None
    assert result.llm_review_decision_summary_md_path is None


def test_m16_model_behavior_unchanged():
    candidate = LLMRewriteCandidate(
        candidate_id="c1",
        original_text="Original.",
        rewritten_text="Rewritten.",
        provider=LLMProviderType.MOCK,
        mode=LLMRewriteMode.CONSERVATIVE_POLISH,
        status=LLMRewriteStatus.REWRITTEN,
    )
    assert candidate.needs_confirmation is True


def test_m22_ui_still_renders(tmp_path: Path):
    rendered = render_llm_review_ui_page(_llm_result(), tmp_path / "llm_review.html")
    assert rendered.output_path
    assert Path(rendered.output_path).is_file()


def test_m22_1_autoescape_remains_enabled():
    env = _create_env()
    template = env.from_string("{{ value }}")
    assert template.render(value="<script>alert(1)</script>") == "&lt;script&gt;alert(1)&lt;/script&gt;"


def test_candidate_decisions_are_not_applied_to_final_resume(tmp_path: Path):
    workflow_input = ResumeWorkflowInput(
        user_profile=SAMPLE_USER_PROFILE,
        resume_content=SAMPLE_RESUME_CONTENT,
        output_dir=str(tmp_path / "workflow"),
    )
    workflow_result = run_resume_workflow(workflow_input)
    html_path = Path(workflow_result.html_output_path or "")
    before = html_path.read_text(encoding="utf-8")

    result_path = tmp_path / "llm_rewrite_result.json"
    decisions_path = tmp_path / "llm_rewrite_review_decisions.json"
    result_path.write_text(_llm_result().model_dump_json(indent=2), encoding="utf-8")
    decisions_path.write_text(
        json.dumps(
            {"decisions": [{"candidate_id": "c1", "decision": "approve_candidate"}]},
            indent=2,
        ),
        encoding="utf-8",
    )
    summarize_llm_review_decisions_to_files(
        decisions_path=decisions_path,
        result_path=result_path,
        output_json_path=tmp_path / "summary.json",
        output_md_path=tmp_path / "summary.md",
    )
    after = html_path.read_text(encoding="utf-8")
    assert before == after
    assert "APPROVED TEXT SHOULD NOT APPEAR IN RESUME" not in after
    assert not hasattr(workflow_result, "applied_candidates")


def test_export_format_still_only_pdf():
    assert [x.value for x in ExportFormat] == ["pdf"]


def test_no_word_jpg_png_export_formats():
    formats = [x.value for x in ExportFormat]
    assert "word" not in formats
    assert "jpg" not in formats
    assert "png" not in formats


def test_no_new_framework_or_llm_sdk_dependencies():
    pyproject = Path(__file__).resolve().parent.parent / "pyproject.toml"
    content = pyproject.read_text(encoding="utf-8").lower()
    for forbidden in [
        "react",
        "vite",
        "next.js",
        "vue",
        "svelte",
        "streamlit",
        "flask",
        "openai",
        "anthropic",
    ]:
        assert forbidden not in content


def test_no_network_calls_in_new_package():
    package_dir = Path(__file__).resolve().parent.parent / "src" / "resume_pdf_agent" / "llm_review_decisions"
    text = "\n".join(p.read_text(encoding="utf-8").lower() for p in package_dir.glob("*.py"))
    for forbidden in ["fetch(", "xmlhttprequest", "sendbeacon", "websocket", "http://", "https://"]:
        assert forbidden not in text
