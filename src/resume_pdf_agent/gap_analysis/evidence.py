"""Deterministic candidate evidence extraction for gap analysis."""

import re
from dataclasses import dataclass, field

from resume_pdf_agent.models import ResumeContent, UserProfile


def normalize_text(value: str) -> str:
    """Normalize text for simple deterministic matching."""

    lowered = value.lower()
    cleaned = re.sub(r"[^a-z0-9+#.%/-]+", " ", lowered)
    return " ".join(cleaned.split())


def _keywords_from_text(text: str) -> list[str]:
    tokens = [token for token in normalize_text(text).split() if len(token) > 1]
    return list(dict.fromkeys(tokens))


@dataclass(frozen=True)
class EvidenceItem:
    """One searchable evidence item extracted from candidate data."""

    source_type: str
    source_id: str | None
    text: str
    normalized_text: str
    keywords: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class CandidateEvidenceBundle:
    """Aggregated candidate evidence for criterion matching."""

    items: list[EvidenceItem]
    all_text: str
    normalized_all_text: str


def _make_item(source_type: str, text: str | None, source_id: str | None = None) -> EvidenceItem | None:
    if not text or not text.strip():
        return None
    normalized = normalize_text(text)
    if not normalized:
        return None
    return EvidenceItem(
        source_type=source_type,
        source_id=source_id,
        text=text,
        normalized_text=normalized,
        keywords=_keywords_from_text(text),
    )


def _append(items: list[EvidenceItem], source_type: str, text: str | None, source_id: str | None = None) -> None:
    item = _make_item(source_type, text, source_id)
    if item is not None:
        items.append(item)


def extract_user_profile_evidence(user_profile: UserProfile) -> list[EvidenceItem]:
    """Extract searchable evidence from user profile fields.

    The user's full name is intentionally excluded from match evidence.
    """

    items: list[EvidenceItem] = []
    for role in user_profile.target_roles:
        _append(items, "target_role", role)
    for industry in user_profile.target_industries:
        _append(items, "target_industry", industry)
    for education in user_profile.education:
        _append(items, "education_institution", education.institution)
        _append(items, "education_degree", education.degree)
        _append(items, "education_major", education.major)
        for course in education.core_courses:
            _append(items, "core_course", course)
        for honor in education.honors:
            _append(items, "honor", honor)
    for skill_group in user_profile.skills:
        _append(items, "skill_group", skill_group.category)
        for skill in skill_group.skills:
            _append(items, "skill", skill)
    for language in user_profile.languages:
        _append(items, "language", f"{language.language} {language.proficiency}")
    for award in user_profile.awards:
        _append(items, "award", award.title)
        _append(items, "award", award.description)
    _append(items, "additional_note", user_profile.additional_notes)
    return items


def extract_resume_content_evidence(resume_content: ResumeContent | None) -> list[EvidenceItem]:
    """Extract searchable evidence from optional structured resume content."""

    if resume_content is None:
        return []

    items: list[EvidenceItem] = []
    _append(items, "resume_type", resume_content.resume_type.value)
    _append(items, "summary", resume_content.summary)
    for experience in resume_content.experiences:
        source_id = experience.experience_id
        _append(items, "experience_title", experience.title, source_id)
        _append(items, "experience_type", experience.experience_type.value, source_id)
        _append(items, "experience_organization", experience.organization, source_id)
        _append(items, "raw_description", experience.raw_description, source_id)
        for responsibility in experience.responsibilities:
            _append(items, "responsibility", responsibility, source_id)
        for tool in experience.tools_used:
            _append(items, "tool", tool, source_id)
        for method in experience.methods_used:
            _append(items, "method", method, source_id)
        for outcome in experience.outcomes:
            _append(items, "outcome", outcome, source_id)
        for metric in experience.metrics:
            _append(items, "metric", " ".join(filter(None, [metric.name, metric.value, metric.unit, metric.context])), source_id)
        for note in experience.evidence_notes:
            _append(items, "evidence_note", note, source_id)
    for section in resume_content.sections:
        _append(items, "section_heading", section.heading)
        for bullet in section.bullets:
            _append(items, "resume_bullet", bullet.text, bullet.source_experience_id)
            for criterion_id in bullet.targeted_criteria_ids:
                _append(items, "targeted_criterion_id", criterion_id, bullet.source_experience_id)
            for risk_flag in bullet.risk_flags:
                _append(items, "risk_flag", risk_flag, bullet.source_experience_id)
    return items


def extract_candidate_evidence(
    user_profile: UserProfile,
    resume_content: ResumeContent | None = None,
) -> CandidateEvidenceBundle:
    """Extract and aggregate candidate evidence from profile and resume content."""

    items = [
        *extract_user_profile_evidence(user_profile),
        *extract_resume_content_evidence(resume_content),
    ]
    all_text = " ".join(item.text for item in items)
    return CandidateEvidenceBundle(
        items=items,
        all_text=all_text,
        normalized_all_text=normalize_text(all_text),
    )
