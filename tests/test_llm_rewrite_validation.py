"""Tests for M16 LLM rewrite validation."""

from __future__ import annotations

from resume_pdf_agent.llm.validation import (
    detect_new_terms,
    extract_numeric_tokens,
    validate_llm_rewrite_candidate,
)
from resume_pdf_agent.models.llm import LLMRewriteOptions, LLMRewriteRequest


class TestExtractNumericTokens:

    def test_extracts_numbers(self):
        tokens = extract_numeric_tokens("Improved by 50%")
        # The function extracts any numeric-like tokens
        assert len(tokens) > 0

    def test_extracts_percentages(self):
        tokens = extract_numeric_tokens("Increased 30% and 15%")
        assert len(tokens) >= 2

    def test_no_numbers(self):
        assert extract_numeric_tokens("No numbers here") == []


class TestDetectNewTerms:

    def test_detects_new_word(self):
        new = detect_new_terms("hello world", "hello world python", [])
        assert "python" in new

    def test_allowed_terms_not_flagged(self):
        new = detect_new_terms("hello", "hello python", ["python"])
        assert "python" not in new


class TestValidateLlmRewriteCandidate:

    def test_rejects_new_numeric_metric(self):
        req = LLMRewriteRequest(
            original_text="Improved performance",
            allowed_facts=["Improved performance"],
        )
        opts = LLMRewriteOptions(allow_new_metrics=False)
        is_valid, warnings, errors = validate_llm_rewrite_candidate(
            req, "Improved performance by 50%", opts,
        )
        assert not is_valid

    def test_rejects_new_percentage(self):
        req = LLMRewriteRequest(
            original_text="Increased efficiency",
            allowed_facts=["Increased efficiency"],
        )
        opts = LLMRewriteOptions(allow_new_metrics=False)
        is_valid, warnings, errors = validate_llm_rewrite_candidate(
            req, "Increased efficiency by 30%", opts,
        )
        assert not is_valid

    def test_warns_on_leadership_inflation(self):
        req = LLMRewriteRequest(
            original_text="Contributed to the project",
            allowed_facts=["Contributed to project"],
        )
        opts = LLMRewriteOptions()
        is_valid, warnings, errors = validate_llm_rewrite_candidate(
            req, "Spearheaded the project end-to-end", opts,
        )
        assert len(warnings) > 0 or not is_valid

    def test_accepts_safe_rewrite(self):
        req = LLMRewriteRequest(
            original_text="Analyzed data using Python",
            allowed_facts=["Analyzed data", "Used Python"],
        )
        opts = LLMRewriteOptions()
        is_valid, warnings, errors = validate_llm_rewrite_candidate(
            req, "Analyzed data using Python.", opts,
        )
        assert is_valid

    def test_rejects_new_tool(self):
        req = LLMRewriteRequest(
            original_text="Analyzed data",
            allowed_facts=["Analyzed data"],
        )
        opts = LLMRewriteOptions(allow_new_tools=False)
        is_valid, warnings, errors = validate_llm_rewrite_candidate(
            req, "Analyzed data using Docker and Kubernetes", opts,
        )
        assert not is_valid

    def test_empty_text_rejected(self):
        req = LLMRewriteRequest(original_text="test")
        opts = LLMRewriteOptions()
        is_valid, warnings, errors = validate_llm_rewrite_candidate(req, "", opts)
        assert not is_valid
