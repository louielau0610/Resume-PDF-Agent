"""Deterministic bullet construction helpers."""

import re

from resume_pdf_agent.enhancement.safeguards import sanitize_metric_text
from resume_pdf_agent.models import (
    BulletEnhancementMode,
    ExperienceEntry,
    ExperienceType,
    ScreeningCriterion,
)


def normalize_phrase(value: str) -> str:
    """Normalize whitespace for generated phrases."""

    return " ".join(value.strip().split())


def _join_limited(values: list[str], limit: int = 2) -> str:
    return " and ".join(normalize_phrase(value) for value in values[:limit] if value.strip())


def select_action_verb(
    experience_type: ExperienceType,
    methods_used: list[str],
    tools_used: list[str],
) -> str:
    """Select a conservative action verb from source evidence."""

    method_text = " ".join(methods_used).lower()
    tool_text = " ".join(tools_used).lower()
    if "research" in experience_type.value or "literature" in method_text:
        return "Researched"
    if "market" in method_text:
        return "Conducted"
    if any(term in method_text for term in ["analysis", "regression", "model", "evaluation"]):
        return "Analyzed"
    if tools_used and any(term in tool_text for term in ["python", "react", "java", "sql"]):
        return "Built"
    return "Developed" if experience_type == ExperienceType.PROJECT else "Contributed to"


def build_evidence_phrase(experience: ExperienceEntry) -> str:
    """Build object/context phrase from the source experience."""

    if experience.raw_description:
        return normalize_phrase(experience.raw_description)
    if experience.responsibilities:
        return normalize_phrase(experience.responsibilities[0])
    return normalize_phrase(experience.title)


def build_method_phrase(experience: ExperienceEntry) -> str:
    """Build a tools/methods phrase from source evidence."""

    methods = _join_limited(experience.methods_used)
    tools = _join_limited(experience.tools_used)
    if tools and methods:
        return f"using {tools} and {methods}"
    if tools:
        return f"using {tools}"
    if methods:
        return f"with {methods}"
    return ""


def build_outcome_phrase(experience: ExperienceEntry) -> str:
    """Build a conservative outcome phrase from source outcomes."""

    if not experience.outcomes:
        return ""
    return f"to {normalize_phrase(experience.outcomes[0]).rstrip('.')}"


def build_metric_phrase(experience: ExperienceEntry) -> str | None:
    """Build source-supported metric phrase when available."""

    for metric in experience.metrics:
        metric_text = sanitize_metric_text(metric)
        if metric_text:
            return metric_text
    return None


def _trim_words(text: str, limit: int = 35) -> str:
    words = text.split()
    return " ".join(words[:limit])


def build_enhanced_bullet_text(
    experience: ExperienceEntry,
    targeted_criteria: list[ScreeningCriterion] | None = None,
    mode: BulletEnhancementMode = BulletEnhancementMode.CONSERVATIVE_REWRITE,
) -> str | None:
    """Build one conservative enhanced bullet from source-supported evidence."""

    if not any([experience.title, experience.raw_description, experience.responsibilities, experience.tools_used, experience.methods_used]):
        return None

    action = select_action_verb(experience.experience_type, experience.methods_used, experience.tools_used)
    evidence = build_evidence_phrase(experience)
    method = build_method_phrase(experience)
    outcome = build_outcome_phrase(experience)
    metric = build_metric_phrase(experience)

    parts = [action, evidence]
    if method:
        parts.append(method)
    if outcome:
        parts.append(outcome)
    if metric:
        parts.append(f"with user-provided metric {metric}")

    text = normalize_phrase(" ".join(parts))
    text = re.sub(r"\b(improved|optimized|increased|reduced)\b", "supported", text, flags=re.IGNORECASE)
    text = _trim_words(text)
    return text.rstrip(".") + "."
