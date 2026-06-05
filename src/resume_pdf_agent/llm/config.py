"""Configuration helpers for M16 LLM-assisted rewriting."""

from __future__ import annotations

import os

from resume_pdf_agent.models.llm import (
    LLMProviderType,
    LLMRewriteMode,
    LLMRewriteOptions,
)


def default_llm_rewrite_options() -> LLMRewriteOptions:
    """Return safe default LLM rewrite options.

    LLM rewriting is disabled by default. All safety flags are enabled.
    """
    return LLMRewriteOptions(
        enabled=False,
        provider=LLMProviderType.DISABLED,
        mode=LLMRewriteMode.CONSERVATIVE_POLISH,
        max_candidates=3,
        require_truthfulness_pass=True,
        require_confirmation_packet_clear=False,
        mark_all_llm_output_needs_confirmation=True,
        allow_new_metrics=False,
        allow_new_tools=False,
        allow_new_methods=False,
        allow_new_organizations=False,
    )


def load_llm_rewrite_options_from_env() -> LLMRewriteOptions:
    """Load LLM rewrite options from environment variables.

    Environment variables (optional):
    - RESUME_AGENT_LLM_ENABLED: "true" or "1" to enable
    - RESUME_AGENT_LLM_PROVIDER: "mock" or "external"

    Returns safe defaults if env vars are absent. Does NOT require
    API keys or network access.
    """
    opts = default_llm_rewrite_options()

    enabled_str = os.environ.get("RESUME_AGENT_LLM_ENABLED", "").lower()
    if enabled_str in ("true", "1", "yes"):
        opts.enabled = True

        provider_str = os.environ.get("RESUME_AGENT_LLM_PROVIDER", "").lower()
        if provider_str == "mock":
            opts.provider = LLMProviderType.MOCK
        elif provider_str == "external":
            opts.provider = LLMProviderType.EXTERNAL

    return opts
