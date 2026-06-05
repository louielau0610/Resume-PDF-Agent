"""Tests for M15 JD criteria builder."""

from __future__ import annotations

from pathlib import Path

from resume_pdf_agent.jd.criteria_builder import build_criteria_profile_from_jd
from resume_pdf_agent.jd.parser import parse_user_provided_jd
from resume_pdf_agent.models.enums import SourceType

_SAMPLE_JD_PATH = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "sample_inputs"
    / "sample_data_science_jd.txt"
)


class TestBuildCriteriaProfileFromJd:

    def test_creates_profile_with_source_type(self):
        text = _SAMPLE_JD_PATH.read_text(encoding="utf-8")
        parsed = parse_user_provided_jd(text)
        result = build_criteria_profile_from_jd(parsed)
        assert result.criteria_profile is not None
        # Check source type
        for c in result.criteria_profile.criteria:
            assert c.source.source_type == SourceType.USER_PROVIDED_JD

    def test_no_fake_url(self):
        text = _SAMPLE_JD_PATH.read_text(encoding="utf-8")
        parsed = parse_user_provided_jd(text)
        result = build_criteria_profile_from_jd(parsed)
        for c in result.criteria_profile.criteria:
            assert c.source.url is None

    def test_has_minimum_criteria(self):
        text = _SAMPLE_JD_PATH.read_text(encoding="utf-8")
        parsed = parse_user_provided_jd(text)
        result = build_criteria_profile_from_jd(parsed)
        assert len(result.criteria_profile.criteria) >= 3

    def test_blocked_jd_returns_no_profile(self):
        text = "CONFIDENTIAL do not distribute."
        parsed = parse_user_provided_jd(text)
        result = build_criteria_profile_from_jd(parsed)
        assert result.criteria_profile is None
        assert len(result.errors) > 0

    def test_no_internal_screening_claim(self):
        text = _SAMPLE_JD_PATH.read_text(encoding="utf-8")
        parsed = parse_user_provided_jd(text)
        result = build_criteria_profile_from_jd(parsed)
        for c in result.criteria_profile.criteria:
            desc = c.description.lower()
            assert "internal screening" not in desc
            assert "proprietary" not in desc

    def test_resume_types_inferred(self):
        text = _SAMPLE_JD_PATH.read_text(encoding="utf-8")
        parsed = parse_user_provided_jd(text)
        result = build_criteria_profile_from_jd(parsed)
        assert len(result.criteria_profile.resume_types) > 0
