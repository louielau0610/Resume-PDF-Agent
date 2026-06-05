"""Models for deterministic criteria-aware bullet enhancement."""

from enum import Enum

from pydantic import BaseModel, Field, field_validator, model_validator

from resume_pdf_agent.models.enums import EvidenceLevel, MetricStatus, ResumeType


def _validate_non_empty(value: str, field_name: str) -> str:
    if not value or not value.strip():
        raise ValueError(f"{field_name} cannot be empty")
    return value


class BulletEnhancementMode(str, Enum):
    """Supported deterministic enhancement modes."""

    CLARITY = "clarity"
    CRITERIA_ALIGNMENT = "criteria_alignment"
    IMPACT_FRAMING = "impact_framing"
    ATS_KEYWORD_ALIGNMENT = "ats_keyword_alignment"
    CONSERVATIVE_REWRITE = "conservative_rewrite"


class BulletEnhancementStatus(str, Enum):
    """Enhancement candidate status."""

    ENHANCED = "enhanced"
    UNCHANGED = "unchanged"
    SKIPPED_DUE_TO_TRUTHFULNESS_RISK = "skipped_due_to_truthfulness_risk"
    NEEDS_USER_CONFIRMATION = "needs_user_confirmation"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"


class EnhancedBulletCandidate(BaseModel):
    """One conservative enhanced bullet candidate."""

    candidate_id: str
    source_experience_id: str | None = None
    original_text: str | None = None
    enhanced_text: str
    mode: BulletEnhancementMode
    status: BulletEnhancementStatus
    targeted_criteria_ids: list[str] = Field(default_factory=list)
    evidence_level: EvidenceLevel
    metric_status: MetricStatus
    needs_confirmation: bool = False
    risk_flags: list[str] = Field(default_factory=list)
    rationale: str

    @field_validator("candidate_id", "enhanced_text", "rationale")
    @classmethod
    def required_text_fields_cannot_be_empty(cls, value: str, info):
        return _validate_non_empty(value, info.field_name)

    @model_validator(mode="after")
    def unsupported_values_require_confirmation(self):
        if self.evidence_level == EvidenceLevel.UNSUPPORTED:
            self.needs_confirmation = True
        if self.metric_status == MetricStatus.UNSUPPORTED:
            self.needs_confirmation = True
        return self


class ExperienceEnhancementResult(BaseModel):
    """Enhancement results for one source experience."""

    experience_id: str
    title: str
    candidates: list[EnhancedBulletCandidate] = Field(default_factory=list)
    skipped_reasons: list[str] = Field(default_factory=list)

    @field_validator("experience_id", "title")
    @classmethod
    def required_text_fields_cannot_be_empty(cls, value: str, info):
        return _validate_non_empty(value, info.field_name)


class BulletEnhancementResult(BaseModel):
    """Aggregate result from deterministic bullet enhancement."""

    resume_type: ResumeType
    experience_results: list[ExperienceEnhancementResult] = Field(default_factory=list)
    global_warnings: list[str] = Field(default_factory=list)
    truthfulness_blockers: list[str] = Field(default_factory=list)
    candidates_generated: int = Field(ge=0)
    candidates_requiring_confirmation: int = Field(ge=0)
    safe_candidates_count: int = Field(ge=0)
    summary: str

    @field_validator("summary")
    @classmethod
    def summary_cannot_be_empty(cls, value: str) -> str:
        return _validate_non_empty(value, "summary")
