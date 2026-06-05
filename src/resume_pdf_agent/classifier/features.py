"""Feature extraction helpers for the rule-based resume type classifier."""

from resume_pdf_agent.models import ResumeContent, UserProfile


def normalize_text(value: str) -> str:
    """Normalize text for deterministic keyword matching."""

    return " ".join(value.lower().replace("_", " ").replace("/", " ").split())


def _append_if_present(features: list[str], value: str | None) -> None:
    if value and value.strip():
        if ":" in value:
            source, text = value.split(":", 1)
            if text.strip() and text.strip().lower() != "none":
                features.append(f"{source}:{normalize_text(text)}")
        else:
            features.append(normalize_text(value))


def extract_profile_text_features(user_profile: UserProfile) -> list[str]:
    """Extract text features from a structured user profile."""

    features: list[str] = []
    for target_role in user_profile.target_roles:
        _append_if_present(features, f"target_role:{target_role}")
    for industry in user_profile.target_industries:
        _append_if_present(features, f"target_industry:{industry}")
    for company in user_profile.target_companies:
        _append_if_present(features, f"target_company:{company}")
    for education in user_profile.education:
        _append_if_present(features, f"major:{education.major}")
        for course in education.core_courses:
            _append_if_present(features, f"core_course:{course}")
    for skill_group in user_profile.skills:
        _append_if_present(features, f"skill_category:{skill_group.category}")
        for skill in skill_group.skills:
            _append_if_present(features, f"skill:{skill}")
    for award in user_profile.awards:
        _append_if_present(features, f"award:{award.title}")
        _append_if_present(features, f"award:{award.description}")
    _append_if_present(features, f"additional_text:{user_profile.additional_notes}" if user_profile.additional_notes else None)
    return features


def extract_resume_content_text_features(resume_content: ResumeContent | None) -> list[str]:
    """Extract text features from optional resume content."""

    if resume_content is None:
        return []

    features: list[str] = []
    _append_if_present(features, f"additional_text:{resume_content.summary}" if resume_content.summary else None)
    for experience in resume_content.experiences:
        _append_if_present(features, f"experience_title:{experience.title}")
        _append_if_present(features, f"additional_text:{experience.organization}" if experience.organization else None)
        _append_if_present(features, f"additional_text:{experience.raw_description}" if experience.raw_description else None)
        for responsibility in experience.responsibilities:
            _append_if_present(features, f"additional_text:{responsibility}")
        for tool in experience.tools_used:
            _append_if_present(features, f"skill:{tool}")
        for method in experience.methods_used:
            _append_if_present(features, f"skill:{method}")
        for outcome in experience.outcomes:
            _append_if_present(features, f"additional_text:{outcome}")
    for section in resume_content.sections:
        _append_if_present(features, f"additional_text:{section.heading}")
        for bullet in section.bullets:
            _append_if_present(features, f"additional_text:{bullet.text}")
    return features


def extract_experience_type_features(resume_content: ResumeContent | None) -> list[str]:
    """Extract experience type features from optional resume content."""

    if resume_content is None:
        return []
    return [f"experience_type:{normalize_text(item.experience_type.value)}" for item in resume_content.experiences]
