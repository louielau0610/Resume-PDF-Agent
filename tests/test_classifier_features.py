from resume_pdf_agent.classifier import (
    extract_experience_type_features,
    extract_profile_text_features,
    extract_resume_content_text_features,
    normalize_text,
)
from resume_pdf_agent.models import (
    EducationEntry,
    ExperienceEntry,
    ExperienceType,
    ResumeContent,
    ResumeType,
    SkillGroup,
    UserProfile,
)


def test_normalize_text_is_lowercase_and_compact():
    assert normalize_text("  Data_Science / Intern  ") == "data science intern"


def test_extract_profile_text_features_includes_expected_sources():
    profile = UserProfile(
        full_name="Alex Chen",
        education=[
            EducationEntry(
                institution="Example University",
                degree="BS",
                major="Computer Science",
                core_courses=["Data Structures"],
            )
        ],
        target_roles=["Software Engineering Intern"],
        target_industries=["Technology"],
        skills=[SkillGroup(category="Programming", skills=["Python", "Git"])],
    )

    features = extract_profile_text_features(profile)

    assert "target_role:software engineering intern" in features
    assert "major:computer science" in features
    assert "core_course:data structures" in features
    assert "skill:python" in features
    assert "skill:git" in features


def test_extract_resume_content_features_include_titles_tools_methods_and_types():
    content = ResumeContent(
        resume_type=ResumeType.TECHNICAL_RESUME,
        experiences=[
            ExperienceEntry(
                experience_id="exp_api",
                experience_type=ExperienceType.PROJECT,
                title="Backend API Project",
                tools_used=["FastAPI", "Docker"],
                methods_used=["Testing", "Debugging"],
            )
        ],
    )

    text_features = extract_resume_content_text_features(content)
    type_features = extract_experience_type_features(content)

    assert "experience_title:backend api project" in text_features
    assert "skill:fastapi" in text_features
    assert "skill:testing" in text_features
    assert "experience_type:project" in type_features
