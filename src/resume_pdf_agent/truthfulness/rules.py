"""Rule-based truthfulness checks for resume claims."""

import re

from resume_pdf_agent.models import (
    ClaimEvidenceStatus,
    EvidenceLevel,
    Metric,
    MetricStatus,
    ResumeClaim,
    TruthfulnessIssue,
    TruthfulnessIssueType,
    TruthfulnessSeverity,
)

_IMPACT_TERMS = [
    "increased",
    "reduced",
    "improved",
    "optimized",
    "saved",
    "generated",
    "ranked",
    "top",
    "users",
    "revenue",
    "accuracy",
    "runtime",
]
_STRONG_LEADERSHIP_TERMS = [
    "led",
    "owned",
    "directed",
    "managed",
    "spearheaded",
    "founded",
    "architected",
    "designed end-to-end",
    "independently built",
]
_WEAK_CONTRIBUTION_TERMS = [
    "assisted",
    "supported",
    "contributed",
    "participated",
    "helped",
    "collaborated",
    "coursework",
    "team project",
]
_TOOL_OR_METHOD_TERMS = [
    "python",
    "sql",
    "pandas",
    "numpy",
    "scikit-learn",
    "react",
    "fastapi",
    "docker",
    "excel",
    "tableau",
    "regression",
    "classification",
    "model evaluation",
]


def _issue_id(claim: ResumeClaim, issue_type: TruthfulnessIssueType, suffix: str | None = None) -> str:
    base = f"{claim.claim_id}:{issue_type.value}"
    return f"{base}:{suffix}" if suffix else base


def _issue(
    claim: ResumeClaim,
    issue_type: TruthfulnessIssueType,
    severity: TruthfulnessSeverity,
    evidence_status: ClaimEvidenceStatus,
    reason: str,
    suggested_action: str,
    suffix: str | None = None,
) -> TruthfulnessIssue:
    return TruthfulnessIssue(
        issue_id=_issue_id(claim, issue_type, suffix),
        issue_type=issue_type,
        severity=severity,
        source_type=claim.source_type,
        source_id=claim.source_id,
        claim_text=claim.text,
        evidence_status=evidence_status,
        reason=reason,
        suggested_action=suggested_action,
        related_criteria_ids=claim.targeted_criteria_ids,
    )


def has_numeric_or_percentage_claim(text: str) -> bool:
    """Return true when text contains numeric or impact wording."""

    lowered = text.lower()
    return bool(re.search(r"\b\d+(\.\d+)?%?\b", lowered)) or any(term in lowered for term in _IMPACT_TERMS)


def has_strong_leadership_verb(text: str) -> bool:
    """Return true when text uses strong ownership wording."""

    lowered = text.lower()
    return any(term in lowered for term in _STRONG_LEADERSHIP_TERMS)


def detect_unsupported_evidence_issue(claim: ResumeClaim) -> TruthfulnessIssue | None:
    if claim.evidence_level != EvidenceLevel.UNSUPPORTED:
        return None
    return _issue(
        claim,
        TruthfulnessIssueType.UNSUPPORTED_EVIDENCE,
        TruthfulnessSeverity.HIGH,
        ClaimEvidenceStatus.UNSUPPORTED,
        "Claim is explicitly marked with unsupported evidence.",
        "Remove the claim, verify it, or provide user evidence before final resume generation.",
    )


def detect_unsupported_metric_issue(claim: ResumeClaim) -> TruthfulnessIssue | None:
    if claim.metric_status != MetricStatus.UNSUPPORTED:
        return None
    return _issue(
        claim,
        TruthfulnessIssueType.UNSUPPORTED_METRIC,
        TruthfulnessSeverity.HIGH,
        ClaimEvidenceStatus.UNSUPPORTED,
        "Claim is explicitly marked with unsupported metric status.",
        "Remove the metric or provide verifiable source evidence.",
    )


def detect_needs_confirmation_issue(claim: ResumeClaim) -> TruthfulnessIssue | None:
    if not claim.needs_confirmation:
        return None
    return _issue(
        claim,
        TruthfulnessIssueType.NEEDS_CONFIRMATION,
        TruthfulnessSeverity.MEDIUM,
        ClaimEvidenceStatus.NEEDS_USER_CONFIRMATION,
        "Claim is marked as needing user confirmation.",
        "Ask the user to verify the claim before final resume generation.",
    )


def detect_risk_flag_issues(claim: ResumeClaim) -> list[TruthfulnessIssue]:
    return [
        _issue(
            claim,
            TruthfulnessIssueType.RISK_FLAG,
            TruthfulnessSeverity.MEDIUM,
            ClaimEvidenceStatus.NEEDS_USER_CONFIRMATION,
            f"Claim has risk flag: {risk_flag}.",
            f"Review and resolve the risk flag '{risk_flag}' before final resume generation.",
            suffix=risk_flag,
        )
        for risk_flag in claim.risk_flags
    ]


def _metric_source_text(source_experience_metrics: list[Metric] | None) -> str:
    if not source_experience_metrics:
        return ""
    parts = []
    for metric in source_experience_metrics:
        parts.extend([metric.name, metric.value, metric.unit or "", metric.context or "", metric.source_note or ""])
    return " ".join(parts).lower()


def detect_unverifiable_quantified_claim(
    claim: ResumeClaim,
    source_experience_metrics: list[Metric] | None = None,
) -> TruthfulnessIssue | None:
    if not has_numeric_or_percentage_claim(claim.text):
        return None
    if claim.metric_status == MetricStatus.USER_PROVIDED:
        return None
    metric_text = _metric_source_text(source_experience_metrics)
    if metric_text and any(token in metric_text for token in re.findall(r"\d+(?:\.\d+)?%?", claim.text.lower())):
        return None
    severity = TruthfulnessSeverity.HIGH if claim.evidence_level == EvidenceLevel.UNSUPPORTED else TruthfulnessSeverity.MEDIUM
    issue_type = (
        TruthfulnessIssueType.METRIC_WITHOUT_SOURCE
        if claim.source_type == "metric"
        else TruthfulnessIssueType.UNVERIFIABLE_QUANTIFIED_CLAIM
    )
    return _issue(
        claim,
        issue_type,
        severity,
        ClaimEvidenceStatus.UNVERIFIABLE,
        "Claim contains quantified or impact wording without user-provided metric evidence.",
        "Ask the user to provide verifiable metric evidence or remove the quantified claim.",
    )


def detect_leadership_exaggeration_risk(
    claim: ResumeClaim,
    source_experience_text: str | None = None,
) -> TruthfulnessIssue | None:
    if not has_strong_leadership_verb(claim.text):
        return None
    source_text = (source_experience_text or "").lower()
    if any(term in source_text for term in _STRONG_LEADERSHIP_TERMS):
        return None
    if claim.needs_confirmation or any(term in source_text for term in _WEAK_CONTRIBUTION_TERMS):
        return _issue(
            claim,
            TruthfulnessIssueType.LEADERSHIP_EXAGGERATION_RISK,
            TruthfulnessSeverity.MEDIUM,
            ClaimEvidenceStatus.NEEDS_USER_CONFIRMATION,
            "Claim uses strong ownership wording while source evidence suggests partial contribution or needs confirmation.",
            "Ask the user to clarify the actual responsibility level.",
        )
    return None


def detect_tool_or_method_not_supported(
    claim: ResumeClaim,
    source_experience_text: str | None = None,
) -> TruthfulnessIssue | None:
    if claim.source_type not in {"resume_bullet", "summary"}:
        return None
    source_text = (source_experience_text or "").lower()
    if not source_text:
        return None
    unsupported_terms = [
        term for term in _TOOL_OR_METHOD_TERMS if term in claim.normalized_text and term not in source_text
    ]
    if not unsupported_terms:
        return None
    return _issue(
        claim,
        TruthfulnessIssueType.TOOL_OR_METHOD_NOT_SUPPORTED,
        TruthfulnessSeverity.LOW,
        ClaimEvidenceStatus.NEEDS_USER_CONFIRMATION,
        f"Claim mentions tool or method not visible in the source experience: {unsupported_terms[0]}.",
        "Ask the user to confirm whether the tool or method was actually used.",
        suffix=unsupported_terms[0],
    )
