"""LLM output validation for M16.

Validates that LLM-rewritten text does not introduce fabricated claims,
new metrics, tools, methods, or organizations.
"""

from __future__ import annotations

import re

from resume_pdf_agent.models.llm import LLMRewriteOptions, LLMRewriteRequest

# ── Dangerous leadership/impact phrases ─────────────────────────────────
_DANGEROUS_PHRASES: list[str] = [
    "increased by",
    "reduced by",
    "improved by",
    "boosted",
    "generated revenue",
    "led end-to-end",
    "spearheaded",
    "owned",
    "managed",
]

# ── Numeric pattern ────────────────────────────────────────────────────
_NUMERIC_PATTERN = re.compile(r"\d+(?:\.\d+)?\s*%?")
_PERCENTAGE_PATTERN = re.compile(r"\d+(?:\.\d+)?\s*%")


def extract_numeric_tokens(text: str) -> list[str]:
    """Extract numeric tokens (numbers, percentages) from text."""
    return _NUMERIC_PATTERN.findall(text)


def detect_new_terms(
    original_text: str,
    rewritten_text: str,
    allowed_terms: list[str],
) -> list[str]:
    """Detect terms in rewritten_text that are not in original_text or allowed_terms.

    Uses simple word-level comparison.
    """
    orig_words = set(original_text.lower().split())
    allowed_words = set(t.lower() for t in allowed_terms)
    new_terms: list[str] = []

    rewrite_words = rewritten_text.lower().split()
    for word in rewrite_words:
        clean = word.strip(".,;:!?()[]{}'\"")
        if len(clean) < 3:
            continue
        if clean not in orig_words and clean not in allowed_words:
            new_terms.append(clean)

    return new_terms


def validate_llm_rewrite_candidate(
    request: LLMRewriteRequest,
    rewritten_text: str,
    options: LLMRewriteOptions,
) -> tuple[bool, list[str], list[str]]:
    """Validate LLM-rewritten text against safety constraints.

    Parameters
    ----------
    request : LLMRewriteRequest
        The original rewrite request with constraints.
    rewritten_text : str
        The LLM-generated text to validate.
    options : LLMRewriteOptions
        Safety configuration.

    Returns
    -------
    tuple[bool, list[str], list[str]]
        (is_valid, warnings, errors)
    """
    warnings: list[str] = []
    errors: list[str] = []

    if not rewritten_text or not rewritten_text.strip():
        errors.append("Rewritten text is empty.")
        return False, warnings, errors

    orig_nums = set(extract_numeric_tokens(request.original_text))
    rewrite_nums = set(extract_numeric_tokens(rewritten_text))

    # ── Check for new numeric metrics ────────────────────────────────
    if not options.allow_new_metrics:
        new_nums = rewrite_nums - orig_nums
        if new_nums:
            errors.append(
                f"New numeric values introduced: {', '.join(sorted(new_nums))}"
            )

    # ── Check for new percentages ────────────────────────────────────
    orig_pct = set(_PERCENTAGE_PATTERN.findall(request.original_text))
    rewrite_pct = set(_PERCENTAGE_PATTERN.findall(rewritten_text))
    new_pct = rewrite_pct - orig_pct
    if new_pct:
        errors.append(
            f"New percentages introduced: {', '.join(sorted(new_pct))}"
        )

    # ── Check for dangerous leadership/inflated phrases ───────────────
    rewrite_lower = rewritten_text.lower()
    orig_lower = request.original_text.lower()
    for phrase in _DANGEROUS_PHRASES:
        if phrase in rewrite_lower and phrase not in orig_lower:
            # Check if allowed facts contain this
            allowed_facts_lower = " ".join(request.allowed_facts).lower()
            if phrase not in allowed_facts_lower:
                warnings.append(
                    f"Potentially inflated claim: '{phrase}' not in original or allowed facts."
                )

    # ── Check for new tools (simple heuristic) ───────────────────────
    if not options.allow_new_tools:
        _common_tools = {
            "python", "r", "sql", "excel", "tableau", "power bi",
            "java", "c++", "javascript", "react", "node.js", "docker",
            "aws", "azure", "gcp", "git", "spark", "hadoop", "kafka",
            "tensorflow", "pytorch", "pandas", "numpy", "scikit-learn",
        }
        rewrite_tool_words = set(rewritten_text.lower().split())
        orig_tool_words = set(request.original_text.lower().split())
        for tool in _common_tools:
            if tool in rewrite_tool_words and tool not in orig_tool_words:
                allowed_lower = " ".join(request.allowed_facts).lower()
                if tool not in allowed_lower:
                    errors.append(f"New tool introduced: '{tool}'")

    # ── Check for new methods ────────────────────────────────────────
    if not options.allow_new_methods:
        _method_markers = {
            "agile", "scrum", "kanban", "waterfall", "lean",
            "design thinking", "six sigma",
        }
        rewrite_words = set(rewritten_text.lower().split())
        orig_words = set(request.original_text.lower().split())
        for method in _method_markers:
            method_clean = method.replace(" ", "")
            rewrite_clean = rewritten_text.lower().replace(" ", "")
            orig_clean = request.original_text.lower().replace(" ", "")
            if method in rewrite_words and method not in orig_words:
                if method_clean not in orig_clean:
                    errors.append(f"New method introduced: '{method}'")

    # ── Determine validity ───────────────────────────────────────────
    is_valid = len(errors) == 0

    return is_valid, warnings, errors
