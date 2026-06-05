"""JD-to-criteria converter for M15.

Converts a ParsedJD into a RoleCriteriaProfile suitable for use by
the existing criteria-aware workflow.
"""

from __future__ import annotations

import re
import uuid

from resume_pdf_agent.models.criteria import (
    RoleCriteriaProfile,
    ScreeningCriterion,
    SourceMetadata,
)
from resume_pdf_agent.models.enums import (
    CriteriaCategory,
    ResumeType,
    SourceType,
)
from resume_pdf_agent.models.jd import (
    JDComplianceStatus,
    JDToCriteriaBuildResult,
    ParsedJD,
)


def _safe_slug(text: str | None) -> str:
    """Create a safe slug from text for profile IDs."""
    if not text:
        return "jd"
    slug = re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")
    return slug[:40] or "jd"


def _infer_resume_types(role_title: str | None, skills: list[str]) -> list[ResumeType]:
    """Infer applicable resume types from role title and skills."""
    if not role_title:
        return [ResumeType.GENERAL_STUDENT_RESUME]

    text = role_title.lower()
    types: list[ResumeType] = []

    # Data science / analytics
    if any(kw in text for kw in (
        "data sci", "data analy", "machine learn", "analytics",
        "data engineer", "ml engineer", "ai ", "statistic",
    )):
        types.append(ResumeType.DATA_SCIENCE_RESUME)

    # Software engineering
    if any(kw in text for kw in (
        "software", "developer", "engineer", "backend", "frontend",
        "full stack", "fullstack", "devops", "sre",
    )):
        types.append(ResumeType.TECHNICAL_RESUME)

    # Product manager
    if any(kw in text for kw in ("product manager", "product owner", "pm ")):
        types.append(ResumeType.PRODUCT_MANAGER_RESUME)

    # Finance
    if any(kw in text for kw in (
        "finance", "investment", "banking", "accounting", "actuar",
        "trading", "portfolio",
    )):
        types.append(ResumeType.FINANCE_BUSINESS_RESUME)

    # Consulting
    if any(kw in text for kw in ("consult", "strategy", "advisory")):
        types.append(ResumeType.CONSULTING_RESUME)

    # Research
    if any(kw in text for kw in (
        "research", "scientist", "lab ", "laboratory", "phd",
        "postdoc", "post doc",
    )):
        types.append(ResumeType.RESEARCH_CV)

    # Design
    if any(kw in text for kw in ("design", "ux ", "ui ", "user experience")):
        types.append(ResumeType.DESIGN_PORTFOLIO_RESUME)

    if not types:
        types.append(ResumeType.GENERAL_STUDENT_RESUME)

    return types


def _make_criterion(
    criterion_id: str,
    category: CriteriaCategory,
    name: str,
    description: str,
    importance: int,
    keywords: list[str],
) -> ScreeningCriterion:
    """Create a ScreeningCriterion with user_provided_jd source."""
    return ScreeningCriterion(
        criterion_id=criterion_id,
        category=category,
        name=name,
        description=description,
        importance=importance,
        evidence_required=[],
        keywords=keywords,
        source=SourceMetadata(
            source_type=SourceType.USER_PROVIDED_JD,
            title="User-provided JD",
            notes="Criteria derived from user-provided job description text.",
        ),
        confidence=0.75,
    )


def build_criteria_profile_from_jd(
    parsed_jd: ParsedJD,
    profile_id: str | None = None,
) -> JDToCriteriaBuildResult:
    """Convert a ParsedJD into a RoleCriteriaProfile.

    Parameters
    ----------
    parsed_jd : ParsedJD
        The parsed JD to convert.
    profile_id : str | None
        Optional profile ID. Auto-generated if None.

    Returns
    -------
    JDToCriteriaBuildResult
        Result with criteria profile or error details.
    """
    warnings: list[str] = []
    errors: list[str] = []

    # ── Compliance gate ──────────────────────────────────────────────
    if not parsed_jd.compliance_result.can_parse:
        errors.append(
            "Cannot build criteria profile: JD compliance check blocked parsing."
        )
        return JDToCriteriaBuildResult(
            criteria_profile=None,
            parsed_jd=parsed_jd,
            warnings=warnings,
            errors=errors,
            summary="JD 合规检查未通过，无法生成 criteria profile。",
        )

    # ── Build profile ────────────────────────────────────────────────
    pid = profile_id or f"user_jd_{_safe_slug(parsed_jd.role_title)}"
    role_title = parsed_jd.role_title or "User-provided JD"
    resume_types = _infer_resume_types(
        parsed_jd.role_title, parsed_jd.skills
    )

    criteria: list[ScreeningCriterion] = []
    all_keywords = list(parsed_jd.keywords)

    # Required qualifications → importance 5
    for i, qual in enumerate(parsed_jd.required_qualifications[:8]):
        criteria.append(
            _make_criterion(
                criterion_id=f"{pid}_req_{i}",
                category=CriteriaCategory.SKILL_COVERAGE,
                name=f"Required: {qual[:80]}",
                description=qual,
                importance=5,
                keywords=all_keywords[:10],
            )
        )

    # Responsibilities → importance 4
    for i, resp in enumerate(parsed_jd.responsibilities[:5]):
        criteria.append(
            _make_criterion(
                criterion_id=f"{pid}_resp_{i}",
                category=CriteriaCategory.ROLE_FIT,
                name=f"Responsibility: {resp[:80]}",
                description=resp,
                importance=4,
                keywords=all_keywords[:10],
            )
        )

    # Skills/tools → importance 4
    if parsed_jd.skills:
        criteria.append(
            _make_criterion(
                criterion_id=f"{pid}_skills",
                category=CriteriaCategory.SKILL_COVERAGE,
                name="Technical Skills",
                description=f"Required skills: {', '.join(parsed_jd.skills[:15])}",
                importance=4,
                keywords=parsed_jd.skills,
            )
        )

    # Preferred qualifications → importance 3
    for i, pref in enumerate(parsed_jd.preferred_qualifications[:3]):
        criteria.append(
            _make_criterion(
                criterion_id=f"{pid}_pref_{i}",
                category=CriteriaCategory.SKILL_COVERAGE,
                name=f"Preferred: {pref[:80]}",
                description=pref,
                importance=3,
                keywords=all_keywords[:10],
            )
        )

    # Education → importance 3
    if parsed_jd.education_requirements:
        criteria.append(
            _make_criterion(
                criterion_id=f"{pid}_edu",
                category=CriteriaCategory.EDUCATION_RELEVANCE,
                name="Education",
                description="; ".join(parsed_jd.education_requirements[:5]),
                importance=3,
                keywords=[],
            )
        )

    # ATS readability → importance 4
    criteria.append(
        _make_criterion(
            criterion_id=f"{pid}_ats",
            category=CriteriaCategory.ATS_READABILITY,
            name="ATS Readability",
            description="Resume should be ATS-friendly with clear section headings and keyword coverage.",
            importance=4,
            keywords=all_keywords[:10],
        )
    )

    # Impact quantification → importance 4
    criteria.append(
        _make_criterion(
            criterion_id=f"{pid}_impact",
            category=CriteriaCategory.IMPACT_QUANTIFICATION,
            name="Impact Quantification",
            description="Where possible, quantify achievements with metrics (percentages, numbers, scale).",
            importance=4,
            keywords=[],
        )
    )

    # Truthfulness risk → importance 5
    criteria.append(
        _make_criterion(
            criterion_id=f"{pid}_truth",
            category=CriteriaCategory.TRUTHFULNESS_RISK,
            name="Truthfulness",
            description="All claims must be supported by verifiable evidence. No fabrication.",
            importance=5,
            keywords=[],
        )
    )

    if len(criteria) < 3:
        warnings.append(
            "Very few criteria extracted from JD. The JD text may be too short."
        )

    target_companies = []
    if parsed_jd.company_name:
        target_companies.append(parsed_jd.company_name)

    profile = RoleCriteriaProfile(
        profile_id=pid,
        role_title=role_title,
        seniority_level=parsed_jd.seniority_level,
        target_companies=target_companies,
        resume_types=resume_types,
        criteria=criteria,
        notes=f"Auto-generated from user-provided JD. "
              f"Source type: {parsed_jd.source_type.value}. "
              f"Sections found: {', '.join(parsed_jd.sections_found)}.",
    )

    return JDToCriteriaBuildResult(
        criteria_profile=profile,
        parsed_jd=parsed_jd,
        warnings=warnings,
        errors=errors,
        summary=(
            f"从用户提供的 JD 生成了 {len(criteria)} 条 criteria。"
            f"角色: {role_title}。"
            f"简历类型: {', '.join(rt.value for rt in resume_types)}。"
        ),
    )
