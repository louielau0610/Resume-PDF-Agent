"""Screening criteria schemas."""

from pydantic import BaseModel, Field, field_validator

from resume_pdf_agent.models.enums import CriteriaCategory, ResumeType, SourceType


def _validate_non_empty(value: str, field_name: str) -> str:
    if not value or not value.strip():
        raise ValueError(f"{field_name} cannot be empty")
    return value


class SourceMetadata(BaseModel):
    """Public, user-provided, or manually curated source metadata."""

    source_type: SourceType
    title: str | None = None
    organization: str | None = None
    url: str | None = None
    retrieved_at: str | None = None
    notes: str | None = None


class ScreeningCriterion(BaseModel):
    """A normalized public or manually curated role screening criterion."""

    criterion_id: str
    category: CriteriaCategory
    name: str
    description: str
    importance: int = Field(ge=1, le=5)
    evidence_required: list[str] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)
    positive_signals: list[str] = Field(default_factory=list)
    negative_signals: list[str] = Field(default_factory=list)
    source: SourceMetadata
    confidence: float = Field(ge=0.0, le=1.0)

    @field_validator("criterion_id", "name", "description")
    @classmethod
    def required_text_fields_cannot_be_empty(cls, value: str, info):
        return _validate_non_empty(value, info.field_name)


class RoleCriteriaProfile(BaseModel):
    """Criteria profile for a target role and resume type."""

    profile_id: str
    role_title: str
    industry: str | None = None
    seniority_level: str | None = None
    target_companies: list[str] = Field(default_factory=list)
    resume_types: list[ResumeType] = Field(default_factory=list)
    criteria: list[ScreeningCriterion] = Field(default_factory=list)
    notes: str | None = None

    @field_validator("profile_id", "role_title")
    @classmethod
    def required_text_fields_cannot_be_empty(cls, value: str, info):
        return _validate_non_empty(value, info.field_name)
