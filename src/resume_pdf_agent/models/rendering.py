"""Models for deterministic HTML resume rendering."""

from enum import Enum

from pydantic import BaseModel, Field, field_validator, model_validator


def _validate_non_empty(value: str, field_name: str) -> str:
    if not value or not value.strip():
        raise ValueError(f"{field_name} cannot be empty")
    return value


class HTMLRenderStatus(str, Enum):
    """Supported HTML rendering status values."""

    RENDERED = "rendered"
    RENDERED_WITH_WARNINGS = "rendered_with_warnings"
    SKIPPED_DUE_TO_MISSING_TEMPLATE = "skipped_due_to_missing_template"
    SKIPPED_DUE_TO_INSUFFICIENT_CONTENT = "skipped_due_to_insufficient_content"


class RenderSectionItem(BaseModel):
    """One item prepared for a rendered resume section."""

    text: str
    source_id: str | None = None
    source_type: str | None = None
    needs_confirmation: bool = False
    risk_flags: list[str] = Field(default_factory=list)

    @field_validator("text")
    @classmethod
    def text_cannot_be_empty(cls, value: str) -> str:
        return _validate_non_empty(value, "text")


class RenderSection(BaseModel):
    """A section prepared for deterministic HTML rendering."""

    section_id: str
    heading: str
    items: list[RenderSectionItem] = Field(default_factory=list)
    required: bool

    @field_validator("section_id", "heading")
    @classmethod
    def required_text_fields_cannot_be_empty(cls, value: str, info):
        return _validate_non_empty(value, info.field_name)


class HTMLRenderOptions(BaseModel):
    """Options for HTML resume rendering."""

    include_css: bool = True
    include_preview_reminder_panel: bool = False
    include_truthfulness_warnings: bool = True
    ats_friendly_mode: bool = True
    max_items_per_section: int | None = None
    language: str = "en"

    @field_validator("language")
    @classmethod
    def language_cannot_be_empty(cls, value: str) -> str:
        return _validate_non_empty(value, "language")


class HTMLRenderResult(BaseModel):
    """Result returned by deterministic HTML rendering."""

    status: HTMLRenderStatus
    template_id: str
    html: str
    css: str | None = None
    sections_rendered: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    output_path: str | None = None
    summary: str

    @field_validator("template_id", "summary")
    @classmethod
    def required_text_fields_cannot_be_empty(cls, value: str, info):
        return _validate_non_empty(value, info.field_name)

    @model_validator(mode="after")
    def rendered_status_requires_html(self):
        if self.status in {
            HTMLRenderStatus.RENDERED,
            HTMLRenderStatus.RENDERED_WITH_WARNINGS,
        } and not self.html.strip():
            raise ValueError("html cannot be empty when rendering succeeds")
        return self
