import pytest
from pydantic import ValidationError as PydanticValidationError

from resume_pdf_agent.models import (
    EvidenceLevel,
    ExperienceEntry,
    ExperienceType,
    MetricStatus,
    ResumeBullet,
    ResumeContent,
    ResumeSection,
    ResumeType,
)


def test_resume_content_models_can_be_imported():
    content = ResumeContent(
        resume_type=ResumeType.DATA_SCIENCE_RESUME,
        experiences=[
            ExperienceEntry(
                experience_id="exp_1",
                experience_type=ExperienceType.PROJECT,
                title="Data Analysis Project",
            )
        ],
        sections=[
            ResumeSection(
                heading="Projects",
                bullets=[
                    ResumeBullet(
                        text="Analyzed public sample data with Python.",
                        evidence_level=EvidenceLevel.USER_PROVIDED,
                        metric_status=MetricStatus.NOT_APPLICABLE,
                    )
                ],
            )
        ],
    )

    assert content.resume_type == ResumeType.DATA_SCIENCE_RESUME
    assert content.sections[0].bullets[0].needs_confirmation is False


def test_resume_bullet_rejects_empty_text():
    with pytest.raises(PydanticValidationError):
        ResumeBullet(
            text="",
            evidence_level=EvidenceLevel.USER_PROVIDED,
            metric_status=MetricStatus.NOT_APPLICABLE,
        )


def test_experience_entry_rejects_empty_identifiers():
    with pytest.raises(PydanticValidationError):
        ExperienceEntry(
            experience_id="",
            experience_type=ExperienceType.PROJECT,
            title="Project",
        )

    with pytest.raises(PydanticValidationError):
        ExperienceEntry(
            experience_id="exp_1",
            experience_type=ExperienceType.PROJECT,
            title="",
        )


def test_resume_section_rejects_empty_heading():
    with pytest.raises(PydanticValidationError):
        ResumeSection(heading="")


def test_unsupported_evidence_level_requires_confirmation():
    bullet = ResumeBullet(
        text="Claim requires evidence.",
        evidence_level=EvidenceLevel.UNSUPPORTED,
        metric_status=MetricStatus.NOT_APPLICABLE,
        needs_confirmation=False,
    )

    assert bullet.needs_confirmation is True


def test_needs_user_confirmation_evidence_level_requires_confirmation():
    bullet = ResumeBullet(
        text="Claim needs user confirmation.",
        evidence_level=EvidenceLevel.NEEDS_USER_CONFIRMATION,
        metric_status=MetricStatus.NOT_APPLICABLE,
        needs_confirmation=False,
    )

    assert bullet.needs_confirmation is True


def test_unsupported_metric_status_requires_confirmation():
    bullet = ResumeBullet(
        text="Claim includes an unsupported metric.",
        evidence_level=EvidenceLevel.USER_PROVIDED,
        metric_status=MetricStatus.UNSUPPORTED,
        needs_confirmation=False,
    )

    assert bullet.needs_confirmation is True
