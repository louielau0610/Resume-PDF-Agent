from resume_pdf_agent.gap_analysis import extract_candidate_evidence
from resume_pdf_agent.models import (
    EducationEntry,
    EvidenceLevel,
    ExperienceEntry,
    ExperienceType,
    MetricStatus,
    ResumeBullet,
    ResumeContent,
    ResumeSection,
    ResumeType,
    SkillGroup,
    UserProfile,
)


def test_extract_candidate_evidence_extracts_profile_and_resume_fields():
    profile = UserProfile(
        full_name="Private Name",
        education=[
            EducationEntry(
                institution="Example University",
                degree="Bachelor",
                major="Statistics",
                core_courses=["Probability", "Database Systems"],
            )
        ],
        target_roles=["Data Science Intern"],
        target_industries=["Analytics"],
        skills=[SkillGroup(category="Programming", skills=["Python", "SQL"])],
    )
    content = ResumeContent(
        resume_type=ResumeType.DATA_SCIENCE_RESUME,
        experiences=[
            ExperienceEntry(
                experience_id="exp_ml",
                experience_type=ExperienceType.PROJECT,
                title="Machine Learning Project",
                tools_used=["pandas"],
                methods_used=["Model evaluation"],
                outcomes=["Prepared a project report."],
            )
        ],
        sections=[
            ResumeSection(
                heading="Projects",
                bullets=[
                    ResumeBullet(
                        text="Built a Python model evaluation notebook.",
                        evidence_level=EvidenceLevel.USER_PROVIDED,
                        metric_status=MetricStatus.NOT_APPLICABLE,
                    )
                ],
            )
        ],
    )

    bundle = extract_candidate_evidence(profile, content)
    text = bundle.normalized_all_text

    assert "data science intern" in text
    assert "statistics" in text
    assert "probability" in text
    assert "python" in text
    assert "machine learning project" in text
    assert "pandas" in text
    assert "model evaluation" in text
    assert "prepared a project report" in text
    assert "built a python model evaluation notebook" in text


def test_extract_candidate_evidence_does_not_use_full_name_as_match_evidence():
    profile = UserProfile(full_name="Unique Private Name")

    bundle = extract_candidate_evidence(profile)

    assert "unique private name" not in bundle.normalized_all_text
