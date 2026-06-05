"""Deterministic constraints for internal template selection."""

from resume_pdf_agent.models import (
    BulletEnhancementResult,
    InternalTemplateProfile,
    ResumeContent,
    RoleCriteriaProfile,
    TemplateDensity,
    UserProfile,
)


def estimate_resume_density(
    resume_content: ResumeContent | None,
    bullet_enhancement_result: BulletEnhancementResult | None = None,
) -> TemplateDensity:
    """Estimate needed template density from current content size."""

    experience_count = len(resume_content.experiences) if resume_content else 0
    section_bullets = sum(len(section.bullets) for section in resume_content.sections) if resume_content else 0
    generated = bullet_enhancement_result.candidates_generated if bullet_enhancement_result else 0
    total = experience_count + section_bullets + generated
    if total >= 10:
        return TemplateDensity.COMPACT
    if total <= 4:
        return TemplateDensity.SPACIOUS
    return TemplateDensity.STANDARD


def has_research_signals(
    resume_content: ResumeContent | None,
    criteria_profile: RoleCriteriaProfile | None = None,
) -> bool:
    """Return true when profile/content indicates research orientation."""

    text_parts = []
    if resume_content:
        text_parts.extend([resume_content.resume_type.value, resume_content.summary or ""])
        for exp in resume_content.experiences:
            text_parts.extend([exp.experience_type.value, exp.title, exp.raw_description or ""])
    if criteria_profile:
        text_parts.extend([criteria_profile.role_title, criteria_profile.industry or ""])
    text = " ".join(text_parts).lower()
    return any(term in text for term in ["research", "lab", "publication", "professor", "cv"])


def has_portfolio_signals(
    user_profile: UserProfile | None = None,
    resume_content: ResumeContent | None = None,
) -> bool:
    """Return true when user/content indicates portfolio or design signals."""

    if user_profile and user_profile.contact.portfolio:
        return True
    text_parts = []
    if user_profile:
        text_parts.extend(user_profile.target_roles + user_profile.target_industries)
        for skills in user_profile.skills:
            text_parts.extend(skills.skills)
    if resume_content:
        text_parts.extend(exp.title for exp in resume_content.experiences)
    text = " ".join(text_parts).lower()
    return "portfolio" in text


def has_project_heavy_signals(resume_content: ResumeContent | None) -> bool:
    """Return true when content has multiple project-like experiences."""

    if resume_content is None:
        return False
    project_count = sum(1 for exp in resume_content.experiences if "project" in exp.experience_type.value.lower() or "project" in exp.title.lower())
    return project_count >= 2 or len(resume_content.experiences) >= 3


def recommended_sections_for_template(
    template: InternalTemplateProfile,
    resume_content: ResumeContent | None = None,
) -> list[str]:
    """Return section IDs recommended for rendering later."""

    sections = [section.section_id for section in template.sections if section.required]
    optional = [section.section_id for section in template.sections if not section.required]
    if resume_content and resume_content.experiences:
        sections.extend(item for item in optional if item in {"projects", "experience", "research", "research_experience"})
    sections.extend(item for item in optional if item not in sections)
    return list(dict.fromkeys(sections))
