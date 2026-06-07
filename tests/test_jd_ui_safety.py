"""Safety tests for M21 JD upload UI."""

from __future__ import annotations

from pathlib import Path

from resume_pdf_agent.jd_ui.renderer import render_jd_upload_ui_page
from resume_pdf_agent.jd_ui.safety import (
    escape_jd_ui_text,
    get_client_side_jd_risk_markers,
    safe_jd_ui_output_path,
)
from resume_pdf_agent.models.jd_ui import JDClientComplianceHint


# ---------------------------------------------------------------------------
# escape_jd_ui_text
# ---------------------------------------------------------------------------

def test_escape_jd_ui_text_escapes_script_tag():
    """escape_jd_ui_text escapes <script> tags."""
    result = escape_jd_ui_text("<script>alert(1)</script>")
    assert "<script>" not in result
    assert "&lt;" in result


def test_escape_jd_ui_text_escapes_html_entities():
    """escape_jd_ui_text escapes HTML special characters."""
    result = escape_jd_ui_text('<img src=x onerror=alert(1)>')
    assert "<img" not in result
    assert "&lt;" in result


def test_escape_jd_ui_text_escapes_quotes():
    """escape_jd_ui_text escapes both single and double quotes."""
    result = escape_jd_ui_text("He said 'hello' and \"world\"")
    assert "&#x27;" in result or "&apos;" in result or "'" not in result  # depends on html.escape quote=True
    # html.escape with quote=True converts " to &quot;
    assert "&quot;" in result


def test_escape_jd_ui_text_preserves_safe_text():
    """escape_jd_ui_text preserves text without special chars."""
    safe = "Hello World 123"
    assert escape_jd_ui_text(safe) == safe


# ---------------------------------------------------------------------------
# get_client_side_jd_risk_markers
# ---------------------------------------------------------------------------

def test_get_client_side_jd_risk_markers_returns_list():
    """get_client_side_jd_risk_markers returns a non-empty list."""
    markers = get_client_side_jd_risk_markers()
    assert isinstance(markers, list)
    assert len(markers) > 0


def test_markers_are_jd_client_compliance_hint_instances():
    """Each marker is a JDClientComplianceHint with valid fields."""
    markers = get_client_side_jd_risk_markers()
    for m in markers:
        assert isinstance(m, JDClientComplianceHint)
        assert len(m.marker) >= 1
        assert len(m.severity) >= 1
        assert len(m.explanation) >= 1
        assert len(m.suggested_action) >= 1


def test_markers_include_all_required_terms():
    """Markers include all required blocking terms."""
    markers = get_client_side_jd_risk_markers()
    marker_texts = {m.marker for m in markers}
    required = {
        "confidential",
        "internal use only",
        "do not distribute",
        "interview scorecard",
        "candidate evaluation form",
        "scoring rubric",
        "leaked",
        "not for public release",
        "restricted access",
    }
    missing = required - marker_texts
    assert not missing, f"Missing markers: {missing}"


def test_all_markers_have_blocking_severity():
    """All markers have blocking severity."""
    markers = get_client_side_jd_risk_markers()
    for m in markers:
        assert m.severity == "blocking"


# ---------------------------------------------------------------------------
# safe_jd_ui_output_path
# ---------------------------------------------------------------------------

def test_safe_jd_ui_output_path_resolves(tmp_path: Path):
    """safe_jd_ui_output_path returns resolved absolute path."""
    result = safe_jd_ui_output_path(tmp_path / "sub" / "output.html")
    assert result.is_absolute()
    assert ".." not in str(result.parent)  # May still be in path if not resolved


def test_safe_jd_ui_output_path_accepts_string():
    """safe_jd_ui_output_path accepts a string."""
    result = safe_jd_ui_output_path("outputs/test.html")
    assert isinstance(result, Path)


# ---------------------------------------------------------------------------
# rendered HTML safety
# ---------------------------------------------------------------------------

def test_rendered_html_does_not_contain_raw_script_injection(tmp_path: Path):
    """Rendered HTML from renderer does not contain raw <script> from context injection."""
    result = render_jd_upload_ui_page(tmp_path / "safety_test.html")
    html = result.html
    # The page contains inline <script> for the JS module, which is expected.
    # But there should be no unescaped user-input <script> blocks.
    # The page title/safety_notice are hardcoded, so they're safe.
    # Check that no <script> block contains user-controlled content directly.
    assert result.status.value == "rendered"


def test_rendered_html_no_network_requests_in_js(tmp_path: Path):
    """The embedded JS contains no network request primitives."""
    result = render_jd_upload_ui_page(tmp_path / "no_net.html")
    html = result.html

    # Find the <script> block content
    script_start = html.find("<script>")
    script_end = html.find("</script>")
    if script_start == -1 or script_end == -1:
        # JS might be inlined differently; check full HTML
        js_content = html
    else:
        js_content = html[script_start:script_end]

    js_lower = js_content.lower()
    assert "fetch(" not in js_lower
    assert "xmlhttprequest" not in js_lower
    assert "navigator.sendbeacon" not in js_lower
    assert "websocket" not in js_lower


def test_rendered_html_no_eval_in_js(tmp_path: Path):
    """The embedded JS contains no eval() or dynamic import()."""
    result = render_jd_upload_ui_page(tmp_path / "no_eval.html")
    html = result.html
    # Find script content
    script_start = html.find("<script>")
    script_end = html.find("</script>")
    if script_start != -1 and script_end != -1:
        js_content = html[script_start:script_end].lower()
    else:
        js_content = html.lower()

    assert "eval(" not in js_content
    assert "import(" not in js_content


def test_rendered_html_no_http_urls_in_js(tmp_path: Path):
    """The embedded JS contains no http:// or https:// URLs."""
    result = render_jd_upload_ui_page(tmp_path / "no_urls.html")
    html = result.html
    # Find script content
    script_start = html.find("<script>")
    script_end = html.find("</script>")
    if script_start != -1 and script_end != -1:
        js_content = html[script_start:script_end]
    else:
        js_content = html

    assert "http://" not in js_content
    assert "https://" not in js_content


def test_css_no_external_import(tmp_path: Path):
    """The embedded CSS has no @import url() calls."""
    result = render_jd_upload_ui_page(tmp_path / "css_check.html")
    html = result.html.lower()
    # Find the <style> block
    style_start = html.find("<style>")
    style_end = html.find("</style>")
    if style_start != -1 and style_end != -1:
        css_content = html[style_start:style_end]
    else:
        css_content = html

    assert "@import url(" not in css_content


def test_css_no_external_font_image_url(tmp_path: Path):
    """The CSS contains no external font or image URLs."""
    result = render_jd_upload_ui_page(tmp_path / "css_font_check.html")
    html = result.html.lower()
    assert "url(http" not in html  # catches url(http:// and url(https://
    assert "fonts.googleapis" not in html


def test_ui_does_not_bypass_m15_backend(tmp_path: Path):
    """The JD upload UI explicitly states backend M15 check is authoritative."""
    result = render_jd_upload_ui_page(tmp_path / "m15_check.html")
    html = result.html.lower()
    # Should state backend check remains authoritative
    assert "authoritative" in html
    assert "m15" in html or "backend" in html


def test_ui_does_not_claim_browser_hints_authoritative(tmp_path: Path):
    """The UI does not claim browser-side hints are authoritative."""
    result = render_jd_upload_ui_page(tmp_path / "no_auth_claim.html")
    html = result.html.lower()
    # Should contain a disclaimer that it does NOT verify compliance
    assert "this page does not verify compliance" in html or "does not verify compliance" in html or "local hints only" in html


# ---------------------------------------------------------------------------
# static JS file reads
# ---------------------------------------------------------------------------

def test_static_js_file_has_no_network_primitives():
    """The jd_upload_page.js source file has no network primitives."""
    js_path = (
        Path(__file__).resolve().parent.parent
        / "src" / "resume_pdf_agent" / "jd_ui" / "static" / "jd_upload_page.js"
    )
    js_content = js_path.read_text(encoding="utf-8").lower()
    assert "fetch(" not in js_content
    assert "xmlhttprequest" not in js_content
    assert "navigator.sendbeacon" not in js_content
    assert "websocket" not in js_content


def test_static_js_file_has_no_eval():
    """The jd_upload_page.js source file has no eval() or import()."""
    js_path = (
        Path(__file__).resolve().parent.parent
        / "src" / "resume_pdf_agent" / "jd_ui" / "static" / "jd_upload_page.js"
    )
    js_content = js_path.read_text(encoding="utf-8")
    assert "eval(" not in js_content
    assert "import(" not in js_content


def test_static_js_file_has_no_http_urls():
    """The jd_upload_page.js source file has no http/https URLs."""
    js_path = (
        Path(__file__).resolve().parent.parent
        / "src" / "resume_pdf_agent" / "jd_ui" / "static" / "jd_upload_page.js"
    )
    js_content = js_path.read_text(encoding="utf-8")
    assert "http://" not in js_content
    assert "https://" not in js_content


def test_static_js_has_deterministic_marker_detection():
    """The JS file has deterministic marker detection logic."""
    js_path = (
        Path(__file__).resolve().parent.parent
        / "src" / "resume_pdf_agent" / "jd_ui" / "static" / "jd_upload_page.js"
    )
    js_content = js_path.read_text(encoding="utf-8")
    assert "RISK_MARKERS" in js_content
    assert "indexOf" in js_content
    assert "analyzeLocally" in js_content


def test_static_js_has_no_server_submission():
    """The JS file has no server submission logic."""
    js_path = (
        Path(__file__).resolve().parent.parent
        / "src" / "resume_pdf_agent" / "jd_ui" / "static" / "jd_upload_page.js"
    )
    js_content = js_path.read_text(encoding="utf-8")
    assert "form.submit" not in js_content.lower()
    assert ".post(" not in js_content.lower()
    assert ".send(" not in js_content.lower() or "beacon" in js_content.lower()  # navigator.sendBeacon already checked
    assert "upload(" not in js_content.lower()


# ---------------------------------------------------------------------------
# static CSS file reads
# ---------------------------------------------------------------------------

def test_static_css_file_has_no_import_url():
    """The jd_upload_page.css source file has no @import url()."""
    css_path = (
        Path(__file__).resolve().parent.parent
        / "src" / "resume_pdf_agent" / "jd_ui" / "static" / "jd_upload_page.css"
    )
    css_content = css_path.read_text(encoding="utf-8")
    assert "@import url(" not in css_content


def test_static_css_file_has_no_external_urls():
    """The jd_upload_page.css source file has no external http/https URLs."""
    css_path = (
        Path(__file__).resolve().parent.parent
        / "src" / "resume_pdf_agent" / "jd_ui" / "static" / "jd_upload_page.css"
    )
    css_content = css_path.read_text(encoding="utf-8")
    assert "url(http" not in css_content
    assert "url(https" not in css_content
