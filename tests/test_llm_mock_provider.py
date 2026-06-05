"""Tests for M16 LLM mock provider."""

from __future__ import annotations

import pytest

from resume_pdf_agent.llm.providers import (
    DisabledLLMProvider,
    ExternalLLMProvider,
    MockLLMProvider,
    get_llm_provider,
)
from resume_pdf_agent.models.llm import LLMProviderType, LLMRewriteRequest


class TestMockProvider:

    def test_mock_is_deterministic(self):
        provider = MockLLMProvider()
        req = LLMRewriteRequest(
            original_text="test bullet",
            allowed_facts=["test"],
        )
        r1 = provider.rewrite(req)
        r2 = provider.rewrite(req)
        assert r1 == r2

    def test_mock_no_network(self):
        provider = MockLLMProvider()
        req = LLMRewriteRequest(original_text="hello world")
        result = provider.rewrite(req)
        assert len(result) > 0

    def test_mock_normalizes_whitespace(self):
        provider = MockLLMProvider()
        req = LLMRewriteRequest(original_text="  hello   world  ")
        result = provider.rewrite(req)
        assert "  " not in result


class TestDisabledProvider:

    def test_disabled_raises(self):
        provider = DisabledLLMProvider()
        req = LLMRewriteRequest(original_text="test")
        with pytest.raises(RuntimeError):
            provider.rewrite(req)


class TestExternalProvider:

    def test_external_raises_not_implemented(self):
        provider = ExternalLLMProvider()
        req = LLMRewriteRequest(original_text="test")
        with pytest.raises(NotImplementedError):
            provider.rewrite(req)


class TestGetLlmProvider:

    def test_returns_correct_types(self):
        assert isinstance(get_llm_provider(LLMProviderType.DISABLED), DisabledLLMProvider)
        assert isinstance(get_llm_provider(LLMProviderType.MOCK), MockLLMProvider)
        assert isinstance(get_llm_provider(LLMProviderType.EXTERNAL), ExternalLLMProvider)
