"""Criterion-level deterministic matching logic."""

from resume_pdf_agent.gap_analysis.evidence import CandidateEvidenceBundle, normalize_text
from resume_pdf_agent.models import (
    CriteriaCategory,
    CriteriaMatchResult,
    EvidenceLevel,
    MatchLevel,
    MetricStatus,
    ResumeContent,
    RiskLevel,
    ScreeningCriterion,
)

_MEANINGFUL_SOURCES = {
    "experience_title",
    "experience_type",
    "raw_description",
    "responsibility",
    "tool",
    "method",
    "outcome",
    "metric",
    "evidence_note",
    "resume_bullet",
}
_PROFILE_SUPPORT_SOURCES = {
    "skill",
    "skill_group",
    "core_course",
    "education_major",
    "education_degree",
    "honor",
}


def _contains(text: str, phrase: str) -> bool:
    normalized_phrase = normalize_text(phrase)
    if not normalized_phrase:
        return False
    return normalized_phrase in text


def _matched_items(phrases: list[str], evidence_bundle: CandidateEvidenceBundle):
    matches = []
    for item in evidence_bundle.items:
        for phrase in phrases:
            if _contains(item.normalized_text, phrase):
                matches.append((phrase, item))
    return matches


def _resume_risk_flags(resume_content: ResumeContent | None) -> list[str]:
    if resume_content is None:
        return []
    warnings: list[str] = []
    for section in resume_content.sections:
        for bullet in section.bullets:
            prefix = f"Bullet '{bullet.text[:60]}'"
            if bullet.evidence_level == EvidenceLevel.UNSUPPORTED:
                warnings.append(f"{prefix} has unsupported evidence level.")
            if bullet.evidence_level == EvidenceLevel.NEEDS_USER_CONFIRMATION:
                warnings.append(f"{prefix} needs user confirmation.")
            if bullet.metric_status == MetricStatus.UNSUPPORTED:
                warnings.append(f"{prefix} has unsupported metric status.")
            if bullet.needs_confirmation:
                warnings.append(f"{prefix} is marked needs_confirmation.")
            for risk_flag in bullet.risk_flags:
                warnings.append(f"{prefix} has risk flag: {risk_flag}.")
    return warnings


def _has_user_metrics(resume_content: ResumeContent | None) -> bool:
    if resume_content is None:
        return False
    return any(experience.metrics for experience in resume_content.experiences)


def _has_outcomes(resume_content: ResumeContent | None) -> bool:
    if resume_content is None:
        return False
    return any(experience.outcomes for experience in resume_content.experiences)


def _has_sections_and_bullets(resume_content: ResumeContent | None) -> bool:
    if resume_content is None:
        return False
    return any(section.heading and section.bullets for section in resume_content.sections)


def _build_action(criterion: ScreeningCriterion, missing_terms: list[str]) -> str:
    if criterion.category == CriteriaCategory.IMPACT_QUANTIFICATION:
        return "Add user-provided metrics only if the candidate can verify them."
    if criterion.category == CriteriaCategory.ATS_READABILITY:
        return "Keep ATS wording simple with standard section headings."
    if missing_terms:
        return f"Add concrete evidence for {missing_terms[0]} if the candidate actually has it."
    return f"Add concrete evidence for {criterion.name.lower()} if it reflects the candidate's real experience."


def match_criterion_against_evidence(
    criterion: ScreeningCriterion,
    evidence_bundle: CandidateEvidenceBundle,
    resume_content: ResumeContent | None = None,
) -> CriteriaMatchResult:
    """Match one screening criterion against extracted candidate evidence."""

    if criterion.category == CriteriaCategory.IMPACT_QUANTIFICATION:
        if _has_user_metrics(resume_content):
            return CriteriaMatchResult(
                criterion_id=criterion.criterion_id,
                match_level=MatchLevel.STRONG,
                evidence_found=["User-provided metrics are present in resume content."],
                suggested_actions=["Use only verified user-provided metrics and keep source context visible."],
                risk_level=RiskLevel.LOW,
            )
        if _has_outcomes(resume_content):
            return CriteriaMatchResult(
                criterion_id=criterion.criterion_id,
                match_level=MatchLevel.MEDIUM,
                evidence_found=["Experience outcomes are present, but no explicit metric was provided."],
                missing_evidence=["User-provided metric with context"],
                suggested_actions=["Add user-provided metrics only if the candidate can verify them."],
                risk_level=RiskLevel.MEDIUM,
            )
        return CriteriaMatchResult(
            criterion_id=criterion.criterion_id,
            match_level=MatchLevel.MISSING,
            missing_evidence=["Verified outcomes or user-provided metrics"],
            suggested_actions=["Add user-provided metrics only if the candidate can verify them."],
            risk_level=RiskLevel.MEDIUM,
        )

    if criterion.category == CriteriaCategory.TRUTHFULNESS_RISK:
        warnings = _resume_risk_flags(resume_content)
        return CriteriaMatchResult(
            criterion_id=criterion.criterion_id,
            match_level=MatchLevel.WEAK if warnings else MatchLevel.STRONG,
            evidence_found=["No unsupported bullet metadata found."] if not warnings else warnings,
            missing_evidence=[] if not warnings else ["Resolve confirmation-needed or unsupported resume claims."],
            suggested_actions=[
                "Keep claims traceable to user-provided evidence.",
                "Remove or confirm unsupported metrics before final resume generation.",
            ],
            risk_level=RiskLevel.HIGH if len(warnings) >= 2 else RiskLevel.MEDIUM if warnings else RiskLevel.LOW,
        )

    if criterion.category == CriteriaCategory.ATS_READABILITY:
        if _has_sections_and_bullets(resume_content):
            return CriteriaMatchResult(
                criterion_id=criterion.criterion_id,
                match_level=MatchLevel.STRONG,
                evidence_found=["Resume content has section headings and bullet text."],
                suggested_actions=["Keep ATS wording simple with standard section headings."],
                risk_level=RiskLevel.LOW,
            )
        return CriteriaMatchResult(
            criterion_id=criterion.criterion_id,
            match_level=MatchLevel.WEAK,
            missing_evidence=["Structured resume sections and bullets"],
            suggested_actions=["Keep ATS wording simple with standard section headings."],
            risk_level=RiskLevel.MEDIUM,
        )

    phrases = [
        *criterion.keywords,
        *criterion.evidence_required,
        *criterion.positive_signals,
    ]
    matches = _matched_items(phrases, evidence_bundle)
    matched_phrases = list(dict.fromkeys(phrase for phrase, _item in matches))
    evidence_found = list(
        dict.fromkeys(f"{item.source_type}: {item.text}" for _phrase, item in matches)
    )
    missing_terms = [term for term in criterion.keywords if not _contains(evidence_bundle.normalized_all_text, term)]
    missing_required = [
        term for term in criterion.evidence_required if not _contains(evidence_bundle.normalized_all_text, term)
    ]

    meaningful_sources = {item.source_type for _phrase, item in matches if item.source_type in _MEANINGFUL_SOURCES}
    profile_sources = {item.source_type for _phrase, item in matches if item.source_type in _PROFILE_SUPPORT_SOURCES}
    target_only = bool(matches) and not meaningful_sources and not profile_sources

    if len(matched_phrases) >= 3 and meaningful_sources:
        match_level = MatchLevel.STRONG
        risk_level = RiskLevel.LOW
    elif matched_phrases and meaningful_sources:
        match_level = MatchLevel.MEDIUM
        risk_level = RiskLevel.LOW
    elif matched_phrases and profile_sources:
        match_level = MatchLevel.MEDIUM
        risk_level = RiskLevel.MEDIUM
    elif target_only:
        match_level = MatchLevel.WEAK
        risk_level = RiskLevel.MEDIUM
    else:
        match_level = MatchLevel.MISSING
        risk_level = RiskLevel.MEDIUM if criterion.importance >= 4 else RiskLevel.LOW

    if criterion.category == CriteriaCategory.EDUCATION_RELEVANCE and profile_sources and match_level == MatchLevel.MISSING:
        match_level = MatchLevel.MEDIUM
        risk_level = RiskLevel.LOW

    suggested_actions = [_build_action(criterion, missing_terms or missing_required)]
    return CriteriaMatchResult(
        criterion_id=criterion.criterion_id,
        match_level=match_level,
        evidence_found=evidence_found[:8],
        missing_evidence=list(dict.fromkeys([*missing_required, *missing_terms])),
        suggested_actions=suggested_actions,
        risk_level=risk_level,
    )
