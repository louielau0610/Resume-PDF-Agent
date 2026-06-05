"""Enum definitions for resume_pdf_agent schemas."""

from enum import Enum


class ResumeType(str, Enum):
    """Supported resume type labels."""

    TECHNICAL_RESUME = "technical_resume"
    DATA_SCIENCE_RESUME = "data_science_resume"
    FINANCE_BUSINESS_RESUME = "finance_business_resume"
    CONSULTING_RESUME = "consulting_resume"
    RESEARCH_CV = "research_cv"
    PRODUCT_MANAGER_RESUME = "product_manager_resume"
    DESIGN_PORTFOLIO_RESUME = "design_portfolio_resume"
    GENERAL_STUDENT_RESUME = "general_student_resume"


class ExperienceType(str, Enum):
    """Supported experience categories."""

    PROJECT = "project"
    INTERNSHIP = "internship"
    RESEARCH = "research"
    LEADERSHIP = "leadership"
    VOLUNTEER = "volunteer"
    COMPETITION = "competition"
    COURSEWORK = "coursework"
    WORK_EXPERIENCE = "work_experience"
    OTHER = "other"


class CriteriaCategory(str, Enum):
    """Screening criteria categories."""

    ROLE_FIT = "role_fit"
    SKILL_COVERAGE = "skill_coverage"
    EVIDENCE_STRENGTH = "evidence_strength"
    IMPACT_QUANTIFICATION = "impact_quantification"
    ACTION_RESULT_CLARITY = "action_result_clarity"
    EDUCATION_RELEVANCE = "education_relevance"
    ATS_READABILITY = "ats_readability"
    TRUTHFULNESS_RISK = "truthfulness_risk"


class SourceType(str, Enum):
    """Allowed source types for criteria metadata."""

    OFFICIAL_COMPANY_PAGE = "official_company_page"
    OFFICIAL_HIRING_GUIDE = "official_hiring_guide"
    PUBLIC_JOB_DESCRIPTION = "public_job_description"
    UNIVERSITY_CAREER_GUIDE = "university_career_guide"
    PUBLIC_BLOG = "public_blog"
    COMMUNITY_POST = "community_post"
    USER_PROVIDED_JD = "user_provided_jd"
    MANUALLY_CURATED = "manually_curated"


class EvidenceLevel(str, Enum):
    """How strongly a resume claim is backed by user evidence."""

    USER_PROVIDED = "user_provided"
    REASONABLY_INFERRED = "reasonably_inferred"
    NEEDS_USER_CONFIRMATION = "needs_user_confirmation"
    UNSUPPORTED = "unsupported"


class MetricStatus(str, Enum):
    """Whether a metric is supported by user-provided evidence."""

    USER_PROVIDED = "user_provided"
    MISSING = "missing"
    NOT_APPLICABLE = "not_applicable"
    UNSUPPORTED = "unsupported"


class MatchLevel(str, Enum):
    """Match level between candidate evidence and a criterion."""

    STRONG = "strong"
    MEDIUM = "medium"
    WEAK = "weak"
    MISSING = "missing"
    NOT_APPLICABLE = "not_applicable"


class RiskLevel(str, Enum):
    """Risk level for claim quality or truthfulness concerns."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ExportFormat(str, Enum):
    """Supported export formats for v0."""

    PDF = "pdf"
