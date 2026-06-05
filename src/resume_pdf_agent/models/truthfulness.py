"""Models for deterministic truthfulness checking."""

from enum import Enum

from pydantic import BaseModel, Field, field_validator, model_validator

from resume_pdf_agent.models.enums import EvidenceLevel, MetricStatus, RiskLevel


def _validate_non_empty(value: str, field_name: str) -> str:
    if not value or not value.strip():
        raise ValueError(f"{field_name} cannot be empty")
    return value


class TruthfulnessIssueType(str, Enum):
    """Supported truthfulness issue categories."""

    UNSUPPORTED_EVIDENCE = "unsupported_evidence"
    UNSUPPORTED_METRIC = "unsupported_metric"
    NEEDS_CONFIRMATION = "needs_confirmation"
    RISK_FLAG = "risk_flag"
    UNVERIFIABLE_QUANTIFIED_CLAIM = "unverifiable_quantified_claim"
    METRIC_WITHOUT_SOURCE = "metric_without_source"
    LEADERSHIP_EXAGGERATION_RISK = "leadership_exaggeration_risk"
    TOOL_OR_METHOD_NOT_SUPPORTED = "tool_or_method_not_supported"
    SOURCE_EXPERIENCE_MISMATCH = "source_experience_mismatch"
    GAP_ANALYSIS_WARNING = "gap_analysis_warning"
    GENERIC_TRUTHFULNESS_WARNING = "generic_truthfulness_warning"


class TruthfulnessSeverity(str, Enum):
    """Issue severity levels."""

    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ClaimEvidenceStatus(str, Enum):
    """Evidence status for a resume claim."""

    SUPPORTED = "supported"
    USER_PROVIDED = "user_provided"
    REASONABLY_INFERRED = "reasonably_inferred"
    NEEDS_USER_CONFIRMATION = "needs_user_confirmation"
    UNSUPPORTED = "unsupported"
    UNVERIFIABLE = "unverifiable"
    NOT_APPLICABLE = "not_applicable"


class ResumeClaim(BaseModel):
    """Extracted claim from structured resume content."""

    claim_id: str
    source_type: str
    source_id: str | None = None
    text: str
    normalized_text: str
    evidence_level: EvidenceLevel | None = None
    metric_status: MetricStatus | None = None
    needs_confirmation: bool = False
    risk_flags: list[str] = Field(default_factory=list)
    related_experience_id: str | None = None
    targeted_criteria_ids: list[str] = Field(default_factory=list)

    @field_validator("claim_id", "source_type", "text", "normalized_text")
    @classmethod
    def required_text_fields_cannot_be_empty(cls, value: str, info):
        return _validate_non_empty(value, info.field_name)


class TruthfulnessIssue(BaseModel):
    """One detected truthfulness or support issue."""

    issue_id: str
    issue_type: TruthfulnessIssueType
    severity: TruthfulnessSeverity
    source_type: str
    source_id: str | None = None
    claim_text: str
    evidence_status: ClaimEvidenceStatus
    reason: str
    suggested_action: str
    related_criteria_ids: list[str] = Field(default_factory=list)

    @field_validator("issue_id", "source_type", "claim_text", "reason", "suggested_action")
    @classmethod
    def required_text_fields_cannot_be_empty(cls, value: str, info):
        return _validate_non_empty(value, info.field_name)


class TruthfulnessCheckResult(BaseModel):
    """Aggregate result from the truthfulness checker."""

    overall_risk_level: RiskLevel
    issues: list[TruthfulnessIssue] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    claims_checked: int = Field(ge=0)
    high_risk_count: int = Field(ge=0)
    medium_risk_count: int = Field(ge=0)
    low_risk_count: int = Field(ge=0)
    safe_to_proceed: bool
    summary: str

    @field_validator("summary")
    @classmethod
    def summary_cannot_be_empty(cls, value: str) -> str:
        return _validate_non_empty(value, "summary")

    @model_validator(mode="after")
    def high_risk_blocks_safe_to_proceed(self):
        if self.high_risk_count > 0 and self.safe_to_proceed:
            raise ValueError("safe_to_proceed must be false when high_risk_count > 0")
        return self
