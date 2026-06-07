"""Tests for M22 LLM review UI renderer."""

from __future__ import annotations

import json
from pathlib import Path

from resume_pdf_agent.llm_review_ui.renderer import (
    render_llm_review_ui_from_result_file,
    render_llm_review_ui_page,
)
from resume_pdf_agent.models.llm import (
    LLMProviderType,
    LLMRewriteCandidate,
    LLMRewriteMode,
    LLMRewriteResult,
    LLMRewriteStatus,
)
from resume_pdf_agent.models.llm_review_ui import LLMReviewUIStatus


def _make_mock_result() -> LLMRewriteResult:
    candidates = [
        LLMRewriteCandidate(
            candidate_id="c1",
            source_experience_id="exp1",
            original_text="Built data pipelines.",
            rewritten_text="Designed and implemented scalable data pipelines.",
            provider=LLMProviderType.MOCK,
            mode=LLMRewriteMode.CONSERVATIVE_POLISH,
            status=LLMRewriteStatus.REWRITTEN,
            needs_confirmation=True,
            validation_warnings=["Missing metric"],
        ),
        LLMRewriteCandidate(
            candidate_id="c2",
            original_text="Used Python.",
            rewritten_text="Leveraged Python for analysis.",
            provider=LLMProviderType.MOCK,
            mode=LLMRewriteMode.CONSERVATIVE_POLISH,
            status=LLMRewriteStatus.REWRITTEN,
            needs_confirmation=False,
        ),
    ]
    return LLMRewriteResult(
        status=LLMRewriteStatus.REWRITTEN_WITH_WARNINGS,
        provider=LLMProviderType.MOCK,
        candidates=candidates,
        candidates_generated=2,
        candidates_requiring_confirmation=1,
        summary="Mock rewrite result.",
    )


# ---------------------------------------------------------------------------
# render_llm_review_ui_page
# ---------------------------------------------------------------------------

def test_render_llm_review_ui_page_importable():
    """render_llm_review_ui_page is importable and callable."""
    assert callable(render_llm_review_ui_page)


def test_render_creates_html_file(tmp_path: Path):
    """Renderer creates a non-empty llm_review.html file."""
    result = _make_mock_result()
    output_path = tmp_path / "llm_review.html"
    r = render_llm_review_ui_page(result, output_path)
    assert r.status == LLMReviewUIStatus.RENDERED
    assert r.output_path is not None
    assert Path(r.output_path).is_file()
    assert Path(r.output_path).stat().st_size > 0
    assert len(r.html) > 0


def test_render_creates_output_dir(tmp_path: Path):
    """Renderer creates parent directories if they don't exist."""
    result = _make_mock_result()
    output_path = tmp_path / "deeply" / "nested" / "llm_review.html"
    r = render_llm_review_ui_page(result, output_path)
    assert r.status == LLMReviewUIStatus.RENDERED


def test_html_contains_original_and_rewritten_text(tmp_path: Path):
    """Rendered HTML contains both original and rewritten text."""
    result = _make_mock_result()
    r = render_llm_review_ui_page(result, tmp_path / "review.html")
    html = r.html
    assert "Built data pipelines." in html
    assert "Designed and implemented scalable data pipelines." in html


def test_html_contains_candidate_ids(tmp_path: Path):
    """Rendered HTML contains candidate IDs."""
    result = _make_mock_result()
    r = render_llm_review_ui_page(result, tmp_path / "review.html")
    html = r.html
    assert "c1" in html
    assert "c2" in html


def test_html_contains_provider_info(tmp_path: Path):
    """Rendered HTML contains provider information."""
    result = _make_mock_result()
    r = render_llm_review_ui_page(result, tmp_path / "review.html")
    html = r.html.lower()
    assert "mock" in html


def test_html_contains_needs_confirmation_badge(tmp_path: Path):
    """Rendered HTML contains needs confirmation indication."""
    result = _make_mock_result()
    r = render_llm_review_ui_page(result, tmp_path / "review.html")
    html = r.html
    assert "Needs Confirmation" in html


def test_html_contains_decision_controls(tmp_path: Path):
    """Rendered HTML contains decision radio controls."""
    result = _make_mock_result()
    r = render_llm_review_ui_page(result, tmp_path / "review.html")
    html = r.html
    assert "approve_candidate" in html
    assert "reject_candidate" in html


def test_html_contains_json_preview_area(tmp_path: Path):
    """Rendered HTML contains a JSON preview textarea."""
    result = _make_mock_result()
    r = render_llm_review_ui_page(result, tmp_path / "review.html")
    html = r.html
    assert 'id="decisions-output"' in html


def test_html_contains_copy_download_controls(tmp_path: Path):
    """Rendered HTML contains copy and download buttons."""
    result = _make_mock_result()
    r = render_llm_review_ui_page(result, tmp_path / "review.html")
    html = r.html
    assert "copyDecisionsJSON" in html or "Copy to Clipboard" in html
    assert "downloadDecisionsJSON" in html or "Download" in html


def test_html_contains_cli_instructions(tmp_path: Path):
    """Rendered HTML contains CLI instruction section."""
    result = _make_mock_result()
    r = render_llm_review_ui_page(result, tmp_path / "review.html")
    html = r.html
    assert "CLI Instructions" in html or "命令行说明" in html


def test_html_contains_safety_notice(tmp_path: Path):
    """Rendered HTML contains all required safety notice phrases."""
    result = _make_mock_result()
    r = render_llm_review_ui_page(result, tmp_path / "review.html")
    html = r.html.lower()
    assert "suggestions" in html
    assert "personally verify" in html
    assert "automatically" in html
    assert "m14" in html or "confirmation" in html


def test_html_no_truth_verification_claim(tmp_path: Path):
    """Rendered HTML does not positively claim to verify truth."""
    result = _make_mock_result()
    r = render_llm_review_ui_page(result, tmp_path / "review.html")
    html = r.html.lower()
    # Footer says "does not verify truth" - disclaimer, not claim
    assert "verifies truth" not in html
    # Must include the disclaimer
    assert "does not verify" in html


def test_html_no_hiring_probability(tmp_path: Path):
    """Rendered HTML does not positively claim hiring probability."""
    result = _make_mock_result()
    r = render_llm_review_ui_page(result, tmp_path / "review.html")
    html = r.html.lower()
    assert "offer probability" not in html
    assert "interview probability" not in html


def test_html_no_internal_screening(tmp_path: Path):
    """Rendered HTML does not positively claim internal screening access."""
    result = _make_mock_result()
    r = render_llm_review_ui_page(result, tmp_path / "review.html")
    html = r.html.lower()
    assert "internal screening access" not in html
    assert "company screening" not in html


def test_html_no_external_cdn(tmp_path: Path):
    """Rendered HTML has no external CDN links."""
    result = _make_mock_result()
    r = render_llm_review_ui_page(result, tmp_path / "review.html")
    html = r.html.lower()
    assert "cdn." not in html
    assert "unpkg.com" not in html


def test_html_no_external_fonts(tmp_path: Path):
    """Rendered HTML has no external font imports."""
    result = _make_mock_result()
    r = render_llm_review_ui_page(result, tmp_path / "review.html")
    html = r.html.lower()
    assert "fonts.googleapis.com" not in html
    assert "@import url(http" not in html


def test_html_no_react_vite_next(tmp_path: Path):
    """Rendered HTML has no React/Vite/Next markers."""
    result = _make_mock_result()
    r = render_llm_review_ui_page(result, tmp_path / "review.html")
    html = r.html.lower()
    assert "react-dom" not in html
    assert "__vite" not in html
    assert "__next" not in html


def test_html_no_form_action(tmp_path: Path):
    """Rendered HTML has no form action to server."""
    result = _make_mock_result()
    r = render_llm_review_ui_page(result, tmp_path / "review.html")
    html = r.html.lower()
    assert '<form' not in html
    assert 'action="http' not in html


# ---------------------------------------------------------------------------
# render_llm_review_ui_from_result_file
# ---------------------------------------------------------------------------

def test_render_from_result_file_importable():
    """render_llm_review_ui_from_result_file is importable."""
    assert callable(render_llm_review_ui_from_result_file)


def test_render_from_result_file_creates_html(tmp_path: Path):
    """render_llm_review_ui_from_result_file reads JSON and creates HTML."""
    result = _make_mock_result()
    result_path = tmp_path / "llm_rewrite_result.json"
    result_path.write_text(result.model_dump_json(indent=2), encoding="utf-8")

    output_path = tmp_path / "llm_review.html"
    r = render_llm_review_ui_from_result_file(result_path, output_path)
    assert r.status == LLMReviewUIStatus.RENDERED
    assert output_path.is_file()


def test_render_from_missing_file_returns_failed(tmp_path: Path):
    """render_llm_review_ui_from_result_file returns FAILED for missing file."""
    r = render_llm_review_ui_from_result_file(
        tmp_path / "nonexistent.json",
        tmp_path / "review.html",
    )
    assert r.status == LLMReviewUIStatus.FAILED


def test_render_from_invalid_json_returns_failed(tmp_path: Path):
    """render_llm_review_ui_from_result_file returns FAILED for invalid JSON."""
    bad_path = tmp_path / "bad.json"
    bad_path.write_text("not valid json", encoding="utf-8")
    r = render_llm_review_ui_from_result_file(bad_path, tmp_path / "review.html")
    assert r.status == LLMReviewUIStatus.FAILED


def test_render_result_includes_candidate_count(tmp_path: Path):
    """Renderer result includes candidate count."""
    result = _make_mock_result()
    r = render_llm_review_ui_page(result, tmp_path / "review.html")
    assert r.candidate_count == 2
    assert r.candidates_requiring_confirmation == 1
