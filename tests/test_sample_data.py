from resume_pdf_agent.models import ResumeContent, RoleCriteriaProfile, UserProfile
from resume_pdf_agent.pipeline import run_resume_pipeline
from resume_pdf_agent.sample_data import (
    SAMPLE_CRITERIA_PROFILE,
    SAMPLE_RESUME_CONTENT,
    SAMPLE_USER_PROFILE,
)


def test_sample_user_profile_validates():
    assert isinstance(SAMPLE_USER_PROFILE, UserProfile)
    assert SAMPLE_USER_PROFILE.target_roles == ["Data Science Intern"]


def test_sample_resume_content_validates():
    assert isinstance(SAMPLE_RESUME_CONTENT, ResumeContent)
    assert len(SAMPLE_RESUME_CONTENT.experiences) >= 2


def test_sample_criteria_profile_validates():
    assert isinstance(SAMPLE_CRITERIA_PROFILE, RoleCriteriaProfile)
    assert SAMPLE_CRITERIA_PROFILE.role_title == "Data Science Intern"


def test_role_criteria_profile_sample_does_not_claim_internal_access():
    text = " ".join(
        [
            SAMPLE_CRITERIA_PROFILE.notes or "",
            *[
                " ".join(
                    [
                        criterion.name,
                        criterion.description,
                        criterion.source.notes or "",
                    ]
                )
                for criterion in SAMPLE_CRITERIA_PROFILE.criteria
            ],
        ]
    ).lower()

    assert "internal company screening algorithm" not in text
    assert "internal company screening algorithms" not in text
    assert "internal company screening standard" in text
    assert "not an internal company screening standard" in text


def test_placeholder_pipeline_includes_criteria_aware_stages():
    result = run_resume_pipeline({"target_role": "Data Science Intern"})

    assert result["status"] == "skeleton"
    assert "criteria_selection" in result["stages"]
    assert "gap_analysis" in result["stages"]
    assert "criteria_aware_content_enhancement" in result["stages"]
    assert "html_rendering" in result["stages"]
    assert "pdf_generation" in result["stages"]
    assert result["supported_export_formats"] == ["pdf"]
    assert "M7 deterministic internal template selector" in result["message"]
