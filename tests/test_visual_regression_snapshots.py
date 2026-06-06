"""Tests for M18 visual regression snapshots."""

from __future__ import annotations

from resume_pdf_agent.visual_regression.snapshots import (
    compare_snapshot_text,
    extract_stable_snapshot_sections,
    normalize_html_for_snapshot,
)


class TestNormalizeHtmlForSnapshot:

    def test_collapses_whitespace(self):
        result = normalize_html_for_snapshot("hello    world")
        assert "    " not in result

    def test_removes_timestamps(self):
        result = normalize_html_for_snapshot("created at 2024-01-15T10:30:00Z")
        assert "[TIMESTAMP]" in result
        assert "2024-01-15" not in result

    def test_deterministic(self):
        r1 = normalize_html_for_snapshot("  hello  world  ")
        r2 = normalize_html_for_snapshot("  hello  world  ")
        assert r1 == r2


class TestExtractStableSnapshotSections:

    def test_extracts_css_classes(self):
        html = '<div class="app-shell hero-panel"><div class="metric-grid"></div></div>'
        sections = extract_stable_snapshot_sections(html)
        assert "css_classes" in sections
        assert "app-shell" in sections["css_classes"]


class TestCompareSnapshotText:

    def test_identical_match(self):
        ok, diffs = compare_snapshot_text("line1\nline2", "line1\nline2")
        assert ok is True
        assert len(diffs) == 0

    def test_difference_detected(self):
        ok, diffs = compare_snapshot_text("line1\nline2", "line1\nline3")
        assert ok is False  # 0 allowed changes
        assert len(diffs) > 0
