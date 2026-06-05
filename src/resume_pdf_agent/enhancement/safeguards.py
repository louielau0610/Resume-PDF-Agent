"""Safety helpers for deterministic bullet enhancement."""

from resume_pdf_agent.models import (
    EvidenceLevel,
    Metric,
    MetricStatus,
    TruthfulnessCheckResult,
    TruthfulnessSeverity,
)


def has_high_risk_truthfulness_issue(
    truthfulness_result: TruthfulnessCheckResult | None,
    source_experience_id: str | None = None,
) -> bool:
    """Return true if high-risk issues exist globally or for the source experience."""

    if truthfulness_result is None:
        return False
    for issue in truthfulness_result.issues:
        if issue.severity != TruthfulnessSeverity.HIGH:
            continue
        if source_experience_id is None or issue.source_id in {None, source_experience_id}:
            return True
    return False


def collect_truthfulness_blockers(
    truthfulness_result: TruthfulnessCheckResult | None,
    source_experience_id: str | None = None,
) -> list[str]:
    """Collect high-risk truthfulness blocker reasons."""

    if truthfulness_result is None:
        return []
    blockers = []
    for issue in truthfulness_result.issues:
        if issue.severity == TruthfulnessSeverity.HIGH and (
            source_experience_id is None or issue.source_id in {None, source_experience_id}
        ):
            blockers.append(f"{issue.issue_type.value}: {issue.reason}")
    return list(dict.fromkeys(blockers))


def should_include_metric(metric: Metric) -> bool:
    """Return true only when a metric has source-supported value/context."""

    return bool(metric.name.strip() and metric.value.strip() and (metric.source_note or metric.context))


def sanitize_metric_text(metric: Metric) -> str | None:
    """Build conservative metric text without inventing missing context."""

    if not should_include_metric(metric):
        return None
    parts = [metric.name, metric.value]
    if metric.unit:
        parts.append(metric.unit)
    if metric.context:
        parts.append(f"for {metric.context}")
    return " ".join(parts)


def is_claim_safe_to_enhance(
    evidence_level: EvidenceLevel,
    metric_status: MetricStatus,
    needs_confirmation: bool,
    risk_flags: list[str],
) -> bool:
    """Return false for explicitly unsupported or risky claim metadata."""

    return (
        evidence_level != EvidenceLevel.UNSUPPORTED
        and metric_status != MetricStatus.UNSUPPORTED
        and not needs_confirmation
        and not risk_flags
    )
