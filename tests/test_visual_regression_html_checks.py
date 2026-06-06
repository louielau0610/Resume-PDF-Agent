"""Tests for M18 visual regression HTML checks."""

from __future__ import annotations

from resume_pdf_agent.visual_regression.html_checks import (
    check_dashboard_html_structure,
    check_no_forbidden_frontend_content,
    check_required_css_classes,
    check_resume_html_structure,
)

_DASHBOARD_HTML = """<!DOCTYPE html>
<html><head></head><body>
<main class="app-shell">
<header class="top-bar"><span>Resume Intelligence Console</span></header>
<section class="hero-panel"><h1>Workflow Dashboard</h1><div class="hero-meta"></div></section>
<section class="metric-grid"><div class="metric-card"></div></section>
<section class="section-panel"><div class="stage-timeline"><div class="stage-item"></div></div></section>
<section class="section-panel"><div class="artifact-grid"><a class="artifact-button"></a></div></section>
</main>
</body></html>"""

_RESUME_HTML = """<!DOCTYPE html>
<html><head></head><body>
<h1>Alex Chen</h1>
<section><h2>Education</h2><p>Example University</p></section>
<section><h2>Skills</h2><p>Python, SQL</p></section>
</body></html>"""


class TestCheckRequiredCssClasses:

    def test_all_present(self):
        missing = check_required_css_classes(_DASHBOARD_HTML, ["app-shell", "hero-panel"])
        assert missing == []

    def test_some_missing(self):
        missing = check_required_css_classes(_DASHBOARD_HTML, ["nonexistent-class"])
        assert len(missing) > 0


class TestCheckDashboardHtmlStructure:

    def test_valid_dashboard_passes(self):
        issues = check_dashboard_html_structure(_DASHBOARD_HTML)
        assert issues == []

    def test_missing_doctype(self):
        html = "<html><body><main class='app-shell'></main></body></html>"
        issues = check_dashboard_html_structure(html)
        assert any("DOCTYPE" in i for i in issues)

    def test_missing_required_classes(self):
        html = "<!DOCTYPE html><html><body></body></html>"
        issues = check_dashboard_html_structure(html)
        assert len(issues) > 0


class TestCheckResumeHtmlStructure:

    def test_valid_resume_passes(self):
        issues = check_resume_html_structure(_RESUME_HTML)
        assert issues == []

    def test_no_dashboard_classes_in_resume(self):
        html = """<!DOCTYPE html><html><body>
        <main class="app-shell">Resume</main>
        </body></html>"""
        issues = check_resume_html_structure(html)
        assert any("app-shell" in i for i in issues)

    def test_empty_body(self):
        html = "<!DOCTYPE html><html><body></body></html>"
        issues = check_resume_html_structure(html)
        assert len(issues) > 0


class TestCheckNoForbiddenContent:

    def test_flags_cdn_link(self):
        html = '<html><body><link href="https://cdn.example.com/style.css"></body></html>'
        issues = check_no_forbidden_frontend_content(html)
        assert any("CDN" in i for i in issues)

    def test_flags_hiring_probability(self):
        html = "<html><body>This predicts hiring probability</body></html>"
        issues = check_no_forbidden_frontend_content(html)
        assert any("hiring probability" in i.lower() for i in issues)

    def test_clean_html_passes(self):
        html = "<!DOCTYPE html><html><body><p>Safe content</p></body></html>"
        issues = check_no_forbidden_frontend_content(html)
        assert issues == []
