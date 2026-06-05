"""LLM provider interface and implementations for M16.

Provides a plugin-like provider system with:
- DisabledLLMProvider (default, no-op)
- MockLLMProvider (deterministic, for tests)
- ExternalLLMProvider (placeholder for future real integration)
"""

from __future__ import annotations

import abc

from resume_pdf_agent.models.llm import LLMProviderType, LLMRewriteRequest


class BaseLLMProvider(abc.ABC):
    """Abstract base for LLM rewrite providers."""

    @abc.abstractmethod
    def rewrite(self, request: LLMRewriteRequest) -> str:
        """Rewrite a single bullet.

        Parameters
        ----------
        request : LLMRewriteRequest
            The rewrite request.

        Returns
        -------
        str
            The rewritten bullet text.
        """
        ...

    @property
    @abc.abstractmethod
    def provider_type(self) -> LLMProviderType:
        ...


class DisabledLLMProvider(BaseLLMProvider):
    """Provider that always raises — LLM rewriting is disabled."""

    @property
    def provider_type(self) -> LLMProviderType:
        return LLMProviderType.DISABLED

    def rewrite(self, request: LLMRewriteRequest) -> str:
        raise RuntimeError(
            "LLM rewriting is disabled. Enable it via options or CLI flags."
        )


class MockLLMProvider(BaseLLMProvider):
    """Deterministic mock provider for testing and local demo.

    Does NOT call any network or external API. Performs safe,
    conservative text polish without inventing new claims.
    """

    @property
    def provider_type(self) -> LLMProviderType:
        return LLMProviderType.MOCK

    def rewrite(self, request: LLMRewriteRequest) -> str:
        """Deterministic conservative polish.

        - Trims extra whitespace
        - Ensures proper capitalization
        - Normalizes sentence structure
        - Does NOT add new facts, metrics, tools, or methods
        """
        text = request.original_text.strip()
        if not text:
            return text

        # Simple conservative polish
        text = " ".join(text.split())  # normalize whitespace

        # Capitalize first letter
        if text and text[0].islower():
            text = text[0].upper() + text[1:]

        # Ensure ends with period if it's a sentence
        if text and text[-1] not in ".!?":
            text = text + "."

        # Use deterministic candidate if provided and safe
        if request.deterministic_candidate_text:
            cand = request.deterministic_candidate_text.strip()
            if cand and len(cand) > 5:
                text = cand

        return text


class ExternalLLMProvider(BaseLLMProvider):
    """Placeholder for future real LLM provider integration.

    Currently raises NotImplementedError with a clear message.
    """

    @property
    def provider_type(self) -> LLMProviderType:
        return LLMProviderType.EXTERNAL

    def rewrite(self, request: LLMRewriteRequest) -> str:
        raise NotImplementedError(
            "External LLM provider is not yet implemented. "
            "Use --llm-provider mock for deterministic local testing, "
            "or leave LLM rewriting disabled."
        )


# ── Provider registry ──────────────────────────────────────────────────

_PROVIDER_REGISTRY: dict[LLMProviderType, type[BaseLLMProvider]] = {
    LLMProviderType.DISABLED: DisabledLLMProvider,
    LLMProviderType.MOCK: MockLLMProvider,
    LLMProviderType.EXTERNAL: ExternalLLMProvider,
}


def get_llm_provider(provider_type: LLMProviderType) -> BaseLLMProvider:
    """Factory: return an LLM provider instance for the given type.

    Parameters
    ----------
    provider_type : LLMProviderType
        Which provider to instantiate.

    Returns
    -------
    BaseLLMProvider
        A provider instance.
    """
    cls = _PROVIDER_REGISTRY.get(provider_type)
    if cls is None:
        raise ValueError(f"Unknown LLM provider type: {provider_type}")
    return cls()
