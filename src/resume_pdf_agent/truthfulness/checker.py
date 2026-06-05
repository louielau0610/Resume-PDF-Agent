"""Main deterministic truthfulness checker."""

from resume_pdf_agent.models import (
    ClaimEvidenceStatus,
    GapAnalysisResult,
    Metric,
    ResumeContent,
    RiskLevel,
    TruthfulnessCheckResult,
    TruthfulnessIssue,
    TruthfulnessIssueType,
    TruthfulnessSeverity,
)
from resume_pdf_agent.truthfulness.claims import extract_resume_claims
from resume_pdf_agent.truthfulness.rules import (
    detect_leadership_exaggeration_risk,
    detect_needs_confirmation_issue,
    detect_risk_flag_issues,
    detect_tool_or_method_not_supported,
    detect_unsupported_evidence_issue,
    detect_unsupported_metric_issue,
    detect_unverifiable_quantified_claim,
)


def _experience_text_and_metrics(resume_content: ResumeContent) -> tuple[dict[str, str], dict[str, list[Metric]]]:
    text_by_id: dict[str, str] = {}
    metrics_by_id: dict[str, list[Metric]] = {}
    for experience in resume_content.experiences:
        parts = [
            experience.title,
            experience.organization or "",
            experience.raw_description or "",
            *experience.responsibilities,
            *experience.tools_used,
            *experience.methods_used,
            *experience.outcomes,
            *experience.evidence_notes,
        ]
        text_by_id[experience.experience_id] = " ".join(parts).lower()
        metrics_by_id[experience.experience_id] = experience.metrics
    return text_by_id, metrics_by_id


def _gap_warning_issue(index: int, warning: str) -> TruthfulnessIssue:
    lowered = warning.lower()
    severity = TruthfulnessSeverity.HIGH if "unsupported" in lowered and "metric" in lowered else TruthfulnessSeverity.MEDIUM
    return TruthfulnessIssue(
        issue_id=f"gap_analysis_warning:{index}",
        issue_type=TruthfulnessIssueType.GAP_ANALYSIS_WARNING,
        severity=severity,
        source_type="gap_analysis",
        source_id=None,
        claim_text=warning,
        evidence_status=ClaimEvidenceStatus.NEEDS_USER_CONFIRMATION,
        reason="Gap analysis surfaced a truthfulness warning.",
        suggested_action="Review the warning and resolve it before final resume generation.",
        related_criteria_ids=[],
    )


def _dedupe_issues(issues: list[TruthfulnessIssue]) -> list[TruthfulnessIssue]:
    deduped: dict[tuple, TruthfulnessIssue] = {}
    for issue in issues:
        key = (
            issue.issue_type,
            issue.source_type,
            issue.source_id,
            issue.claim_text,
            issue.reason,
            tuple(issue.related_criteria_ids),
        )
        deduped.setdefault(key, issue)
    return list(deduped.values())


def check_truthfulness(
    resume_content: ResumeContent,
    gap_analysis_result: GapAnalysisResult | None = None,
) -> TruthfulnessCheckResult:
    """Check structured resume content for unsupported or risky claims."""

    claims = extract_resume_claims(resume_content)
    experience_text, experience_metrics = _experience_text_and_metrics(resume_content)
    issues: list[TruthfulnessIssue] = []

    for claim in claims:
        source_text = experience_text.get(claim.related_experience_id or "", "")
        source_metrics = experience_metrics.get(claim.related_experience_id or "", [])
        for issue in [
            detect_unsupported_evidence_issue(claim),
            detect_unsupported_metric_issue(claim),
            detect_needs_confirmation_issue(claim),
            detect_unverifiable_quantified_claim(claim, source_metrics),
            detect_leadership_exaggeration_risk(claim, source_text),
            detect_tool_or_method_not_supported(claim, source_text),
        ]:
            if issue is not None:
                issues.append(issue)
        issues.extend(detect_risk_flag_issues(claim))

    if gap_analysis_result is not None:
        issues.extend(
            _gap_warning_issue(index, warning)
            for index, warning in enumerate(gap_analysis_result.truthfulness_warnings)
        )

    issues = _dedupe_issues(issues)
    high_count = sum(1 for issue in issues if issue.severity == TruthfulnessSeverity.HIGH)
    medium_count = sum(1 for issue in issues if issue.severity == TruthfulnessSeverity.MEDIUM)
    low_count = sum(1 for issue in issues if issue.severity in {TruthfulnessSeverity.LOW, TruthfulnessSeverity.INFO})
    overall = RiskLevel.HIGH if high_count else RiskLevel.MEDIUM if medium_count else RiskLevel.LOW
    summary = (
        f"Checked {len(claims)} resume claims and found {len(issues)} truthfulness issue(s). "
        "This deterministic checker surfaces support risks; it does not independently verify real-world truth."
    )

    return TruthfulnessCheckResult(
        overall_risk_level=overall,
        issues=issues,
        warnings=[issue.reason for issue in issues],
        claims_checked=len(claims),
        high_risk_count=high_count,
        medium_risk_count=medium_count,
        low_risk_count=low_count,
        safe_to_proceed=high_count == 0,
        summary=summary,
    )
