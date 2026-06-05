"""Models for deterministic PDF generation."""

from enum import Enum

from pydantic import BaseModel, Field, field_validator, model_validator


def _validate_non_empty(value: str, field_name: str) -> str:
    if not value or not value.strip():
        raise ValueError(f"{field_name} cannot be empty")
    return value


def _contains_forbidden_claim(value: str | None) -> bool:
    if not value:
        return False
    normalized = value.lower()
    return "hiring probability" in normalized or "internal company screening" in normalized


class PDFBackend(str, Enum):
    """Supported PDF generation backend identifiers."""

    WEASYPRINT = "weasyprint"
    PLAYWRIGHT = "playwright"
    MOCK = "mock"


class PDFGenerationStatus(str, Enum):
    """Supported PDF generation status values."""

    GENERATED = "generated"
    GENERATED_WITH_WARNINGS = "generated_with_warnings"
    SKIPPED_BACKEND_UNAVAILABLE = "skipped_backend_unavailable"
    FAILED = "failed"


class PDFPageFormat(str, Enum):
    """Supported PDF page formats for v0."""

    A4 = "A4"
    LETTER = "Letter"


class PDFGenerationOptions(BaseModel):
    """Options for HTML-to-PDF generation."""

    backend: PDFBackend = PDFBackend.WEASYPRINT
    page_format: PDFPageFormat = PDFPageFormat.A4
    margin_top_mm: float = Field(default=10.0, ge=0.0)
    margin_right_mm: float = Field(default=10.0, ge=0.0)
    margin_bottom_mm: float = Field(default=10.0, ge=0.0)
    margin_left_mm: float = Field(default=10.0, ge=0.0)
    print_background: bool = True
    prefer_single_page: bool = True
    include_conversion_reminder: bool = True
    fail_on_backend_unavailable: bool = False


class PDFGenerationResult(BaseModel):
    """Result returned by PDF generation."""

    status: PDFGenerationStatus
    backend: PDFBackend
    output_path: str | None = None
    file_size_bytes: int | None = None
    page_format: PDFPageFormat
    warnings: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    conversion_reminder: str | None = None
    summary: str

    @field_validator("summary")
    @classmethod
    def summary_cannot_be_empty(cls, value: str) -> str:
        return _validate_non_empty(value, "summary")

    @model_validator(mode="after")
    def generated_status_requires_output_metadata(self):
        if self.status in {
            PDFGenerationStatus.GENERATED,
            PDFGenerationStatus.GENERATED_WITH_WARNINGS,
        }:
            if not self.output_path:
                raise ValueError("output_path is required when PDF generation succeeds")
            if self.file_size_bytes is None or self.file_size_bytes <= 0:
                raise ValueError("file_size_bytes must be positive when PDF generation succeeds")
        if _contains_forbidden_claim(self.summary) or _contains_forbidden_claim(self.conversion_reminder):
            raise ValueError("PDF generation metadata cannot include unsupported hiring or screening claims")
        return self
