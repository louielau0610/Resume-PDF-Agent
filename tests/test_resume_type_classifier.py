from resume_pdf_agent.classifier import classify_resume_type
from resume_pdf_agent.criteria import load_criteria_profile
from resume_pdf_agent.models import (
    AwardEntry,
    EducationEntry,
    ExperienceEntry,
    ExperienceType,
    ResumeContent,
    ResumeType,
    SkillGroup,
    UserProfile,
)
from resume_pdf_agent.sample_data import SAMPLE_RESUME_CONTENT, SAMPLE_USER_PROFILE


def _profile(target_role: str, major: str, skills: list[str], courses: list[str] | None = None) -> UserProfile:
    return UserProfile(
        full_name="Test Student",
        education=[
            EducationEntry(
                institution="Example University",
                degree="Bachelor",
                major=major,
                core_courses=courses or [],
            )
        ],
        target_roles=[target_role],
        target_industries=[],
        skills=[SkillGroup(category="Skills", skills=skills)],
    )


def _content(
    resume_type: ResumeType,
    title: str,
    experience_type: ExperienceType = ExperienceType.PROJECT,
    tools: list[str] | None = None,
    methods: list[str] | None = None,
) -> ResumeContent:
    return ResumeContent(
        resume_type=resume_type,
        experiences=[
            ExperienceEntry(
                experience_id="exp_1",
                experience_type=experience_type,
                title=title,
                tools_used=tools or [],
                methods_used=methods or [],
            )
        ],
    )


def test_classify_resume_type_can_be_imported():
    assert callable(classify_resume_type)


def test_data_science_sample_profile_classifies_as_data_science():
    result = classify_resume_type(SAMPLE_USER_PROFILE, SAMPLE_RESUME_CONTENT)

    assert result.ranked_types[0].resume_type == ResumeType.DATA_SCIENCE_RESUME
    assert result.primary_resume_type == ResumeType.DATA_SCIENCE_RESUME


def test_software_engineering_profile_classifies_as_technical_resume():
    result = classify_resume_type(
        _profile(
            "Software Engineering Intern",
            "Computer Science",
            ["Java", "Git", "React", "Docker"],
            ["Data Structures", "Algorithms"],
        ),
        _content(ResumeType.TECHNICAL_RESUME, "Backend API Project", tools=["Java", "Git"]),
    )

    assert result.primary_resume_type == ResumeType.TECHNICAL_RESUME


def test_finance_profile_classifies_as_finance_business_resume():
    result = classify_resume_type(
        _profile(
            "Finance Intern",
            "Finance",
            ["Excel", "Financial Modeling", "Valuation"],
            ["Accounting", "Corporate Finance"],
        ),
        _content(ResumeType.FINANCE_BUSINESS_RESUME, "Equity Research Valuation Project"),
    )

    assert result.primary_resume_type == ResumeType.FINANCE_BUSINESS_RESUME


def test_consulting_profile_classifies_as_consulting_resume():
    result = classify_resume_type(
        _profile(
            "Consulting Intern",
            "Business",
            ["Market Sizing", "Presentation", "Business Analysis"],
        ),
        _content(ResumeType.CONSULTING_RESUME, "Strategy Case Competition"),
    )

    assert result.primary_resume_type == ResumeType.CONSULTING_RESUME


def test_research_profile_classifies_as_research_cv():
    result = classify_resume_type(
        _profile(
            "Research Assistant",
            "Biology",
            ["Literature Review", "Experiment", "Academic Writing"],
        ),
        _content(
            ResumeType.RESEARCH_CV,
            "Lab Research Assistant Project",
            experience_type=ExperienceType.RESEARCH,
        ),
    )

    assert result.primary_resume_type == ResumeType.RESEARCH_CV


def test_product_manager_profile_classifies_as_product_manager_resume():
    result = classify_resume_type(
        _profile(
            "Product Manager Intern",
            "Information Systems",
            ["User Research", "PRD", "Roadmap", "Metrics"],
        ),
        _content(ResumeType.PRODUCT_MANAGER_RESUME, "MVP Prototype Product Project"),
    )

    assert result.primary_resume_type == ResumeType.PRODUCT_MANAGER_RESUME


def test_design_portfolio_profile_classifies_as_design_portfolio_resume():
    result = classify_resume_type(
        _profile(
            "UX Design Intern",
            "Design",
            ["Figma", "Visual Design", "Interaction Design", "Typography"],
        ),
        _content(ResumeType.DESIGN_PORTFOLIO_RESUME, "Portfolio UX UI Design Project"),
    )

    assert result.primary_resume_type == ResumeType.DESIGN_PORTFOLIO_RESUME


def test_weak_generic_student_profile_falls_back_to_general_student():
    profile = UserProfile(
        full_name="Generic Student",
        education=[
            EducationEntry(
                institution="Example University",
                degree="Bachelor",
                major="Undeclared",
            )
        ],
        awards=[AwardEntry(title="Campus Volunteer Recognition")],
    )

    result = classify_resume_type(profile)

    assert result.primary_resume_type == ResumeType.GENERAL_STUDENT_RESUME
    assert result.confidence < 0.5


def test_criteria_profiles_can_influence_classification():
    profile = UserProfile(
        full_name="Criteria Only",
        education=[
            EducationEntry(
                institution="Example University",
                degree="Bachelor",
                major="Interdisciplinary Studies",
            )
        ],
        target_roles=["Intern"],
    )

    result = classify_resume_type(
        profile,
        criteria_profiles=[load_criteria_profile("product_manager_intern")],
    )

    assert result.primary_resume_type == ResumeType.PRODUCT_MANAGER_RESUME


def test_max_ranked_types_is_respected_and_scores_are_sorted():
    result = classify_resume_type(
        _profile("Data Science Intern", "Statistics", ["Python", "SQL", "pandas"]),
        SAMPLE_RESUME_CONTENT,
        max_ranked_types=2,
    )

    assert len(result.ranked_types) <= 2
    scores = [item.score for item in result.ranked_types]
    assert scores == sorted(scores, reverse=True)


def test_confidence_and_primary_rank_invariants():
    result = classify_resume_type(SAMPLE_USER_PROFILE, SAMPLE_RESUME_CONTENT)

    assert 0.0 <= result.confidence <= 1.0
    assert result.primary_resume_type in {item.resume_type for item in result.ranked_types}
    assert result.explanation.strip()
