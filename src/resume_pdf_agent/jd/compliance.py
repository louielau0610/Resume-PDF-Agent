"""Deterministic JD compliance checker for M15.

Checks user-provided JD text for confidential/internal/leaked content
markers before allowing parsing.
"""

from __future__ import annotations

import uuid

from resume_pdf_agent.models.enums import RiskLevel
from resume_pdf_agent.models.jd import (
    JDComplianceIssue,
    JDComplianceIssueType,
    JDComplianceResult,
    JDComplianceStatus,
    JDSourceType,
)

# ── Blocking phrases (high-confidence confidential/internal markers) ────
_BLOCKING_PHRASES: list[tuple[str, JDComplianceIssueType]] = [
    ("confidential", JDComplianceIssueType.CONFIDENTIAL_MARKER),
    ("internal use only", JDComplianceIssueType.INTERNAL_USE_MARKER),
    ("do not distribute", JDComplianceIssueType.CONFIDENTIAL_MARKER),
    ("proprietary hiring rubric", JDComplianceIssueType.LEAKED_RUBRIC_RISK),
    ("private recruiter notes", JDComplianceIssueType.PRIVATE_CANDIDATE_EVALUATION_RISK),
    ("candidate evaluation form", JDComplianceIssueType.PRIVATE_CANDIDATE_EVALUATION_RISK),
    ("interview scorecard", JDComplianceIssueType.PRIVATE_CANDIDATE_EVALUATION_RISK),
    ("scoring rubric", JDComplianceIssueType.LEAKED_RUBRIC_RISK),
    ("resume screening algorithm", JDComplianceIssueType.LEAKED_RUBRIC_RISK),
    ("not for public release", JDComplianceIssueType.ACCESS_CONTROL_RISK),
    ("restricted access", JDComplianceIssueType.ACCESS_CONTROL_RISK),
]

# ── Warning phrases (medium-risk, ambiguous context) ────────────────────
_WARNING_PHRASES: list[tuple[str, JDComplianceIssueType]] = [
    ("recruiter screen", JDComplianceIssueType.GENERIC_COMPLIANCE_WARNING),
    ("hiring manager notes", JDComplianceIssueType.GENERIC_COMPLIANCE_WARNING),
    ("assessment criteria", JDComplianceIssueType.GENERIC_COMPLIANCE_WARNING),
    ("interview feedback", JDComplianceIssueType.PRIVATE_CANDIDATE_EVALUATION_RISK),
    ("evaluation criteria", JDComplianceIssueType.GENERIC_COMPLIANCE_WARNING),
]


def _make_issue_id() -> str:
    return f"jd_comp_{uuid.uuid4().hex[:8]}"


def check_jd_compliance(
    jd_text: str,
    source_type: JDSourceType = JDSourceType.USER_PROVIDED_TEXT,
) -> JDComplianceResult:
    """Run deterministic compliance checks on user-provided JD text.

    Parameters
    ----------
    jd_text : str
        The raw JD text to check.
    source_type : JDSourceType
        How the JD was provided.

    Returns
    -------
    JDComplianceResult
        Structured compliance result.
    """
    text_lower = jd_text.lower()
    issues: list[JDComplianceIssue] = []
    warnings_list: list[str] = []

    # ── Check blocking phrases ─────────────────────────────────────────
    for phrase, issue_type in _BLOCKING_PHRASES:
        if phrase in text_lower:
            issues.append(
                JDComplianceIssue(
                    issue_id=_make_issue_id(),
                    issue_type=issue_type,
                    severity=RiskLevel.HIGH,
                    matched_text=phrase,
                    reason=f"JD text contains '{phrase}', which suggests confidential or internal content.",
                    suggested_action=(
                        "请仅使用公开发布的岗位描述。"
                        "不要使用标记为机密、内部使用或限制访问的内容。"
                    ),
                )
            )

    # ── Check warning phrases ──────────────────────────────────────────
    for phrase, issue_type in _WARNING_PHRASES:
        if phrase in text_lower:
            issues.append(
                JDComplianceIssue(
                    issue_id=_make_issue_id(),
                    issue_type=issue_type,
                    severity=RiskLevel.MEDIUM,
                    matched_text=phrase,
                    reason=f"JD text contains '{phrase}', which may suggest non-public evaluation content.",
                    suggested_action=(
                        "请确认该内容是公开发布的岗位描述，而非内部评估表。"
                    ),
                )
            )

    # ── Check source type ──────────────────────────────────────────────
    if source_type == JDSourceType.UNKNOWN:
        warnings_list.append(
            "JD source type is unknown. 请确认内容来自公开发布的岗位描述。"
        )
        issues.append(
            JDComplianceIssue(
                issue_id=_make_issue_id(),
                issue_type=JDComplianceIssueType.UNKNOWN_SOURCE_WARNING,
                severity=RiskLevel.LOW,
                matched_text="unknown source",
                reason="JD source type is unknown.",
                suggested_action="请明确标注 JD 来源为公开发布的岗位描述。",
            )
        )

    # ── Determine status ───────────────────────────────────────────────
    high_severity = [i for i in issues if i.severity == RiskLevel.HIGH]
    medium_severity = [i for i in issues if i.severity == RiskLevel.MEDIUM]

    if high_severity:
        status = JDComplianceStatus.BLOCKED
        can_parse = False
    elif medium_severity:
        status = JDComplianceStatus.ALLOWED_WITH_WARNINGS
        can_parse = True
    else:
        status = JDComplianceStatus.ALLOWED
        can_parse = True

    # ── Summary ────────────────────────────────────────────────────────
    if status == JDComplianceStatus.BLOCKED:
        summary = (
            f"JD 合规检查：已阻止。发现 {len(high_severity)} 个高风险问题。"
            f"请使用公开发布的岗位描述，不要使用机密或内部评估内容。"
        )
    elif status == JDComplianceStatus.ALLOWED_WITH_WARNINGS:
        summary = (
            f"JD 合规检查：允许但有警告。发现 {len(medium_severity)} 个需注意的问题。"
        )
    else:
        summary = "JD 合规检查：通过。内容看起来是公开发布的岗位描述。"

    return JDComplianceResult(
        status=status,
        source_type=source_type,
        issues=issues,
        warnings=warnings_list,
        can_parse=can_parse,
        summary=summary,
    )
