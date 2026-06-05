"""Prompt construction for M16 LLM-assisted rewriting.

Builds safe prompts that instruct the LLM to rewrite conservatively
without introducing new claims, metrics, or fabricated content.
"""

from __future__ import annotations

from resume_pdf_agent.models.llm import LLMRewriteRequest, LLMRewriteMode


def build_llm_rewrite_prompt(request: LLMRewriteRequest) -> str:
    """Build a safe rewrite prompt for an LLM provider.

    The prompt instructs the LLM to rewrite for clarity while strictly
    limiting what can be added or changed.

    Parameters
    ----------
    request : LLMRewriteRequest
        The rewrite request with original text and constraints.

    Returns
    -------
    str
        A prompt string for the LLM provider.
    """
    mode_instruction = _mode_instruction(request.mode)
    facts = "\n".join(f"- {f}" for f in request.allowed_facts) if request.allowed_facts else "(none provided)"
    keywords = ", ".join(request.allowed_keywords) if request.allowed_keywords else "(none)"
    prohibited = ", ".join(request.prohibited_additions) if request.prohibited_additions else "(none specified)"

    return f"""You are a conservative resume bullet editor. Your ONLY job is to improve clarity, concision, and role alignment.

MODE: {mode_instruction}

ORIGINAL BULLET:
{request.original_text}

ALLOWED FACTS (ONLY use these — do not invent anything beyond this list):
{facts}

ALLOWED KEYWORDS (you may incorporate these naturally if they fit):
{keywords}

PROHIBITED ADDITIONS (DO NOT add any of these):
{prohibited}

SAFETY RULES — YOU MUST FOLLOW ALL OF THESE:
1. Use ONLY the allowed facts above. Do NOT invent new achievements, metrics, tools, methods, or organizations.
2. Do NOT add any numbers, percentages, dollar amounts, or quantified metrics unless they appear in the allowed facts.
3. Do NOT add new tools, technologies, or software names.
4. Do NOT add new methods, methodologies, or frameworks.
5. Do NOT add new organizations, companies, or team names.
6. Do NOT upgrade "assisted", "contributed to", or "participated in" into "led", "owned", "managed", or "spearheaded".
7. Do NOT claim end-to-end ownership unless explicitly stated in the allowed facts.
8. Keep the bullet under 35 words.
9. Keep wording ATS-friendly and professional.
10. Preserve truthfulness — do not exaggerate or embellish.
11. Return ONLY the rewritten bullet text. No explanations, no prefixes, no labels.
12. Do NOT include "I", "my", or first-person pronouns.

REWRITTEN BULLET:"""


def _mode_instruction(mode: LLMRewriteMode) -> str:
    """Return a mode-specific instruction string."""
    instructions = {
        LLMRewriteMode.CLARITY: "Improve clarity and readability without changing meaning.",
        LLMRewriteMode.CONCISE: "Make the bullet more concise while preserving key information.",
        LLMRewriteMode.ATS_ALIGNED: "Align wording with ATS-friendly keywords and structure.",
        LLMRewriteMode.IMPACT_FRAMING: "Frame the bullet to emphasize impact, using only allowed facts.",
        LLMRewriteMode.CONSERVATIVE_POLISH: "Apply minimal conservative polish — fix grammar, improve flow, do not change meaning.",
    }
    return instructions.get(mode, instructions[LLMRewriteMode.CONSERVATIVE_POLISH])
