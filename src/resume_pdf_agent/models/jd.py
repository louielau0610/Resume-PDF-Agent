"""Pydantic models for M15 user-provided JD parser."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field, model_validator

from resume_pdf_agent.models.criteria import RoleCriteriaProfile
from resume_pdf_agent.models.enums import RiskLevel


class JDSourceType(str, Enum):
    """Source type of the JD content."""

    USER_PROVIDED_TEXT = "user_provided_text"
    USER_PROVIDED_FILE = "user_provided_file"
    PUBLIC_JOB_DESCRIPTION = "public_job_description"
    UNKNOWN = "unknown"


class JDComplianceStatus(str, Enum):
    """Compliance check result status."""

    ALLOWED = "allowed"
    ALLOWED_WITH_WARNINGS = "allowed_with_warnings"
    BLOCKED = "blocked"


class JDComplianceIssueType(str, Enum):
    """Types of compliance issues detected in JD text."""

    CONFIDENTIAL_MARKER = "confidential_marker"
    INTERNAL_USE_MARKER = "internal_use_marker"
    LEAKED_RUBRIC_RISK = "leaked_rubric_risk"
    PRIVATE_CANDIDATE_EVALUATION_RISK = "private_candidate_evaluation_risk"
    ACCESS_CONTROL_RISK = "access_control_risk"
    UNSUPPORTED_SOURCE = "unsupported_source"
    UNKNOWN_SOURCE_WARNING = "unknown_source_warning"
    GENERIC_COMPLIANCE_WARNING = "generic_compliance_warning"


class JDComplianceIssue(BaseModel):
    """A single compliance issue found in JD text."""

    issue_id: str = Field(min_length=1)
    issue_type: JDComplianceIssueType
    severity: RiskLevel
    matched_text: str = Field(min_length=1)
    reason: str = Field(min_length=1)
    suggested_action: str = Field(min_length=1)


class JDComplianceResult(BaseModel):
    """Result of JD compliance checking."""

    status: JDComplianceStatus
    source_type: JDSourceType
    issues: list[JDComplianceIssue] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    can_parse: bool = True
    summary: str = Field(min_length=1)

    @model_validator(mode="after")
    def _blocked_means_cannot_parse(self) -> JDComplianceResult:
        if self.status == JDComplianceStatus.BLOCKED:
            self.can_parse = False
        return self


class ParsedJD(BaseModel):
    """Structured result of deterministic JD parsing."""

    jd_id: str = Field(min_length=1)
    source_type: JDSourceType
    raw_text: str = Field(min_length=1)
    normalized_text: str = Field(min_length=1)
    role_title: str | None = None
    company_name: str | None = None
    location: str | None = None
    employment_type: str | None = None
    seniority_level: str | None = None
    responsibilities: list[str] = Field(default_factory=list)
    required_qualifications: list[str] = Field(default_factory=list)
    preferred_qualifications: list[str] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)
    tools: list[str] = Field(default_factory=list)
    education_requirements: list[str] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)
    sections_found: list[str] = Field(default_factory=list)
    compliance_result: JDComplianceResult
    warnings: list[str] = Field(default_factory=list)


class JDToCriteriaBuildResult(BaseModel):
    """Result of converting a parsed JD to a RoleCriteriaProfile."""

    criteria_profile: RoleCriteriaProfile | None = None
    parsed_jd: ParsedJD
    warnings: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    summary: str = Field(min_length=1)

    @model_validator(mode="after")
    def _profile_when_allowed(self) -> JDToCriteriaBuildResult:
        if not self.errors and self.parsed_jd.compliance_result.can_parse:
            if self.criteria_profile is None:
                raise ValueError(
                    "criteria_profile is required when compliance allows parsing"
                )
        return self
