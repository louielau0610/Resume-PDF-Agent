from resume_pdf_agent.classifier import classify_resume_type
from resume_pdf_agent.models import (
    ContactInfo,
    EducationEntry,
    ExperienceEntry,
    ExperienceType,
    ResumeContent,
    ResumeType,
    SkillGroup,
    UserProfile,
)
from resume_pdf_agent.templates import select_internal_template


def _profile(role: str, major: str, skills: list[str] | None = None, portfolio: str | None = None):
    return UserProfile(
        full_name="Template User",
        contact=ContactInfo(portfolio=portfolio),
        education=[EducationEntry(institution="Example University", degree="Bachelor", major=major)],
        target_roles=[role],
        skills=[SkillGroup(category="Skills", skills=skills or [])],
    )


def _content(resume_type: ResumeType, title: str, experience_type: ExperienceType = ExperienceType.PROJECT):
    return ResumeContent(
        resume_type=resume_type,
        experiences=[ExperienceEntry(experience_id="exp_1", experience_type=experience_type, title=title)],
    )


def _ranked_ids(result):
    return [item.template_id for item in result.ranked_templates]


def test_select_internal_template_can_be_imported():
    assert callable(select_internal_template)


def test_data_science_selects_or_ranks_data_science_template_highly():
    profile = _profile("Data Science Intern", "Statistics", ["Python", "SQL"])
    content = _content(ResumeType.DATA_SCIENCE_RESUME, "Machine Learning Project")
    result = select_internal_template(profile, content, classify_resume_type(profile, content))

    assert "data_science_technical" in _ranked_ids(result)


def test_software_engineering_selects_or_ranks_swe_template_highly():
    profile = _profile("Software Engineering Intern", "Computer Science", ["Java", "Git"])
    content = _content(ResumeType.TECHNICAL_RESUME, "Backend API Project")
    result = select_internal_template(profile, content, classify_resume_type(profile, content))

    assert "software_engineering_technical" in _ranked_ids(result)


def test_finance_consulting_research_product_templates_rank_highly():
    cases = [
        ("Finance Intern", "Finance", ResumeType.FINANCE_BUSINESS_RESUME, "Valuation Project", ExperienceType.PROJECT, "finance_business"),
        ("Consulting Intern", "Business", ResumeType.CONSULTING_RESUME, "Strategy Case", ExperienceType.PROJECT, "consulting_business"),
        ("Research Assistant", "Biology", ResumeType.RESEARCH_CV, "Lab Research", ExperienceType.RESEARCH, "research_cv"),
        ("Product Manager Intern", "Information Systems", ResumeType.PRODUCT_MANAGER_RESUME, "MVP Product Project", ExperienceType.PROJECT, "product_manager"),
    ]
    for role, major, resume_type, title, exp_type, expected in cases:
        profile = _profile(role, major)
        content = _content(resume_type, title, exp_type)
        result = select_internal_template(profile, content, classify_resume_type(profile, content))
        assert expected in _ranked_ids(result)


def test_design_portfolio_requires_portfolio_signal_to_rank_highly():
    no_portfolio = _profile("UX Design Intern", "Design", ["Figma", "UX"])
    no_portfolio_content = _content(ResumeType.DESIGN_PORTFOLIO_RESUME, "UX Design Project")
    without = select_internal_template(no_portfolio, no_portfolio_content, classify_resume_type(no_portfolio, no_portfolio_content))

    with_portfolio = _profile("UX Design Intern", "Design", ["Figma", "UX"], portfolio="https://portfolio.local")
    with_content = _content(ResumeType.DESIGN_PORTFOLIO_RESUME, "UX Design Portfolio Project")
    with_result = select_internal_template(with_portfolio, with_content, classify_resume_type(with_portfolio, with_content))

    assert "design_portfolio_light" not in _ranked_ids(without)[:1]
    assert "design_portfolio_light" in _ranked_ids(with_result)


def test_generic_weak_profile_falls_back_to_ats_student_basic():
    profile = UserProfile(
        full_name="Generic",
        education=[EducationEntry(institution="Example University", degree="Bachelor", major="Undeclared")],
    )
    result = select_internal_template(user_profile=profile)

    assert result.selected_template_id == "ats_student_basic"


def test_ranked_templates_sorted_and_limited_with_selected_present():
    profile = _profile("Data Science Intern", "Statistics", ["Python"])
    content = _content(ResumeType.DATA_SCIENCE_RESUME, "Data Project")
    result = select_internal_template(profile, content, classify_resume_type(profile, content), max_ranked_templates=2)

    assert len(result.ranked_templates) <= 2
    assert [item.score for item in result.ranked_templates] == sorted([item.score for item in result.ranked_templates], reverse=True)
    assert result.selected_template_id in {item.template_id for item in result.ranked_templates}
    assert result.recommended_sections
