from resume_pdf_agent.classifier import classify_resume_type
from resume_pdf_agent.models import EducationEntry, ExportFormat, ResumeType, UserProfile
from resume_pdf_agent.pipeline import run_resume_pipeline


def test_warnings_returned_when_target_roles_empty():
    profile = UserProfile(
        full_name="No Target Role",
        education=[
            EducationEntry(
                institution="Example University",
                degree="Bachelor",
                major="Computer Science",
            )
        ],
    )

    result = classify_resume_type(profile)

    assert any("target_roles is empty" in warning for warning in result.warnings)


def test_warnings_returned_when_resume_content_missing():
    profile = UserProfile(
        full_name="No Content",
        education=[
            EducationEntry(
                institution="Example University",
                degree="Bachelor",
                major="Statistics",
            )
        ],
        target_roles=["Data Science Intern"],
    )

    result = classify_resume_type(profile)

    assert any("resume_content is missing" in warning for warning in result.warnings)


def test_classifier_does_not_mention_hiring_probability_or_internal_access():
    profile = UserProfile(
        full_name="Safe Text",
        education=[
            EducationEntry(
                institution="Example University",
                degree="Bachelor",
                major="Statistics",
            )
        ],
        target_roles=["Data Science Intern"],
    )

    result = classify_resume_type(profile)
    text = " ".join(
        [
            result.explanation,
            " ".join(result.warnings),
            *[signal.reason for score in result.ranked_types for signal in score.signals],
        ]
    ).lower()

    assert "hiring probability" not in text
    assert "offer probability" not in text
    assert "internal screening" not in text
    assert "internal company screening" not in text


def test_pipeline_placeholder_still_includes_resume_type_classification_and_criteria_stages():
    result = run_resume_pipeline({"target_role": "software engineer intern"})

    assert "criteria_selection" in result["stages"]
    assert "resume_type_classification" in result["stages"]
    assert "criteria_aware_content_enhancement" in result["stages"]
    assert "pdf_generation" in result["stages"]
    assert "M10 integrated" in result["message"]


def test_export_format_still_only_includes_pdf():
    assert [item.value for item in ExportFormat] == ["pdf"]


def test_general_student_type_is_available_for_fallback():
    assert ResumeType.GENERAL_STUDENT_RESUME.value == "general_student_resume"
