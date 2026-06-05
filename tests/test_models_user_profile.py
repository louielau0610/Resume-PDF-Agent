import pytest
from pydantic import ValidationError as PydanticValidationError

from resume_pdf_agent.models import ContactInfo, EducationEntry, UserProfile


def test_major_user_profile_models_can_be_imported():
    profile = UserProfile(
        full_name="Alex Chen",
        contact=ContactInfo(email="alex@example.com"),
        education=[
            EducationEntry(
                institution="Example University",
                degree="Bachelor of Science",
                major="Statistics",
            )
        ],
    )

    assert profile.full_name == "Alex Chen"
    assert profile.education[0].core_courses == []


def test_user_profile_rejects_empty_full_name():
    with pytest.raises(PydanticValidationError):
        UserProfile(full_name=" ")


def test_education_rejects_empty_required_fields():
    with pytest.raises(PydanticValidationError):
        EducationEntry(institution="", degree="Bachelor of Science", major="Statistics")

    with pytest.raises(PydanticValidationError):
        EducationEntry(institution="Example University", degree="", major="Statistics")

    with pytest.raises(PydanticValidationError):
        EducationEntry(institution="Example University", degree="Bachelor", major="")
