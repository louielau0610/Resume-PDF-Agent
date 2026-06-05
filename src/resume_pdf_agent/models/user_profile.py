"""User profile schemas."""

from pydantic import BaseModel, Field, field_validator


def _validate_non_empty(value: str, field_name: str) -> str:
    if not value or not value.strip():
        raise ValueError(f"{field_name} cannot be empty")
    return value


class ContactInfo(BaseModel):
    """Basic user contact information."""

    email: str | None = None
    phone: str | None = None
    location: str | None = None
    linkedin: str | None = None
    github: str | None = None
    portfolio: str | None = None


class EducationEntry(BaseModel):
    """Education history entry."""

    institution: str
    degree: str
    major: str
    start_date: str | None = None
    end_date: str | None = None
    gpa: str | None = None
    core_courses: list[str] = Field(default_factory=list)
    honors: list[str] = Field(default_factory=list)

    @field_validator("institution", "degree", "major")
    @classmethod
    def required_text_fields_cannot_be_empty(cls, value: str, info):
        return _validate_non_empty(value, info.field_name)


class SkillGroup(BaseModel):
    """A group of related skills."""

    category: str
    skills: list[str] = Field(default_factory=list)

    @field_validator("category")
    @classmethod
    def category_cannot_be_empty(cls, value: str) -> str:
        return _validate_non_empty(value, "category")


class LanguageSkill(BaseModel):
    """Language and proficiency pair."""

    language: str
    proficiency: str

    @field_validator("language", "proficiency")
    @classmethod
    def required_text_fields_cannot_be_empty(cls, value: str, info):
        return _validate_non_empty(value, info.field_name)


class AwardEntry(BaseModel):
    """Award, honor, or recognition entry."""

    title: str
    issuer: str | None = None
    date: str | None = None
    description: str | None = None

    @field_validator("title")
    @classmethod
    def title_cannot_be_empty(cls, value: str) -> str:
        return _validate_non_empty(value, "title")


class UserProfile(BaseModel):
    """Structured user profile for future resume generation stages."""

    full_name: str
    contact: ContactInfo = Field(default_factory=ContactInfo)
    education: list[EducationEntry] = Field(default_factory=list)
    target_roles: list[str] = Field(default_factory=list)
    target_companies: list[str] = Field(default_factory=list)
    target_industries: list[str] = Field(default_factory=list)
    skills: list[SkillGroup] = Field(default_factory=list)
    languages: list[LanguageSkill] = Field(default_factory=list)
    awards: list[AwardEntry] = Field(default_factory=list)
    additional_notes: str | None = None

    @field_validator("full_name")
    @classmethod
    def full_name_cannot_be_empty(cls, value: str) -> str:
        return _validate_non_empty(value, "full_name")
