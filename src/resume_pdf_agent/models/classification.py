"""Models for deterministic resume type classification results."""

from pydantic import BaseModel, Field, field_validator, model_validator

from resume_pdf_agent.models.enums import ResumeType


def _validate_non_empty(value: str, field_name: str) -> str:
    if not value or not value.strip():
        raise ValueError(f"{field_name} cannot be empty")
    return value


class ClassificationSignal(BaseModel):
    """One matched signal used by the rule-based classifier."""

    source: str
    matched_text: str
    resume_type: ResumeType
    weight: float = Field(ge=0.0)
    reason: str

    @field_validator("source", "matched_text", "reason")
    @classmethod
    def required_text_fields_cannot_be_empty(cls, value: str, info):
        return _validate_non_empty(value, info.field_name)


class ResumeTypeScore(BaseModel):
    """Score and supporting signals for one resume type."""

    resume_type: ResumeType
    score: float = Field(ge=0.0)
    signals: list[ClassificationSignal] = Field(default_factory=list)


class ResumeTypeClassificationResult(BaseModel):
    """Ranked output from the deterministic resume type classifier."""

    primary_resume_type: ResumeType
    ranked_types: list[ResumeTypeScore]
    confidence: float = Field(ge=0.0, le=1.0)
    recommended_sections: list[str] = Field(default_factory=list)
    explanation: str
    warnings: list[str] = Field(default_factory=list)

    @field_validator("explanation")
    @classmethod
    def explanation_cannot_be_empty(cls, value: str) -> str:
        return _validate_non_empty(value, "explanation")

    @model_validator(mode="after")
    def primary_type_must_appear_in_ranked_types(self):
        if not self.ranked_types:
            raise ValueError("ranked_types cannot be empty")
        ranked_resume_types = {item.resume_type for item in self.ranked_types}
        if self.primary_resume_type not in ranked_resume_types:
            raise ValueError("primary_resume_type must appear in ranked_types")
        return self
