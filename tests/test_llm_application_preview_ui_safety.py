"""Safety tests for M25 application preview UI."""

from __future__ import annotations

from pathlib import Path

from resume_pdf_agent.llm_application_preview_ui.renderer import (
    render_llm_application_preview_ui_page,
)
from resume_pdf_agent.llm_application_preview_ui.safety import (
    escape_llm_application_preview_text,
    safe_llm_application_preview_output_path,
    validate_llm_application_plan_for_preview,
)
from resume_pdf_agent.models.llm_application_plan import (
    LLMApplicationPlanStatus,
    LLMCandidateApplicationPlan,
    LLMCandidateApplicationPlanItem,
)


def _malicious_plan(value: str) -> LLMCandidateApplicationPlan:
    return LLMCandidateApplicationPlan(
        total_candidates=1,
        blocked_count=1,
        items=[
            LLMCandidateApplicationPlanItem(
                candidate_id=value,
                source_action="approve_candidate",
                plan_status=LLMApplicationPlanStatus.BLOCKED,
                original_text=value,
                candidate_text=value,
                application_instruction=value,
            )
        ],
        safety_notice=value,
        summary="Plan summary.",
    )


def test_escape_helper_escapes_html():
    assert escape_llm_application_preview_text("<script>alert(1)</script>") == "&lt;script&gt;alert(1)&lt;/script&gt;"


def test_safe_output_path_resolves(tmp_path: Path):
    assert safe_llm_application_preview_output_path(tmp_path / "preview.html").is_absolute()


def test_validate_empty_plan_warns():
    plan = LLMCandidateApplicationPlan(
        safety_notice="Plan only.",
        summary="Empty.",
    )
    issues = validate_llm_application_plan_for_preview(plan)
    assert any("no items" in issue.lower() for issue in issues)


def test_malicious_payloads_cannot_inject_active_script(tmp_path: Path):
    payloads = [
        '<script>alert("xss")</script>',
        '</textarea><script>alert("xss")</script>',
        '" onmouseover="alert(1)',
        '</script><script>alert("xss")</script>',
        "javascript:alert(1)",
    ]
    for index, payload in enumerate(payloads):
        result = render_llm_application_preview_ui_page(
            _malicious_plan(payload),
            tmp_path / f"preview_{index}.html",
        )
        html = result.html
        assert "<script>alert" not in html
        assert "</textarea><script" not in html
        assert '" onmouseover="alert(1)' not in html


def test_static_js_no_forbidden_primitives():
    js = (
        Path(__file__).resolve().parent.parent
        / "src"
        / "resume_pdf_agent"
        / "llm_application_preview_ui"
        / "static"
        / "llm_application_preview_page.js"
    ).read_text(encoding="utf-8").lower()
    for forbidden in [
        "fetch(",
        "xmlhttprequest",
        "sendbeacon",
        "websocket",
        "eventsource",
        "eval(",
        "new function",
        "function constructor",
        "import(",
        "http://",
        "https://",
    ]:
        assert forbidden not in js


def test_static_css_no_external_imports_or_urls():
    css = (
        Path(__file__).resolve().parent.parent
        / "src"
        / "resume_pdf_agent"
        / "llm_application_preview_ui"
        / "static"
        / "llm_application_preview_page.css"
    ).read_text(encoding="utf-8").lower()
    assert "@import" not in css
    assert "url(" not in css
    assert "http://" not in css
    assert "https://" not in css


def test_rendered_html_has_no_forbidden_ui_labels(tmp_path: Path):
    result = render_llm_application_preview_ui_page(
        _malicious_plan("safe text"),
        tmp_path / "preview.html",
    )
    html = result.html
    forbidden = [
        "Accept and apply",
        "Auto apply",
        "Update resume",
        "Patch resume",
        ">Submit<",
        ">Upload<",
        ">Send<",
    ]
    for label in forbidden:
        assert label not in html
    assert "<form" not in html.lower()
    assert "cdn." not in html.lower()
