"""Main deterministic criteria-aware bullet enhancement engine."""

from resume_pdf_agent.enhancement.bullet_builder import build_enhanced_bullet_text
from resume_pdf_agent.enhancement.safeguards import (
    collect_truthfulness_blockers,
    has_high_risk_truthfulness_issue,
)
from resume_pdf_agent.models import (
    BulletEnhancementMode,
    BulletEnhancementResult,
    BulletEnhancementStatus,
    EnhancedBulletCandidate,
    EvidenceLevel,
    ExperienceEnhancementResult,
    GapAnalysisResult,
    MatchLevel,
    MetricStatus,
    ResumeContent,
    RoleCriteriaProfile,
    ScreeningCriterion,
    TruthfulnessCheckResult,
)


def _criteria_for_experience(
    criteria_profile: RoleCriteriaProfile | None,
    gap_analysis_result: GapAnalysisResult | None,
) -> list[ScreeningCriterion]:
    if criteria_profile is None:
        return []
    criteria = criteria_profile.criteria
    if gap_analysis_result is None:
        return criteria[:3]
    weak_or_medium = {
        result.criterion_id
        for result in gap_analysis_result.criteria_results
        if result.match_level in {MatchLevel.WEAK, MatchLevel.MEDIUM, MatchLevel.MISSING}
    }
    selected = [criterion for criterion in criteria if criterion.criterion_id in weak_or_medium]
    return selected or criteria[:3]


def enhance_resume_bullets(
    resume_content: ResumeContent,
    criteria_profile: RoleCriteriaProfile | None = None,
    gap_analysis_result: GapAnalysisResult | None = None,
    truthfulness_result: TruthfulnessCheckResult | None = None,
    max_candidates_per_experience: int = 3,
) -> BulletEnhancementResult:
    """Generate conservative source-supported bullet candidates."""

    global_warnings: list[str] = []
    truthfulness_blockers = collect_truthfulness_blockers(truthfulness_result)
    if truthfulness_blockers:
        global_warnings.append("High-risk truthfulness issues exist; unsafe experiences are skipped.")

    criteria = _criteria_for_experience(criteria_profile, gap_analysis_result)
    experience_results: list[ExperienceEnhancementResult] = []

    for experience in resume_content.experiences:
        skipped_reasons: list[str] = []
        candidates: list[EnhancedBulletCandidate] = []
        blockers = collect_truthfulness_blockers(truthfulness_result, experience.experience_id)
        if has_high_risk_truthfulness_issue(truthfulness_result, experience.experience_id):
            skipped_reasons.extend(blockers or ["High-risk truthfulness issue blocks enhancement."])
            experience_results.append(
                ExperienceEnhancementResult(
                    experience_id=experience.experience_id,
                    title=experience.title,
                    candidates=[],
                    skipped_reasons=skipped_reasons,
                )
            )
            continue

        if not any([experience.raw_description, experience.responsibilities, experience.tools_used, experience.methods_used, experience.outcomes]):
            skipped_reasons.append("Insufficient source evidence to build an enhanced bullet.")
            candidates.append(
                EnhancedBulletCandidate(
                    candidate_id=f"{experience.experience_id}:insufficient:0",
                    source_experience_id=experience.experience_id,
                    original_text=None,
                    enhanced_text=f"Insufficient evidence for {experience.title}.",
                    mode=BulletEnhancementMode.CONSERVATIVE_REWRITE,
                    status=BulletEnhancementStatus.INSUFFICIENT_EVIDENCE,
                    targeted_criteria_ids=[],
                    evidence_level=EvidenceLevel.NEEDS_USER_CONFIRMATION,
                    metric_status=MetricStatus.NOT_APPLICABLE,
                    needs_confirmation=True,
                    risk_flags=["insufficient_evidence"],
                    rationale="Source experience lacks enough concrete evidence for safe enhancement.",
                )
            )
        else:
            selected_criteria = criteria[: max(1, max_candidates_per_experience)]
            if not selected_criteria:
                selected_criteria = []
            for index in range(max(1, min(max_candidates_per_experience, max(1, len(selected_criteria))))):
                targeted = selected_criteria[index : index + 1]
                text = build_enhanced_bullet_text(experience, targeted)
                if text is None:
                    skipped_reasons.append("No meaningful source evidence to build an enhanced bullet.")
                    continue
                weak_source = not experience.outcomes and not experience.evidence_notes
                candidates.append(
                    EnhancedBulletCandidate(
                        candidate_id=f"{experience.experience_id}:candidate:{index}",
                        source_experience_id=experience.experience_id,
                        original_text=experience.raw_description or (experience.responsibilities[0] if experience.responsibilities else None),
                        enhanced_text=text,
                        mode=BulletEnhancementMode.CRITERIA_ALIGNMENT if targeted else BulletEnhancementMode.CONSERVATIVE_REWRITE,
                        status=BulletEnhancementStatus.NEEDS_USER_CONFIRMATION if weak_source else BulletEnhancementStatus.ENHANCED,
                        targeted_criteria_ids=[criterion.criterion_id for criterion in targeted],
                        evidence_level=EvidenceLevel.NEEDS_USER_CONFIRMATION if weak_source else EvidenceLevel.USER_PROVIDED,
                        metric_status=MetricStatus.USER_PROVIDED if experience.metrics else MetricStatus.NOT_APPLICABLE,
                        needs_confirmation=weak_source,
                        risk_flags=["weak_source_evidence"] if weak_source else [],
                        rationale="Built from source experience fields without adding unsupported tools, outcomes, or metrics.",
                    )
                )

        experience_results.append(
            ExperienceEnhancementResult(
                experience_id=experience.experience_id,
                title=experience.title,
                candidates=candidates[:max_candidates_per_experience],
                skipped_reasons=skipped_reasons,
            )
        )

    all_candidates = [candidate for result in experience_results for candidate in result.candidates]
    requiring_confirmation = sum(1 for candidate in all_candidates if candidate.needs_confirmation)
    safe_count = sum(
        1
        for candidate in all_candidates
        if not candidate.needs_confirmation and candidate.status == BulletEnhancementStatus.ENHANCED
    )
    return BulletEnhancementResult(
        resume_type=resume_content.resume_type,
        experience_results=experience_results,
        global_warnings=global_warnings,
        truthfulness_blockers=truthfulness_blockers,
        candidates_generated=len(all_candidates),
        candidates_requiring_confirmation=requiring_confirmation,
        safe_candidates_count=safe_count,
        summary=(
            f"Generated {len(all_candidates)} deterministic bullet candidate(s) from source-supported evidence. "
            "Candidates are not final verified resume bullets."
        ),
    )
