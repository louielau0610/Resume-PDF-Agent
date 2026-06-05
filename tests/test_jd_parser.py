"""Tests for M15 JD parser."""

from __future__ import annotations

from pathlib import Path

from resume_pdf_agent.jd.parser import (
    normalize_jd_text,
    parse_user_provided_jd,
)
from resume_pdf_agent.models.jd import JDComplianceStatus, JDSourceType

_SAMPLE_JD_PATH = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "sample_inputs"
    / "sample_data_science_jd.txt"
)


def _sample_jd_text() -> str:
    return _SAMPLE_JD_PATH.read_text(encoding="utf-8")


class TestNormalizeJdText:

    def test_strips_whitespace(self):
        result = normalize_jd_text("  hello  \n\nworld  ")
        assert result.startswith("hello")
        assert "world" in result

    def test_collapses_blank_lines(self):
        result = normalize_jd_text("line1\n\n\n\nline2")
        assert "\n\n\n" not in result


class TestParseUserProvidedJd:

    def test_extracts_role_title(self):
        text = _sample_jd_text()
        parsed = parse_user_provided_jd(text)
        assert parsed.role_title is not None
        assert "Data Science" in parsed.role_title

    def test_extracts_responsibilities(self):
        text = _sample_jd_text()
        parsed = parse_user_provided_jd(text)
        assert len(parsed.responsibilities) > 0

    def test_extracts_required_qualifications(self):
        text = _sample_jd_text()
        parsed = parse_user_provided_jd(text)
        assert len(parsed.required_qualifications) > 0

    def test_extracts_preferred_qualifications(self):
        text = _sample_jd_text()
        parsed = parse_user_provided_jd(text)
        assert len(parsed.preferred_qualifications) > 0

    def test_extracts_skills(self):
        text = _sample_jd_text()
        parsed = parse_user_provided_jd(text)
        assert "python" in parsed.skills or "Python" in str(parsed.skills).lower()
        assert "sql" in parsed.skills or "SQL" in str(parsed.skills).lower()

    def test_deduplicates_skills(self):
        text = _sample_jd_text()
        parsed = parse_user_provided_jd(text)
        assert len(parsed.skills) == len(set(parsed.skills))

    def test_compliance_passed(self):
        text = _sample_jd_text()
        parsed = parse_user_provided_jd(text)
        assert parsed.compliance_result.status == JDComplianceStatus.ALLOWED

    def test_blocked_jd_returns_minimal_result(self):
        text = "CONFIDENTIAL do not distribute. Data Scientist."
        parsed = parse_user_provided_jd(text)
        assert parsed.compliance_result.status == JDComplianceStatus.BLOCKED
        assert len(parsed.responsibilities) == 0

    def test_extracts_company_name(self):
        text = _sample_jd_text()
        parsed = parse_user_provided_jd(text)
        assert parsed.company_name is not None

    def test_extracts_location(self):
        text = _sample_jd_text()
        parsed = parse_user_provided_jd(text)
        assert parsed.location is not None
