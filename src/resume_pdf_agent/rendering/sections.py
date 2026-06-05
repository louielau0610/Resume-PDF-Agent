"""Section construction utilities for HTML resume rendering."""

from collections import defaultdict

from resume_pdf_agent.models import (
    BulletEnhancementResult,
    BulletEnhancementStatus,
    HTMLRenderOptions,
    RenderSection,
    RenderSectionItem,
    ResumeContent,
    TemplateSelectionResult,
    UserProfile,
)
from resume_pdf_agent.models.enums import ExperienceType
from resume_pdf_agent.rendering.safety import escape_html_text, is_safe_render_item

SECTION_ALIASES: dict[str, set[str]] = {
    "experience": {"experience", "work experience", "work_experience"},
    "projects": {"projects", "project", "coursework"},
    "research": {"research"},
    "research_experience": {"research experience", "research_experience", "research"},
    "product_experience": {"product experience", "product_experience", "product"},
    "consulting_projects": {"consulting projects", "consulting_projects", "case projects"},
    "design_projects": {"design projects", "design_projects", "portfolio projects"},
    "leadership": {"leadership", "activities"},
    "publications_or_presentations": {
        "publications",
        "presentations",
        "publications or presentations",
        "publications_or_presentations",
    },
    "portfolio": {"portfolio"},
}

EXPERIENCE_SECTION_TYPES: dict[str, set[ExperienceType]] = {
    "experience": {
        ExperienceType.INTERNSHIP,
        ExperienceType.WORK_EXPERIENCE,
        ExperienceType.VOLUNTEER,
        ExperienceType.OTHER,
    },
    "projects": {
        ExperienceType.PROJECT,
        ExperienceType.COURSEWORK,
        ExperienceType.COMPETITION,
    },
    "research": {ExperienceType.RESEARCH},
    "research_experience": {ExperienceType.RESEARCH},
    "product_experience": {
        ExperienceType.PROJECT,
        ExperienceType.INTERNSHIP,
        ExperienceType.WORK_EXPERIENCE,
    },
    "consulting_projects": {
        ExperienceType.PROJECT,
        ExperienceType.COMPETITION,
        ExperienceType.WORK_EXPERIENCE,
    },
    "design_projects": {
        ExperienceType.PROJECT,
        ExperienceType.WORK_EXPERIENCE,
    },
    "leadership": {ExperienceType.LEADERSHIP, ExperienceType.VOLUNTEER},
}


def _text_item(
    text: str,
    source_id: str | None = None,
    source_type: str | None = None,
    needs_confirmation: bool = False,
    risk_flags: list[str] | None = None,
) -> RenderSectionItem:
    return RenderSectionItem(
        text=escape_html_text(text),
        source_id=source_id,
        source_type=source_type,
        needs_confirmation=needs_confirmation,
        risk_flags=risk_flags or [],
    )


def _section_heading_matches(section_heading: str, section_id: str) -> bool:
    normalized = section_heading.strip().lower().replace("-", " ")
    aliases = SECTION_ALIASES.get(section_id, {section_id})
    return normalized in {alias.replace("_", " ") for alias in aliases}


def _items_from_resume_sections(resume_content: ResumeContent, section_id: str) -> list[RenderSectionItem]:
    items: list[RenderSectionItem] = []
    for section in resume_content.sections:
        if not _section_heading_matches(section.heading, section_id):
            continue
        for bullet in section.bullets:
            items.append(
                _text_item(
                    bullet.text,
                    source_id=bullet.source_experience_id,
                    source_type="resume_bullet",
                    needs_confirmation=bullet.needs_confirmation,
                    risk_flags=bullet.risk_flags,
                )
            )
    return items


def _safe_enhanced_items_by_experience(
    bullet_enhancement_result: BulletEnhancementResult | None,
) -> dict[str, list[RenderSectionItem]]:
    grouped: dict[str, list[RenderSectionItem]] = defaultdict(list)
    if bullet_enhancement_result is None:
        return grouped
    for experience_result in bullet_enhancement_result.experience_results:
        for candidate in experience_result.candidates:
            is_usable_status = candidate.status in {
                BulletEnhancementStatus.ENHANCED,
                BulletEnhancementStatus.UNCHANGED,
            }
            if not is_usable_status:
                continue
            if not is_safe_render_item(
                candidate.needs_confirmation,
                candidate.risk_flags,
                include_confirmation_needed=False,
            ):
                continue
            source_id = candidate.source_experience_id or experience_result.experience_id
            grouped[source_id].append(
                _text_item(
                    candidate.enhanced_text,
                    source_id=source_id,
                    source_type="enhanced_bullet_candidate",
                    needs_confirmation=candidate.needs_confirmation,
                    risk_flags=candidate.risk_flags,
                )
            )
    return grouped


def _experience_summary_item(experience) -> RenderSectionItem:
    parts = [experience.title]
    if experience.organization:
        parts.append(experience.organization)
    if experience.start_date or experience.end_date:
        date_range = " - ".join(part for part in [experience.start_date, experience.end_date] if part)
        parts.append(date_range)
    details = (
        experience.responsibilities
        or experience.outcomes
        or experience.methods_used
        or experience.tools_used
        or ([experience.raw_description] if experience.raw_description else [])
    )
    if details:
        parts.append(details[0])
    return _text_item(
        " | ".join(parts),
        source_id=experience.experience_id,
        source_type=experience.experience_type.value,
    )


def _items_from_experiences(
    resume_content: ResumeContent,
    section_id: str,
    enhanced_by_experience: dict[str, list[RenderSectionItem]],
) -> list[RenderSectionItem]:
    allowed_types = EXPERIENCE_SECTION_TYPES.get(section_id, set())
    if not allowed_types:
        return []
    items: list[RenderSectionItem] = []
    used_sources = set()
    for experience in resume_content.experiences:
        if experience.experience_type not in allowed_types:
            continue
        if experience.experience_id in enhanced_by_experience:
            items.extend(enhanced_by_experience[experience.experience_id])
            used_sources.add(experience.experience_id)
    if items:
        return items
    for experience in resume_content.experiences:
        if experience.experience_type in allowed_types and experience.experience_id not in used_sources:
            items.append(_experience_summary_item(experience))
    return items


def _education_items(user_profile: UserProfile) -> list[RenderSectionItem]:
    items: list[RenderSectionItem] = []
    for education in user_profile.education:
        parts = [education.institution, education.degree, education.major]
        if education.start_date or education.end_date:
            parts.append(" - ".join(part for part in [education.start_date, education.end_date] if part))
        if education.gpa:
            parts.append(f"GPA: {education.gpa}")
        if education.core_courses:
            parts.append("Coursework: " + ", ".join(education.core_courses))
        if education.honors:
            parts.append("Honors: " + ", ".join(education.honors))
        items.append(_text_item(" | ".join(parts), source_type="education"))
    return items


def _skill_items(user_profile: UserProfile) -> list[RenderSectionItem]:
    return [
        _text_item(f"{group.category}: {', '.join(group.skills)}", source_type="skill_group")
        for group in user_profile.skills
        if group.skills
    ]


def _award_items(user_profile: UserProfile) -> list[RenderSectionItem]:
    items: list[RenderSectionItem] = []
    for award in user_profile.awards:
        parts = [award.title]
        if award.issuer:
            parts.append(award.issuer)
        if award.date:
            parts.append(award.date)
        if award.description:
            parts.append(award.description)
        items.append(_text_item(" | ".join(parts), source_type="award"))
    return items


def _language_items(user_profile: UserProfile) -> list[RenderSectionItem]:
    return [
        _text_item(f"{language.language}: {language.proficiency}", source_type="language")
        for language in user_profile.languages
    ]


def _portfolio_items(user_profile: UserProfile, resume_content: ResumeContent) -> list[RenderSectionItem]:
    items: list[RenderSectionItem] = []
    if user_profile.contact.portfolio:
        items.append(_text_item(user_profile.contact.portfolio, source_type="portfolio_link"))
    items.extend(_items_from_resume_sections(resume_content, "portfolio"))
    return items


def _section_items(
    section_id: str,
    user_profile: UserProfile,
    resume_content: ResumeContent,
    enhanced_by_experience: dict[str, list[RenderSectionItem]],
) -> list[RenderSectionItem]:
    if section_id == "education":
        return _education_items(user_profile)
    if section_id in {"skills", "technical_skills", "finance_skills"}:
        return _skill_items(user_profile)
    if section_id == "awards":
        return _award_items(user_profile)
    if section_id == "languages":
        return _language_items(user_profile)
    if section_id == "portfolio":
        return _portfolio_items(user_profile, resume_content)
    allowed_types = EXPERIENCE_SECTION_TYPES.get(section_id, set())
    enhanced_items: list[RenderSectionItem] = []
    for experience in resume_content.experiences:
        if experience.experience_type in allowed_types and experience.experience_id in enhanced_by_experience:
            enhanced_items.extend(enhanced_by_experience[experience.experience_id])
    if enhanced_items:
        return enhanced_items
    items = _items_from_resume_sections(resume_content, section_id)
    if items:
        return items
    return _items_from_experiences(resume_content, section_id, enhanced_by_experience)


def _apply_item_limit(
    items: list[RenderSectionItem],
    section_max_items: int | None,
    options: HTMLRenderOptions,
) -> list[RenderSectionItem]:
    limits = [limit for limit in [section_max_items, options.max_items_per_section] if limit is not None]
    if not limits:
        return items
    return items[: min(limits)]


def build_render_sections(
    user_profile: UserProfile,
    resume_content: ResumeContent,
    template_selection_result: TemplateSelectionResult,
    bullet_enhancement_result: BulletEnhancementResult | None = None,
    options: HTMLRenderOptions | None = None,
) -> list[RenderSection]:
    """Build render sections according to selected internal template metadata."""

    render_options = options or HTMLRenderOptions()
    enhanced_by_experience = _safe_enhanced_items_by_experience(bullet_enhancement_result)
    sections: list[RenderSection] = []

    for template_section in template_selection_result.selected_template.sections:
        items = _section_items(
            template_section.section_id,
            user_profile,
            resume_content,
            enhanced_by_experience,
        )
        items = _apply_item_limit(items, template_section.max_items, render_options)
        if items or template_section.required:
            sections.append(
                RenderSection(
                    section_id=template_section.section_id,
                    heading=template_section.heading,
                    items=items,
                    required=template_section.required,
                )
            )
    return sections
