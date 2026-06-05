"""Models for internal template metadata and selection."""

from enum import Enum

from pydantic import BaseModel, Field, field_validator, model_validator

from resume_pdf_agent.models.enums import ResumeType


def _validate_non_empty(value: str, field_name: str) -> str:
    if not value or not value.strip():
        raise ValueError(f"{field_name} cannot be empty")
    return value


class TemplateStyle(str, Enum):
    """Internal template style categories."""

    ATS_FRIENDLY = "ats_friendly"
    TECHNICAL = "technical"
    BUSINESS = "business"
    RESEARCH = "research"
    PRODUCT = "product"
    PORTFOLIO_LIGHT = "portfolio_light"
    GENERAL_STUDENT = "general_student"


class TemplateDensity(str, Enum):
    """Template density categories."""

    COMPACT = "compact"
    STANDARD = "standard"
    SPACIOUS = "spacious"


class TemplateSection(BaseModel):
    """Section metadata for an internal template profile."""

    section_id: str
    heading: str
    required: bool
    max_items: int | None = None
    notes: str | None = None

    @field_validator("section_id", "heading")
    @classmethod
    def required_text_fields_cannot_be_empty(cls, value: str, info):
        return _validate_non_empty(value, info.field_name)


class InternalTemplateProfile(BaseModel):
    """Metadata-only internal resume template profile."""

    template_id: str
    display_name: str
    description: str
    style: TemplateStyle
    density: TemplateDensity
    supported_resume_types: list[ResumeType] = Field(default_factory=list)
    recommended_roles: list[str] = Field(default_factory=list)
    recommended_industries: list[str] = Field(default_factory=list)
    sections: list[TemplateSection] = Field(default_factory=list)
    ats_friendly: bool
    supports_portfolio_link: bool
    supports_research_outputs: bool
    supports_project_heavy_layout: bool
    supports_one_page_layout: bool
    visual_complexity: int = Field(ge=1, le=5)
    notes: str | None = None

    @field_validator("template_id", "display_name", "description")
    @classmethod
    def required_text_fields_cannot_be_empty(cls, value: str, info):
        return _validate_non_empty(value, info.field_name)


class TemplateMatchReason(BaseModel):
    """One scoring reason for template selection."""

    reason_type: str
    message: str
    weight: float = Field(ge=0.0)

    @field_validator("reason_type", "message")
    @classmethod
    def required_text_fields_cannot_be_empty(cls, value: str, info):
        return _validate_non_empty(value, info.field_name)


class TemplateScore(BaseModel):
    """Score and reasons for one template."""

    template_id: str
    score: float = Field(ge=0.0)
    reasons: list[TemplateMatchReason] = Field(default_factory=list)

    @field_validator("template_id")
    @classmethod
    def template_id_cannot_be_empty(cls, value: str) -> str:
        return _validate_non_empty(value, "template_id")


class TemplateSelectionResult(BaseModel):
    """Result from deterministic internal template selection."""

    selected_template_id: str
    selected_template: InternalTemplateProfile
    ranked_templates: list[TemplateScore]
    recommended_sections: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    summary: str

    @field_validator("selected_template_id", "summary")
    @classmethod
    def required_text_fields_cannot_be_empty(cls, value: str, info):
        return _validate_non_empty(value, info.field_name)

    @model_validator(mode="after")
    def selected_template_must_be_ranked(self):
        if not self.ranked_templates:
            raise ValueError("ranked_templates cannot be empty")
        ranked_ids = {item.template_id for item in self.ranked_templates}
        if self.selected_template_id not in ranked_ids:
            raise ValueError("selected_template_id must appear in ranked_templates")
        return self
