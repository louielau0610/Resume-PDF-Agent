"""Analysis result schemas for future gap analysis modules."""

from pydantic import BaseModel, Field, field_validator

from resume_pdf_agent.models.enums import MatchLevel, RiskLevel


def _validate_non_empty(value: str, field_name: str) -> str:
    if not value or not value.strip():
        raise ValueError(f"{field_name} cannot be empty")
    return value


class CriteriaMatchResult(BaseModel):
    """Result for one criterion after future matching logic runs."""

    criterion_id: str
    match_level: MatchLevel
    evidence_found: list[str] = Field(default_factory=list)
    missing_evidence: list[str] = Field(default_factory=list)
    suggested_actions: list[str] = Field(default_factory=list)
    risk_level: RiskLevel

    @field_validator("criterion_id")
    @classmethod
    def criterion_id_cannot_be_empty(cls, value: str) -> str:
        return _validate_non_empty(value, "criterion_id")


class GapAnalysisResult(BaseModel):
    """Structured gap analysis output for future modules."""

    profile_id: str
    overall_match_level: MatchLevel
    criteria_results: list[CriteriaMatchResult] = Field(default_factory=list)
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    missing_keywords: list[str] = Field(default_factory=list)
    truthfulness_warnings: list[str] = Field(default_factory=list)

    @field_validator("profile_id")
    @classmethod
    def profile_id_cannot_be_empty(cls, value: str) -> str:
        return _validate_non_empty(value, "profile_id")
