"""Tests for M15 JD compliance checker."""

from __future__ import annotations

from resume_pdf_agent.jd.compliance import check_jd_compliance
from resume_pdf_agent.models.jd import (
    JDComplianceStatus,
    JDSourceType,
)


class TestCheckJdCompliance:

    def test_normal_jd_allowed(self):
        """A normal public-style JD should be allowed."""
        text = "Data Scientist - We are looking for a data scientist to join our team. Responsibilities include data analysis and modeling."
        result = check_jd_compliance(text)
        assert result.status == JDComplianceStatus.ALLOWED
        assert result.can_parse is True

    def test_confidential_blocked(self):
        """Text containing 'confidential' should be blocked."""
        text = "CONFIDENTIAL - Internal use only. Data Scientist position."
        result = check_jd_compliance(text)
        assert result.status == JDComplianceStatus.BLOCKED
        assert result.can_parse is False

    def test_internal_use_only_blocked(self):
        """Text containing 'internal use only' should be blocked."""
        text = "For internal use only. Job description for Data Scientist."
        result = check_jd_compliance(text)
        assert result.status == JDComplianceStatus.BLOCKED

    def test_interview_scorecard_blocked(self):
        """Text containing 'interview scorecard' should be blocked."""
        text = "Interview scorecard for data science candidates."
        result = check_jd_compliance(text)
        assert result.status == JDComplianceStatus.BLOCKED

    def test_candidate_evaluation_form_blocked(self):
        """Text containing 'candidate evaluation form' should be blocked."""
        text = "Candidate evaluation form - rate on a scale of 1-5."
        result = check_jd_compliance(text)
        assert result.status == JDComplianceStatus.BLOCKED

    def test_scoring_rubric_blocked(self):
        """Text containing 'scoring rubric' should be blocked."""
        text = "Resume scoring rubric for hiring managers."
        result = check_jd_compliance(text)
        assert result.status == JDComplianceStatus.BLOCKED

    def test_ambiguous_text_warned(self):
        """Text with mild ambiguous markers should get warnings."""
        text = "Recruiter screen notes: Looking for a data scientist. Assessment criteria include Python skills."
        result = check_jd_compliance(text)
        assert result.status in (
            JDComplianceStatus.ALLOWED_WITH_WARNINGS,
            JDComplianceStatus.BLOCKED,
        )

    def test_clean_text_no_issues(self):
        """Completely clean JD text should have no issues."""
        text = "We are hiring a software engineer. Requirements: Python, Java. Apply at example.com."
        result = check_jd_compliance(text)
        assert result.status == JDComplianceStatus.ALLOWED
        assert len(result.issues) == 0

    def test_can_parse_false_when_blocked(self):
        """can_parse must be False when status is BLOCKED."""
        text = "CONFIDENTIAL internal screening rubric"
        result = check_jd_compliance(text)
        assert result.can_parse is False

    def test_source_unknown_warning(self):
        """Unknown source type triggers a warning."""
        text = "We need a data analyst."
        result = check_jd_compliance(
            text, source_type=JDSourceType.UNKNOWN
        )
        assert len(result.warnings) > 0 or len(result.issues) > 0
