"""Tests for M16 LLM prompts."""

from __future__ import annotations

from resume_pdf_agent.llm.prompts import build_llm_rewrite_prompt
from resume_pdf_agent.models.llm import LLMRewriteMode, LLMRewriteRequest


def _make_request() -> LLMRewriteRequest:
    return LLMRewriteRequest(
        source_experience_id="exp1",
        original_text="Analyzed data using Python.",
        allowed_facts=["Analyzed data", "Used Python"],
        allowed_keywords=["Python", "data analysis"],
        prohibited_additions=["metrics", "tools"],
    )


class TestBuildLlmRewritePrompt:

    def test_includes_safety_instructions(self):
        req = _make_request()
        prompt = build_llm_rewrite_prompt(req)
        assert "use only allowed facts" in prompt.lower().replace(" ", "") or "use only the allowed facts" in prompt.lower()
        assert "do not add" in prompt.lower()

    def test_includes_no_metrics_instruction(self):
        req = _make_request()
        prompt = build_llm_rewrite_prompt(req)
        assert "metrics" in prompt.lower() or "quantified" in prompt.lower()

    def test_includes_no_tools_instruction(self):
        req = _make_request()
        prompt = build_llm_rewrite_prompt(req)
        assert "tools" in prompt.lower()

    def test_includes_no_exaggeration_instruction(self):
        req = _make_request()
        prompt = build_llm_rewrite_prompt(req)
        assert "exaggerate" in prompt.lower() or "led" in prompt.lower()

    def test_includes_original_text(self):
        req = _make_request()
        prompt = build_llm_rewrite_prompt(req)
        assert "Analyzed data using Python" in prompt
