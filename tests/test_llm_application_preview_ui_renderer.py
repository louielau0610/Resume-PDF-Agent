"""Renderer tests for M25 application preview UI."""

from __future__ import annotations

import json
from pathlib import Path

from resume_pdf_agent.llm_application_preview_ui.renderer import (
    _create_env,
    render_llm_application_preview_ui_from_plan_file,
    render_llm_application_preview_ui_page,
)
from resume_pdf_agent.models.llm_application_plan import (
    LLMApplicationBlockReason,
    LLMApplicationPlanStatus,
    LLMCandidateApplicationPlan,
    LLMCandidateApplicationPlanItem,
)
from resume_pdf_agent.models.llm_application_preview_ui import (
    LLMApplicationPreviewUIStatus,
)


def _plan(malicious: bool = False) -> LLMCandidateApplicationPlan:
    original = "<script>alert(\"xss\")</script>" if malicious else "Original text."
    candidate = (
        "</textarea><script>alert(\"xss\")</script>"
        if malicious
        else "Candidate text."
    )
    item = LLMCandidateApplicationPlanItem(
        candidate_id='" onmouseover="alert(1)' if malicious else "c1",
        source_action="approve_candidate",
        plan_status=LLMApplicationPlanStatus.BLOCKED,
        target_section="experience",
        target_item_id="exp1",
        original_text=original,
        candidate_text=candidate,
        provider="mock",
        needs_confirmation=True,
        validation_warnings=["javascript:alert(1)"],
        block_reasons=[LLMApplicationBlockReason.NEEDS_CONFIRMATION],
        manual_review_notes=["manual note"],
        decision_note="decision note",
        application_instruction="Inspect manually.",
    )
    return LLMCandidateApplicationPlan(
        total_candidates=1,
        total_decisions=1,
        blocked_count=1,
        items=[item],
        warnings=["plan warning"],
        safety_notice="Plan only; no candidates were applied.",
        source_files={"llm_rewrite_application_plan": "plan.json"},
        summary="Plan summary.",
    )


def test_renderer_jinja_env_autoescape_enabled():
    env = _create_env()
    template = env.from_string("{{ value }}")
    assert template.render(value="<script>alert(1)</script>") == "&lt;script&gt;alert(1)&lt;/script&gt;"


def test_render_creates_html_with_counts_and_text(tmp_path: Path):
    result = render_llm_application_preview_ui_page(_plan(), tmp_path / "preview.html")
    assert result.status == LLMApplicationPreviewUIStatus.RENDERED
    assert Path(result.output_path or "").is_file()
    assert "Candidate Application Preview" in result.html
    assert "Original text." in result.html
    assert "Candidate text." in result.html
    assert "needs_confirmation" in result.html
    assert "plan warning" in result.html
    assert result.blocked_count == 1


def test_render_creates_parent_output_dir(tmp_path: Path):
    output = tmp_path / "nested" / "preview.html"
    result = render_llm_application_preview_ui_page(_plan(), output)
    assert result.status == LLMApplicationPreviewUIStatus.RENDERED
    assert output.is_file()


def test_render_from_missing_plan_file_fails(tmp_path: Path):
    result = render_llm_application_preview_ui_from_plan_file(
        tmp_path / "missing.json",
        tmp_path / "preview.html",
    )
    assert result.status == LLMApplicationPreviewUIStatus.FAILED
    assert "not found" in result.errors[0].lower()


def test_render_from_invalid_json_fails(tmp_path: Path):
    plan_path = tmp_path / "bad.json"
    plan_path.write_text("{not-json", encoding="utf-8")
    result = render_llm_application_preview_ui_from_plan_file(plan_path, tmp_path / "preview.html")
    assert result.status == LLMApplicationPreviewUIStatus.FAILED
    assert "invalid json" in result.errors[0].lower()


def test_render_from_plan_file(tmp_path: Path):
    plan_path = tmp_path / "plan.json"
    plan_path.write_text(_plan().model_dump_json(indent=2), encoding="utf-8")
    output = tmp_path / "preview.html"
    result = render_llm_application_preview_ui_from_plan_file(plan_path, output)
    assert result.status == LLMApplicationPreviewUIStatus.RENDERED
    assert output.is_file()


def test_malicious_candidate_text_is_escaped(tmp_path: Path):
    result = render_llm_application_preview_ui_page(_plan(malicious=True), tmp_path / "preview.html")
    html = result.html
    assert "<script>alert" not in html
    assert "</textarea><script" not in html
    assert '" onmouseover="alert(1)' not in html
    assert "&lt;script&gt;alert" in html
    assert "\\u003c/textarea\\u003e\\u003cscript\\u003ealert" in html


def test_rendered_html_has_no_mutation_fields(tmp_path: Path):
    result = render_llm_application_preview_ui_page(_plan(), tmp_path / "preview.html")
    html = result.html.lower()
    assert "applied_candidates" not in html
    assert "update_resume" not in html
    assert "patch_resume" not in html
    assert "apply_to_resume" not in html
