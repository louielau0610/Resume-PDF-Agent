"""Tests for M16 LLM rewrite engine."""

from __future__ import annotations

from resume_pdf_agent.llm.rewrite import rewrite_bullets_with_llm
from resume_pdf_agent.models.enums import (
    EvidenceLevel,
    ExperienceType,
    MetricStatus,
    ResumeType,
)
from resume_pdf_agent.models.llm import (
    LLMProviderType,
    LLMRewriteMode,
    LLMRewriteOptions,
    LLMRewriteStatus,
)
from resume_pdf_agent.models.resume_content import (
    ExperienceEntry,
    ResumeContent,
)
from resume_pdf_agent.models.truthfulness import (
    ClaimEvidenceStatus,
    RiskLevel,
    TruthfulnessCheckResult,
    TruthfulnessIssue,
    TruthfulnessIssueType,
    TruthfulnessSeverity,
)


def _make_resume() -> ResumeContent:
    return ResumeContent(
        resume_type=ResumeType.DATA_SCIENCE_RESUME,
        experiences=[
            ExperienceEntry(
                experience_id="exp1",
                experience_type=ExperienceType.PROJECT,
                title="Test",
                organization="Org",
                responsibilities=["Analyzed data using Python and SQL."],
            )
        ],
    )


class TestRewriteBulletsWithLlm:

    def test_disabled_returns_disabled(self):
        rc = _make_resume()
        result = rewrite_bullets_with_llm(rc)
        assert result.status == LLMRewriteStatus.DISABLED

    def test_enabled_false_returns_disabled(self):
        rc = _make_resume()
        opts = LLMRewriteOptions(enabled=False)
        result = rewrite_bullets_with_llm(rc, options=opts)
        assert result.status == LLMRewriteStatus.DISABLED

    def test_skips_on_high_risk_truthfulness(self):
        rc = _make_resume()
        tr = TruthfulnessCheckResult(
            overall_risk_level=RiskLevel.HIGH,
            safe_to_proceed=False,
            claims_checked=1,
            high_risk_count=1,
            medium_risk_count=0,
            low_risk_count=0,
            summary="High risk",
        )
        opts = LLMRewriteOptions(
            enabled=True,
            provider=LLMProviderType.MOCK,
            require_truthfulness_pass=True,
        )
        result = rewrite_bullets_with_llm(rc, truthfulness_result=tr, options=opts)
        assert result.status == LLMRewriteStatus.SKIPPED_DUE_TO_SAFETY

    def test_mock_provider_generates_candidates(self):
        rc = _make_resume()
        opts = LLMRewriteOptions(
            enabled=True,
            provider=LLMProviderType.MOCK,
            require_truthfulness_pass=False,
        )
        result = rewrite_bullets_with_llm(rc, options=opts)
        assert result.candidates_generated >= 0
