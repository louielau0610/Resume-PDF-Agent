"""Tests for M21 JD upload UI context builder."""

from __future__ import annotations

from resume_pdf_agent.jd_ui.context import build_jd_upload_ui_context
from resume_pdf_agent.models.jd_ui import JDUploadUIOptions


def test_build_jd_upload_ui_context_importable():
    """build_jd_upload_ui_context is importable and callable."""
    assert callable(build_jd_upload_ui_context)


def test_context_returns_dict_with_required_keys():
    """Context returns a dict with all expected top-level keys."""
    ctx = build_jd_upload_ui_context()
    assert isinstance(ctx, dict)
    assert "page_title" in ctx
    assert "safety_notice" in ctx
    assert "compliance_markers" in ctx
    assert "cli_instructions" in ctx
    assert "options" in ctx


def test_context_page_title():
    """Context page_title is a non-empty string."""
    ctx = build_jd_upload_ui_context()
    assert isinstance(ctx["page_title"], str)
    assert len(ctx["page_title"]) > 0


def test_context_safety_notice_mentions_backend_m15():
    """Safety notice states backend M15 compliance check is authoritative."""
    ctx = build_jd_upload_ui_context()
    notice = ctx["safety_notice"].lower()
    assert "m15" in notice or "backend" in notice
    assert "compliance" in notice


def test_context_safety_notice_mentions_local_hints_only():
    """Safety notice mentions local hints are not authoritative."""
    ctx = build_jd_upload_ui_context()
    notice = ctx["safety_notice"].lower()
    assert "local" in notice or "only" in notice


def test_context_compliance_markers_is_non_empty_list():
    """compliance_markers is a non-empty list of dicts with required keys."""
    ctx = build_jd_upload_ui_context()
    markers = ctx["compliance_markers"]
    assert isinstance(markers, list)
    assert len(markers) > 0
    for m in markers:
        assert isinstance(m, dict)
        assert "marker" in m
        assert "severity" in m
        assert "explanation" in m
        assert "suggested_action" in m


def test_context_includes_risk_marker_confidential():
    """Context includes 'confidential' risk marker."""
    ctx = build_jd_upload_ui_context()
    marker_texts = [m["marker"] for m in ctx["compliance_markers"]]
    assert "confidential" in marker_texts


def test_context_includes_risk_marker_internal_use_only():
    """Context includes 'internal use only' risk marker."""
    ctx = build_jd_upload_ui_context()
    marker_texts = [m["marker"] for m in ctx["compliance_markers"]]
    assert "internal use only" in marker_texts


def test_context_includes_risk_marker_do_not_distribute():
    """Context includes 'do not distribute' risk marker."""
    ctx = build_jd_upload_ui_context()
    marker_texts = [m["marker"] for m in ctx["compliance_markers"]]
    assert "do not distribute" in marker_texts


def test_context_includes_risk_marker_interview_scorecard():
    """Context includes 'interview scorecard' risk marker."""
    ctx = build_jd_upload_ui_context()
    marker_texts = [m["marker"] for m in ctx["compliance_markers"]]
    assert "interview scorecard" in marker_texts


def test_context_includes_risk_marker_candidate_evaluation_form():
    """Context includes 'candidate evaluation form' risk marker."""
    ctx = build_jd_upload_ui_context()
    marker_texts = [m["marker"] for m in ctx["compliance_markers"]]
    assert "candidate evaluation form" in marker_texts


def test_context_includes_risk_marker_scoring_rubric():
    """Context includes 'scoring rubric' risk marker."""
    ctx = build_jd_upload_ui_context()
    marker_texts = [m["marker"] for m in ctx["compliance_markers"]]
    assert "scoring rubric" in marker_texts


def test_context_includes_risk_marker_leaked():
    """Context includes 'leaked' risk marker."""
    ctx = build_jd_upload_ui_context()
    marker_texts = [m["marker"] for m in ctx["compliance_markers"]]
    assert "leaked" in marker_texts


def test_context_includes_risk_marker_not_for_public_release():
    """Context includes 'not for public release' risk marker."""
    ctx = build_jd_upload_ui_context()
    marker_texts = [m["marker"] for m in ctx["compliance_markers"]]
    assert "not for public release" in marker_texts


def test_context_cli_instructions_is_non_empty_list():
    """cli_instructions is a non-empty list of strings."""
    ctx = build_jd_upload_ui_context()
    insts = ctx["cli_instructions"]
    assert isinstance(insts, list)
    assert len(insts) > 0
    for inst in insts:
        assert isinstance(inst, str)
        assert len(inst) > 0


def test_context_options_has_default_keys():
    """options dict has all expected boolean and language keys."""
    ctx = build_jd_upload_ui_context()
    opts = ctx["options"]
    assert "include_copy_buttons" in opts
    assert "include_download_buttons" in opts
    assert "include_compliance_hints" in opts
    assert "include_workflow_json_generator" in opts
    assert "include_cli_instructions" in opts
    assert "language" in opts


def test_context_default_language_is_zh():
    """Default options language is 'zh'."""
    ctx = build_jd_upload_ui_context()
    assert ctx["options"]["language"] == "zh"


def test_context_accepts_custom_options():
    """Context builder accepts and uses custom JDUploadUIOptions."""
    opts = JDUploadUIOptions(
        include_copy_buttons=False,
        include_download_buttons=False,
        include_compliance_hints=False,
        include_workflow_json_generator=False,
        include_cli_instructions=False,
        language="en",
    )
    ctx = build_jd_upload_ui_context(opts)
    assert ctx["options"]["include_copy_buttons"] is False
    assert ctx["options"]["include_download_buttons"] is False
    assert ctx["options"]["include_compliance_hints"] is False
    assert ctx["options"]["language"] == "en"


def test_context_accepts_none_options():
    """Context builder works with None options (uses defaults)."""
    ctx = build_jd_upload_ui_context(None)
    assert ctx["options"]["include_copy_buttons"] is True
    assert ctx["options"]["language"] == "zh"


def test_context_does_not_contain_hiring_probability():
    """Context does not claim hiring probability prediction."""
    ctx = build_jd_upload_ui_context()
    # Flatten all string values
    all_text = _flatten_context_text(ctx).lower()
    assert "hiring probability" not in all_text
    assert "offer probability" not in all_text
    assert "interview probability" not in all_text


def test_context_does_not_claim_internal_screening():
    """Context does not claim internal screening access."""
    ctx = build_jd_upload_ui_context()
    all_text = _flatten_context_text(ctx).lower()
    assert "internal screening" not in all_text


def _flatten_context_text(ctx: dict) -> str:
    """Flatten all string values in context dict for assertions."""
    parts: list[str] = []
    for v in ctx.values():
        if isinstance(v, str):
            parts.append(v)
        elif isinstance(v, list):
            for item in v:
                if isinstance(item, str):
                    parts.append(item)
                elif isinstance(item, dict):
                    for sv in item.values():
                        if isinstance(sv, str):
                            parts.append(sv)
        elif isinstance(v, dict):
            for sv in v.values():
                if isinstance(sv, (str, bool)):
                    parts.append(str(sv))
    return " ".join(parts)
