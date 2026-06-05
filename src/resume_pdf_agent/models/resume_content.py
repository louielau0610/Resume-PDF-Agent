"""Resume content schemas."""

from pydantic import BaseModel, Field, field_validator, model_validator

from resume_pdf_agent.models.enums import EvidenceLevel, ExperienceType, MetricStatus, ResumeType


def _validate_non_empty(value: str, field_name: str) -> str:
    if not value or not value.strip():
        raise ValueError(f"{field_name} cannot be empty")
    return value


class Metric(BaseModel):
    """A user-provided or evidence-backed metric."""

    name: str
    value: str
    unit: str | None = None
    context: str | None = None
    source_note: str | None = None

    @field_validator("name", "value")
    @classmethod
    def required_text_fields_cannot_be_empty(cls, value: str, info):
        return _validate_non_empty(value, info.field_name)


class ExperienceEntry(BaseModel):
    """Structured raw experience entry."""

    experience_id: str
    experience_type: ExperienceType
    title: str
    organization: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    raw_description: str | None = None
    responsibilities: list[str] = Field(default_factory=list)
    tools_used: list[str] = Field(default_factory=list)
    methods_used: list[str] = Field(default_factory=list)
    outcomes: list[str] = Field(default_factory=list)
    metrics: list[Metric] = Field(default_factory=list)
    evidence_notes: list[str] = Field(default_factory=list)

    @field_validator("experience_id", "title")
    @classmethod
    def required_text_fields_cannot_be_empty(cls, value: str, info):
        return _validate_non_empty(value, info.field_name)


class ResumeBullet(BaseModel):
    """A resume bullet with evidence and confirmation metadata."""

    text: str
    source_experience_id: str | None = None
    targeted_criteria_ids: list[str] = Field(default_factory=list)
    evidence_level: EvidenceLevel
    metric_status: MetricStatus
    needs_confirmation: bool = False
    risk_flags: list[str] = Field(default_factory=list)

    @field_validator("text")
    @classmethod
    def text_cannot_be_empty(cls, value: str) -> str:
        return _validate_non_empty(value, "text")

    @model_validator(mode="after")
    def unsupported_claims_require_confirmation(self):
        if self.evidence_level in {
            EvidenceLevel.UNSUPPORTED,
            EvidenceLevel.NEEDS_USER_CONFIRMATION,
        }:
            self.needs_confirmation = True
        if self.metric_status == MetricStatus.UNSUPPORTED:
            self.needs_confirmation = True
        return self


class ResumeSection(BaseModel):
    """A rendered resume section represented as structured bullets."""

    heading: str
    bullets: list[ResumeBullet] = Field(default_factory=list)

    @field_validator("heading")
    @classmethod
    def heading_cannot_be_empty(cls, value: str) -> str:
        return _validate_non_empty(value, "heading")


class ResumeContent(BaseModel):
    """Structured resume content for downstream rendering."""

    resume_type: ResumeType
    summary: str | None = None
    experiences: list[ExperienceEntry] = Field(default_factory=list)
    sections: list[ResumeSection] = Field(default_factory=list)
