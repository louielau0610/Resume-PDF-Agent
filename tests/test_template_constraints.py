from resume_pdf_agent.models import (
    ContactInfo,
    ExperienceEntry,
    ExperienceType,
    ResumeContent,
    ResumeType,
    SkillGroup,
    UserProfile,
)
from resume_pdf_agent.templates.constraints import (
    estimate_resume_density,
    has_portfolio_signals,
    has_project_heavy_signals,
    has_research_signals,
    recommended_sections_for_template,
)
from resume_pdf_agent.templates.registry import load_template_profile


def test_template_constraints_detect_research_portfolio_and_project_signals():
    research_content = ResumeContent(
        resume_type=ResumeType.RESEARCH_CV,
        experiences=[
            ExperienceEntry(
                experience_id="exp_research",
                experience_type=ExperienceType.RESEARCH,
                title="Lab Research Project",
            )
        ],
    )
    portfolio_profile = UserProfile(
        full_name="Designer",
        contact=ContactInfo(portfolio="https://portfolio.local"),
        skills=[SkillGroup(category="Design", skills=["Figma", "UX"])],
    )
    project_heavy = ResumeContent(
        resume_type=ResumeType.TECHNICAL_RESUME,
        experiences=[
            ExperienceEntry(experience_id="p1", experience_type=ExperienceType.PROJECT, title="Project One"),
            ExperienceEntry(experience_id="p2", experience_type=ExperienceType.PROJECT, title="Project Two"),
        ],
    )

    assert has_research_signals(research_content)
    assert has_portfolio_signals(portfolio_profile)
    assert has_project_heavy_signals(project_heavy)


def test_density_and_recommended_sections_are_deterministic():
    template = load_template_profile("ats_student_basic")
    content = ResumeContent(
        resume_type=ResumeType.GENERAL_STUDENT_RESUME,
        experiences=[ExperienceEntry(experience_id="exp", experience_type=ExperienceType.PROJECT, title="Project")],
    )

    assert estimate_resume_density(content).value in {"spacious", "standard", "compact"}
    sections = recommended_sections_for_template(template, content)
    assert "education" in sections
    assert sections
