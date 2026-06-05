"""Simple deterministic criteria profile selector for M2."""

from resume_pdf_agent.criteria.loader import load_all_criteria_profiles
from resume_pdf_agent.models import ResumeType, RoleCriteriaProfile


def _normalize(value: str) -> str:
    return value.lower().replace("_", " ").replace("/", " ")


def _resume_type_value(resume_type: ResumeType | str | None) -> str | None:
    if resume_type is None:
        return None
    if isinstance(resume_type, ResumeType):
        return resume_type.value
    return ResumeType(resume_type).value


def select_criteria_profiles(
    target_role: str | None = None,
    resume_type: ResumeType | str | None = None,
    max_results: int = 3,
) -> list[RoleCriteriaProfile]:
    """Select static criteria profiles with simple keyword and resume type signals.

    This is intentionally small and deterministic. The production resume type
    classifier is planned for a later milestone.
    """

    profiles = load_all_criteria_profiles()
    if max_results <= 0:
        return []

    role_terms = set(_normalize(target_role).split()) if target_role else set()
    resume_type_value = _resume_type_value(resume_type)

    scored_profiles: list[tuple[int, int, RoleCriteriaProfile]] = []
    for index, profile in enumerate(profiles):
        score = 0
        profile_text = _normalize(f"{profile.profile_id} {profile.role_title} {profile.industry or ''}")
        if role_terms:
            score += sum(2 for term in role_terms if term in profile_text)
        if resume_type_value and any(item.value == resume_type_value for item in profile.resume_types):
            score += 3
        scored_profiles.append((score, -index, profile))

    matches = [
        profile
        for score, _order, profile in sorted(scored_profiles, key=lambda item: (-item[0], -item[1]))
        if score > 0
    ]
    if not matches:
        matches = profiles

    return matches[:max_results]
