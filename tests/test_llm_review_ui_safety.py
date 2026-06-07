"""Safety tests for M22 LLM review UI."""

from __future__ import annotations

import json
from pathlib import Path

from resume_pdf_agent.llm_review_ui.renderer import render_llm_review_ui_page
from resume_pdf_agent.llm_review_ui.safety import (
    escape_llm_review_ui_text,
    get_llm_review_decision_options,
    safe_llm_review_output_path,
    validate_llm_rewrite_result_for_ui,
)
from resume_pdf_agent.models.llm import (
    LLMProviderType,
    LLMRewriteCandidate,
    LLMRewriteMode,
    LLMRewriteResult,
    LLMRewriteStatus,
)


def _make_mock_result() -> LLMRewriteResult:
    return LLMRewriteResult(
        status=LLMRewriteStatus.REWRITTEN,
        provider=LLMProviderType.MOCK,
        candidates=[
            LLMRewriteCandidate(
                candidate_id="c1",
                original_text="Built data pipelines.",
                rewritten_text="Designed and implemented scalable data pipelines.",
                provider=LLMProviderType.MOCK,
                mode=LLMRewriteMode.CONSERVATIVE_POLISH,
                status=LLMRewriteStatus.REWRITTEN,
            ),
        ],
        candidates_generated=1,
        candidates_requiring_confirmation=0,
        summary="Mock.",
    )


def _make_malicious_result() -> LLMRewriteResult:
    return LLMRewriteResult(
        status=LLMRewriteStatus.REWRITTEN,
        provider=LLMProviderType.MOCK,
        candidates=[
            LLMRewriteCandidate(
                candidate_id='" onmouseover="alert(1)',
                source_experience_id="</script><script>alert(\"xss\")</script>",
                original_text="<script>alert(\"xss\")</script>",
                rewritten_text="</textarea><script>alert(\"xss\")</script>",
                provider=LLMProviderType.MOCK,
                mode=LLMRewriteMode.CONSERVATIVE_POLISH,
                status=LLMRewriteStatus.REWRITTEN,
                validation_warnings=["javascript:alert(1)"],
                risk_flags=["</script><script>alert(\"xss\")</script>"],
                rationale='" onmouseover="alert(1)',
            ),
        ],
        candidates_generated=1,
        candidates_requiring_confirmation=1,
        summary="</script><script>alert(\"xss\")</script>",
    )


# ---------------------------------------------------------------------------
# escape_llm_review_ui_text
# ---------------------------------------------------------------------------

def test_escape_script_tag():
    """escape_llm_review_ui_text escapes <script> tags."""
    result = escape_llm_review_ui_text("<script>alert(1)</script>")
    assert "<script>" not in result
    assert "&lt;" in result


def test_escape_html_entities():
    """escape_llm_review_ui_text escapes HTML special chars."""
    result = escape_llm_review_ui_text('<img src=x onerror=alert(1)>')
    assert "<img" not in result


def test_escape_preserves_safe_text():
    """escape_llm_review_ui_text preserves safe text."""
    assert escape_llm_review_ui_text("Hello World") == "Hello World"


# ---------------------------------------------------------------------------
# get_llm_review_decision_options
# ---------------------------------------------------------------------------

def test_get_llm_review_decision_options_returns_list():
    """get_llm_review_decision_options returns a non-empty list."""
    opts = get_llm_review_decision_options()
    assert isinstance(opts, list)
    assert len(opts) >= 5


def test_decision_options_have_value_label_description():
    """Each decision option has value, label, description keys."""
    opts = get_llm_review_decision_options()
    for o in opts:
        assert "value" in o
        assert "label" in o
        assert "description" in o


# ---------------------------------------------------------------------------
# safe_llm_review_output_path
# ---------------------------------------------------------------------------

def test_safe_output_path_resolves(tmp_path: Path):
    """safe_llm_review_output_path resolves path."""
    p = safe_llm_review_output_path(tmp_path / "test.html")
    assert p.is_absolute()


# ---------------------------------------------------------------------------
# validate_llm_rewrite_result_for_ui
# ---------------------------------------------------------------------------

def test_validate_empty_candidates():
    """validate_llm_rewrite_result_for_ui warns about empty candidates."""
    result = LLMRewriteResult(
        status=LLMRewriteStatus.DISABLED,
        provider=LLMProviderType.DISABLED,
        candidates=[],
        candidates_generated=0,
        candidates_requiring_confirmation=0,
        summary="No candidates.",
    )
    issues = validate_llm_rewrite_result_for_ui(result)
    assert len(issues) >= 1
    assert any("no candidates" in i.lower() for i in issues)


def test_validate_valid_result():
    """validate_llm_rewrite_result_for_ui returns no issues for valid result."""
    result = _make_mock_result()
    issues = validate_llm_rewrite_result_for_ui(result)
    assert issues == []


# ---------------------------------------------------------------------------
# rendered HTML injection safety
# ---------------------------------------------------------------------------

def test_html_escapes_malicious_original_text(tmp_path: Path):
    """Rendered HTML does not contain raw <script> from candidate original_text."""
    result = LLMRewriteResult(
        status=LLMRewriteStatus.REWRITTEN,
        provider=LLMProviderType.MOCK,
        candidates=[
            LLMRewriteCandidate(
                candidate_id="xss1",
                original_text="<script>alert('xss')</script>",
                rewritten_text="Safe rewritten text.",
                provider=LLMProviderType.MOCK,
                mode=LLMRewriteMode.CONSERVATIVE_POLISH,
                status=LLMRewriteStatus.REWRITTEN,
            ),
        ],
        candidates_generated=1,
        candidates_requiring_confirmation=0,
        summary="XSS test.",
    )
    r = render_llm_review_ui_page(result, tmp_path / "xss_test.html")
    html = r.html
    # After escaping, the raw <script>alert should NOT appear
    assert "<script>alert" not in html
    # The escaped version should appear
    assert "&lt;script&gt;" in html


def test_html_autoescapes_malicious_candidate_contexts(tmp_path: Path):
    """Template autoescape protects visible text, attributes, and textarea-adjacent strings."""
    r = render_llm_review_ui_page(_make_malicious_result(), tmp_path / "xss_contexts.html")
    html = r.html

    assert "<script>alert" not in html
    assert "</textarea><script" not in html
    assert '" onmouseover="alert(1)' not in html
    assert "&lt;script&gt;alert" in html
    assert "&lt;/textarea&gt;&lt;script&gt;alert" in html
    assert "&#34; onmouseover=&#34;alert(1)" in html


def test_candidates_json_uses_html_safe_json(tmp_path: Path):
    """Embedded candidate JSON cannot close the script tag or inject HTML."""
    r = render_llm_review_ui_page(_make_malicious_result(), tmp_path / "xss_json.html")
    html = r.html

    assert "</script><script>alert" not in html
    assert "\\u003c/script\\u003e\\u003cscript\\u003ealert" in html
    assert "\\u003cscript\\u003ealert" in html
    assert "var CANDIDATES =" in html


# ---------------------------------------------------------------------------
# static JS safety
# ---------------------------------------------------------------------------

def test_static_js_no_network_primitives():
    """The llm_review_page.js has no network primitives."""
    js_path = (
        Path(__file__).resolve().parent.parent
        / "src" / "resume_pdf_agent" / "llm_review_ui" / "static" / "llm_review_page.js"
    )
    js = js_path.read_text(encoding="utf-8").lower()
    assert "fetch(" not in js
    assert "xmlhttprequest" not in js
    assert "navigator.sendbeacon" not in js
    assert "websocket" not in js


def test_static_js_no_eval():
    """The llm_review_page.js has no eval() or import()."""
    js_path = (
        Path(__file__).resolve().parent.parent
        / "src" / "resume_pdf_agent" / "llm_review_ui" / "static" / "llm_review_page.js"
    )
    js = js_path.read_text(encoding="utf-8")
    assert "eval(" not in js
    assert "import(" not in js


def test_static_js_no_http_urls():
    """The llm_review_page.js has no http/https URLs."""
    js_path = (
        Path(__file__).resolve().parent.parent
        / "src" / "resume_pdf_agent" / "llm_review_ui" / "static" / "llm_review_page.js"
    )
    js = js_path.read_text(encoding="utf-8")
    assert "http://" not in js
    assert "https://" not in js


def test_static_js_has_decisions_json_logic():
    """The llm_review_page.js has deterministic decisions JSON generation."""
    js_path = (
        Path(__file__).resolve().parent.parent
        / "src" / "resume_pdf_agent" / "llm_review_ui" / "static" / "llm_review_page.js"
    )
    js = js_path.read_text(encoding="utf-8")
    assert "decisions" in js
    assert "JSON.stringify" in js


def test_static_css_no_external_import():
    """The llm_review_page.css has no external imports."""
    css_path = (
        Path(__file__).resolve().parent.parent
        / "src" / "resume_pdf_agent" / "llm_review_ui" / "static" / "llm_review_page.css"
    )
    css = css_path.read_text(encoding="utf-8").lower()
    assert "@import" not in css


def test_static_css_no_external_urls():
    """The llm_review_page.css has no external URLs."""
    css_path = (
        Path(__file__).resolve().parent.parent
        / "src" / "resume_pdf_agent" / "llm_review_ui" / "static" / "llm_review_page.css"
    )
    css = css_path.read_text(encoding="utf-8").lower()
    assert "url(" not in css
    assert "url(http" not in css
    assert "http://" not in css
    assert "https://" not in css
