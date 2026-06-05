"""Tests for M16 LLM models."""

from __future__ import annotations

import pytest

from resume_pdf_agent.models.llm import (
    LLMProviderType,
    LLMRewriteCandidate,
    LLMRewriteMode,
    LLMRewriteOptions,
    LLMRewriteRequest,
    LLMRewriteResult,
    LLMRewriteStatus,
)
from resume_pdf_agent.models.enums import EvidenceLevel, MetricStatus


class TestLLMModels:

    def test_default_options_are_disabled(self):
        opts = LLMRewriteOptions()
        assert opts.enabled is False
        assert opts.provider == LLMProviderType.DISABLED

    def test_enabled_with_disabled_provider(self):
        opts = LLMRewriteOptions(enabled=True, provider=LLMProviderType.DISABLED)
        assert opts.enabled is True

    def test_candidate_defaults_needs_confirmation(self):
        c = LLMRewriteCandidate(
            candidate_id="c1",
            original_text="test",
            rewritten_text="test",
            provider=LLMProviderType.MOCK,
            mode=LLMRewriteMode.CONSERVATIVE_POLISH,
            status=LLMRewriteStatus.REWRITTEN,
        )
        assert c.needs_confirmation is True

    def test_candidate_evidence_not_stronger(self):
        c = LLMRewriteCandidate(
            candidate_id="c1",
            original_text="test",
            rewritten_text="test",
            provider=LLMProviderType.MOCK,
            mode=LLMRewriteMode.CONSERVATIVE_POLISH,
            status=LLMRewriteStatus.REWRITTEN,
            evidence_level=EvidenceLevel.NEEDS_USER_CONFIRMATION,
        )
        assert c.evidence_level != EvidenceLevel.USER_PROVIDED

    def test_result_failed_validation_has_reason(self):
        with pytest.raises(ValueError):
            LLMRewriteResult(
                status=LLMRewriteStatus.FAILED_VALIDATION,
                provider=LLMProviderType.MOCK,
                summary="no warnings or errors",
            )

    def test_result_disabled_ok(self):
        r = LLMRewriteResult(
            status=LLMRewriteStatus.DISABLED,
            provider=LLMProviderType.DISABLED,
            summary="disabled",
        )
        assert r.candidates_generated == 0
