"""Aggregate criteria-based gap analysis."""

from resume_pdf_agent.gap_analysis.evidence import extract_candidate_evidence
from resume_pdf_agent.gap_analysis.matcher import match_criterion_against_evidence
from resume_pdf_agent.models import (
    GapAnalysisResult,
    MatchLevel,
    ResumeContent,
    ResumeTypeClassificationResult,
    RoleCriteriaProfile,
    UserProfile,
)

_MATCH_SCORES = {
    MatchLevel.STRONG: 1.0,
    MatchLevel.MEDIUM: 0.65,
    MatchLevel.WEAK: 0.35,
    MatchLevel.MISSING: 0.0,
    MatchLevel.NOT_APPLICABLE: 0.5,
}


def _overall_match_level(weighted_score: float) -> MatchLevel:
    if weighted_score >= 0.75:
        return MatchLevel.STRONG
    if weighted_score >= 0.50:
        return MatchLevel.MEDIUM
    if weighted_score >= 0.25:
        return MatchLevel.WEAK
    return MatchLevel.MISSING


def _dedupe(values: list[str]) -> list[str]:
    return list(dict.fromkeys(value for value in values if value))


def analyze_criteria_gap(
    user_profile: UserProfile,
    criteria_profile: RoleCriteriaProfile,
    resume_content: ResumeContent | None = None,
    classification_result: ResumeTypeClassificationResult | None = None,
) -> GapAnalysisResult:
    """Analyze deterministic gaps between candidate evidence and role criteria."""

    evidence_bundle = extract_candidate_evidence(user_profile, resume_content)
    criteria_results = [
        match_criterion_against_evidence(criterion, evidence_bundle, resume_content)
        for criterion in criteria_profile.criteria
    ]

    total_weight = 0.0
    weighted_total = 0.0
    criteria_by_id = {criterion.criterion_id: criterion for criterion in criteria_profile.criteria}
    for result in criteria_results:
        criterion = criteria_by_id[result.criterion_id]
        total_weight += criterion.importance
        weighted_total += _MATCH_SCORES[result.match_level] * criterion.importance
    weighted_score = weighted_total / total_weight if total_weight else 0.0

    strengths = [
        f"Strong evidence for {criteria_by_id[result.criterion_id].name}."
        for result in criteria_results
        if result.match_level == MatchLevel.STRONG
    ]
    weaknesses = [
        f"Needs more evidence for {criteria_by_id[result.criterion_id].name}."
        for result in criteria_results
        if result.match_level in {MatchLevel.WEAK, MatchLevel.MISSING}
        and criteria_by_id[result.criterion_id].importance >= 4
    ]

    missing_keywords: list[str] = []
    for result in criteria_results:
        criterion = criteria_by_id[result.criterion_id]
        for keyword in criterion.keywords:
            if keyword in result.missing_evidence:
                missing_keywords.append(keyword)

    truthfulness_warnings: list[str] = []
    for result in criteria_results:
        if "truthfulness" in result.criterion_id or result.risk_level.value in {"medium", "high"}:
            for evidence in result.evidence_found:
                if any(term in evidence.lower() for term in ["unsupported", "needs_confirmation", "risk flag"]):
                    truthfulness_warnings.append(evidence)
    truthfulness_warnings.append("Metrics should only be included when user-provided and verifiable.")

    if (
        classification_result is not None
        and classification_result.primary_resume_type not in criteria_profile.resume_types
    ):
        truthfulness_warnings.append(
            "Classification result primary resume type is not listed in the selected criteria profile resume_types."
        )

    return GapAnalysisResult(
        profile_id=criteria_profile.profile_id,
        overall_match_level=_overall_match_level(weighted_score),
        criteria_results=criteria_results,
        strengths=_dedupe(strengths)[:8],
        weaknesses=_dedupe(weaknesses)[:8],
        missing_keywords=_dedupe(missing_keywords),
        truthfulness_warnings=_dedupe(truthfulness_warnings),
    )
