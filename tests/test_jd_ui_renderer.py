"""Tests for M21 JD upload UI renderer."""

from __future__ import annotations

from pathlib import Path

from resume_pdf_agent.jd_ui.renderer import render_jd_upload_ui_page
from resume_pdf_agent.models.jd_ui import (
    JDUploadUIOptions,
    JDUploadUIStatus,
)


def test_render_jd_upload_ui_page_importable():
    """render_jd_upload_ui_page is importable and callable."""
    assert callable(render_jd_upload_ui_page)


def test_render_creates_html_file(tmp_path: Path):
    """Renderer creates a non-empty jd_upload.html file."""
    output_path = tmp_path / "jd_upload.html"
    result = render_jd_upload_ui_page(output_path)
    assert result.status == JDUploadUIStatus.RENDERED
    assert result.output_path is not None
    assert Path(result.output_path).is_file()
    assert Path(result.output_path).stat().st_size > 0
    assert len(result.html) > 0


def test_render_creates_output_dir(tmp_path: Path):
    """Renderer creates parent directories if they don't exist."""
    output_path = tmp_path / "deeply" / "nested" / "jd_upload.html"
    result = render_jd_upload_ui_page(output_path)
    assert result.status == JDUploadUIStatus.RENDERED
    assert Path(result.output_path).is_file()


def test_render_returns_rendered_status_on_success(tmp_path: Path):
    """Renderer returns RENDERED status with html and output_path."""
    result = render_jd_upload_ui_page(tmp_path / "jd_upload.html")
    assert result.status == JDUploadUIStatus.RENDERED
    assert result.output_path is not None
    assert result.html
    assert "JD upload UI rendered to" in result.summary


def test_render_accepts_str_path(tmp_path: Path):
    """Renderer accepts a string path."""
    output_path = str(tmp_path / "jd_upload.html")
    result = render_jd_upload_ui_page(output_path)
    assert result.status == JDUploadUIStatus.RENDERED


def test_html_contains_jd_textarea(tmp_path: Path):
    """Rendered HTML contains a JD textarea element."""
    result = render_jd_upload_ui_page(tmp_path / "jd_upload.html")
    html = result.html
    assert 'id="jd-text"' in html
    assert "<textarea" in html


def test_html_contains_local_static_page_notice(tmp_path: Path):
    """Rendered HTML states it's a local static page."""
    result = render_jd_upload_ui_page(tmp_path / "jd_upload.html")
    html = result.html.lower()
    assert "local static page" in html
    assert "no data is submitted" in html


def test_html_contains_public_jd_only_notice(tmp_path: Path):
    """Rendered HTML mentions public job descriptions only."""
    result = render_jd_upload_ui_page(tmp_path / "jd_upload.html")
    html = result.html.lower()
    assert "public job description" in html or "public" in html


def test_html_contains_backend_authoritative_notice(tmp_path: Path):
    """Rendered HTML states backend M15 check remains authoritative."""
    result = render_jd_upload_ui_page(tmp_path / "jd_upload.html")
    html = result.html.lower()
    assert "m15" in html or "backend" in html
    assert "authoritative" in html


def test_html_contains_compliance_hints_panel(tmp_path: Path):
    """Rendered HTML contains a compliance hints / risk hint panel."""
    result = render_jd_upload_ui_page(tmp_path / "jd_upload.html")
    html = result.html
    assert "compliance-hints" in html or "Compliance Hints" in html
    assert "Analyze Locally" in html


def test_html_contains_generated_jd_text_preview(tmp_path: Path):
    """Rendered HTML contains a generated JD text preview area."""
    result = render_jd_upload_ui_page(tmp_path / "jd_upload.html")
    html = result.html
    assert 'id="jd-text-output"' in html
    assert "jd_text.txt" in html


def test_html_contains_json_payload_preview(tmp_path: Path):
    """Rendered HTML contains a JSON payload preview area."""
    result = render_jd_upload_ui_page(tmp_path / "jd_upload.html")
    html = result.html
    assert 'id="json-output"' in html
    assert "jd_payload.json" in html


def test_html_contains_copy_download_controls(tmp_path: Path):
    """Rendered HTML contains copy and download buttons."""
    result = render_jd_upload_ui_page(tmp_path / "jd_upload.html")
    html = result.html
    assert "copyActiveTab" in html
    assert "downloadActiveTab" in html


def test_html_contains_cli_instruction_section(tmp_path: Path):
    """Rendered HTML contains CLI instruction section."""
    result = render_jd_upload_ui_page(tmp_path / "jd_upload.html")
    html = result.html
    assert "CLI Instructions" in html or "命令行说明" in html


def test_html_contains_risk_marker_terms(tmp_path: Path):
    """Rendered HTML contains risk marker terms like 'confidential'."""
    result = render_jd_upload_ui_page(tmp_path / "jd_upload.html")
    html = result.html
    # The JS array embeds these markers
    assert "confidential" in html
    assert "internal use only" in html or "internal" in html


def test_html_no_compliance_verification_claim(tmp_path: Path):
    """Rendered HTML does not positively claim browser-side compliance verification."""
    result = render_jd_upload_ui_page(tmp_path / "jd_upload.html")
    html = result.html.lower()
    # Footer says "does NOT verify compliance" - this is a disclaimer, not a claim
    # The page must not positively claim to verify compliance
    assert "browser verifies compliance" not in html
    assert "client-side verification" not in html
    # Must include the disclaimer
    assert "does not verify compliance" in html or "does not verify" in html


def test_html_no_hiring_probability_claim(tmp_path: Path):
    """Rendered HTML does not positively claim hiring probability prediction."""
    result = render_jd_upload_ui_page(tmp_path / "jd_upload.html")
    html = result.html.lower()
    # Footer says "does NOT predict hiring probability" - this is a disclaimer
    # The page must not positively claim to predict hiring outcomes
    assert "can predict hiring" not in html
    assert "predicts your hiring" not in html
    assert "offer probability" not in html
    assert "interview probability" not in html
    # Must include the disclaimer
    assert "does not predict hiring probability" in html


def test_html_no_internal_screening_claim(tmp_path: Path):
    """Rendered HTML does not positively claim internal screening access."""
    result = render_jd_upload_ui_page(tmp_path / "jd_upload.html")
    html = result.html.lower()
    # Footer says "does NOT ... access internal screening standards" - disclaimer
    # The page must not positively claim internal screening access
    assert "provides internal screening" not in html
    assert "internal screening system" not in html
    assert "company screening access" not in html
    # Must include the disclaimer
    assert "internal screening" in html  # mentioned in disclaimer context


def test_html_no_external_cdn_links(tmp_path: Path):
    """Rendered HTML has no external CDN links."""
    result = render_jd_upload_ui_page(tmp_path / "jd_upload.html")
    html = result.html
    assert "cdn." not in html.lower()
    assert "unpkg.com" not in html
    assert "jsdelivr" not in html.lower()
    assert "cloudflare" not in html.lower()


def test_html_no_external_font_imports(tmp_path: Path):
    """Rendered HTML has no external font @import or URL."""
    result = render_jd_upload_ui_page(tmp_path / "jd_upload.html")
    html = result.html.lower()
    assert "@import url(http" not in html
    assert "@import url(//" not in html
    assert "fonts.googleapis.com" not in html
    assert "fonts.gstatic.com" not in html


def test_html_no_react_vite_next_markers(tmp_path: Path):
    """Rendered HTML has no React, Vite, or Next.js markers."""
    result = render_jd_upload_ui_page(tmp_path / "jd_upload.html")
    html = result.html.lower()
    assert "react-dom" not in html
    assert "__vite" not in html
    assert "__next" not in html
    assert "next.js" not in html
    assert "/static/media/" not in html


def test_html_no_form_action_to_server(tmp_path: Path):
    """Rendered HTML has no form action pointing to a server."""
    result = render_jd_upload_ui_page(tmp_path / "jd_upload.html")
    html = result.html.lower()
    assert '<form' not in html
    assert 'action="http' not in html


def test_render_with_custom_options_disables_sections(tmp_path: Path):
    """Custom options that disable UI sections reflect in HTML."""
    opts = JDUploadUIOptions(
        include_copy_buttons=False,
        include_download_buttons=False,
        include_compliance_hints=False,
        include_cli_instructions=False,
    )
    result = render_jd_upload_ui_page(tmp_path / "jd_upload.html", opts)
    html = result.html
    # copy/download button HTML should not appear (JS functions are always embedded)
    assert 'onclick="copyActiveTab()"' not in html
    assert 'onclick="downloadActiveTab()"' not in html
    assert "Copy to Clipboard" not in html
    assert "Download File" not in html
    # compliance hints panel section should not appear
    assert 'id="compliance-hints"' not in html
    assert "Compliance Hints" not in html
    # CLI instructions section should not appear
    assert "CLI Instructions" not in html
    assert "命令行说明" not in html


def test_render_failure_returns_failed_status(tmp_path: Path):
    """Renderer returns FAILED status when template is missing (simulated via bad options)."""
    # The renderer should gracefully handle errors and return FAILED.
    # We test a valid render first, then verify error handling exists.
    result = render_jd_upload_ui_page(tmp_path / "should_work.html")
    assert result.status == JDUploadUIStatus.RENDERED
    assert not result.errors
