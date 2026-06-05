from copy import deepcopy

from resume_pdf_agent.models import (
    CriteriaMatchResult,
    EvidenceLevel,
    ExperienceEntry,
    ExperienceType,
    GapAnalysisResult,
    MatchLevel,
    Metric,
    MetricStatus,
    ResumeBullet,
    ResumeContent,
    ResumeSection,
    ResumeType,
    RiskLevel,
    TruthfulnessIssueType,
)
from resume_pdf_agent.truthfulness import check_truthfulness


def _content_with_bullet(bullet: ResumeBullet, experience: ExperienceEntry | None = None) -> ResumeContent:
    return ResumeContent(
        resume_type=ResumeType.DATA_SCIENCE_RESUME,
        experiences=[experience] if experience else [],
        sections=[ResumeSection(heading="Projects", bullets=[bullet])],
    )


def _issue_types(result):
    return [issue.issue_type for issue in result.issues]


def test_check_truthfulness_can_be_imported():
    assert callable(check_truthfulness)


def test_unsupported_evidence_creates_high_severity_issue():
    result = check_truthfulness(
        _content_with_bullet(
            ResumeBullet(
                text="Unsupported claim.",
                evidence_level=EvidenceLevel.UNSUPPORTED,
                metric_status=MetricStatus.NOT_APPLICABLE,
            )
        )
    )

    assert TruthfulnessIssueType.UNSUPPORTED_EVIDENCE in _issue_types(result)
    assert result.high_risk_count >= 1
    assert result.safe_to_proceed is False


def test_unsupported_metric_creates_high_severity_issue():
    result = check_truthfulness(
        _content_with_bullet(
            ResumeBullet(
                text="Improved accuracy by 20%.",
                evidence_level=EvidenceLevel.USER_PROVIDED,
                metric_status=MetricStatus.UNSUPPORTED,
            )
        )
    )

    assert TruthfulnessIssueType.UNSUPPORTED_METRIC in _issue_types(result)
    assert result.high_risk_count >= 1


def test_needs_confirmation_and_risk_flags_create_issues():
    result = check_truthfulness(
        _content_with_bullet(
            ResumeBullet(
                text="Claim needs confirmation.",
                evidence_level=EvidenceLevel.USER_PROVIDED,
                metric_status=MetricStatus.NOT_APPLICABLE,
                needs_confirmation=True,
                risk_flags=["unclear_scope"],
            )
        )
    )

    assert TruthfulnessIssueType.NEEDS_CONFIRMATION in _issue_types(result)
    assert TruthfulnessIssueType.RISK_FLAG in _issue_types(result)
    assert result.medium_risk_count >= 2


def test_unverifiable_quantified_claim_without_user_metric_is_flagged():
    result = check_truthfulness(
        _content_with_bullet(
            ResumeBullet(
                text="Improved model accuracy by 30%.",
                evidence_level=EvidenceLevel.USER_PROVIDED,
                metric_status=MetricStatus.MISSING,
            )
        )
    )

    assert TruthfulnessIssueType.UNVERIFIABLE_QUANTIFIED_CLAIM in _issue_types(result)


def test_user_provided_metric_status_does_not_create_unsupported_metric_issue():
    result = check_truthfulness(
        _content_with_bullet(
            ResumeBullet(
                text="Improved model accuracy by 30%.",
                evidence_level=EvidenceLevel.USER_PROVIDED,
                metric_status=MetricStatus.USER_PROVIDED,
            )
        )
    )

    assert TruthfulnessIssueType.UNSUPPORTED_METRIC not in _issue_types(result)


def test_missing_metrics_do_not_fabricate_metrics():
    result = check_truthfulness(
        _content_with_bullet(
            ResumeBullet(
                text="Analyzed data and prepared report.",
                evidence_level=EvidenceLevel.USER_PROVIDED,
                metric_status=MetricStatus.MISSING,
            )
        )
    )

    text = " ".join(issue.claim_text + issue.suggested_action for issue in result.issues)
    assert "30%" not in text


def test_leadership_exaggeration_is_flagged_conservatively():
    experience = ExperienceEntry(
        experience_id="exp_1",
        experience_type=ExperienceType.PROJECT,
        title="Team Project",
        raw_description="Assisted and supported a team project.",
    )
    result = check_truthfulness(
        _content_with_bullet(
            ResumeBullet(
                text="Led the team project end-to-end.",
                source_experience_id="exp_1",
                evidence_level=EvidenceLevel.USER_PROVIDED,
                metric_status=MetricStatus.NOT_APPLICABLE,
            ),
            experience,
        )
    )

    assert TruthfulnessIssueType.LEADERSHIP_EXAGGERATION_RISK in _issue_types(result)


def test_leadership_word_supported_by_source_is_not_automatically_flagged():
    experience = ExperienceEntry(
        experience_id="exp_1",
        experience_type=ExperienceType.PROJECT,
        title="Team Project",
        raw_description="Led planning for the team project.",
    )
    result = check_truthfulness(
        _content_with_bullet(
            ResumeBullet(
                text="Led planning for the team project.",
                source_experience_id="exp_1",
                evidence_level=EvidenceLevel.USER_PROVIDED,
                metric_status=MetricStatus.NOT_APPLICABLE,
            ),
            experience,
        )
    )

    assert TruthfulnessIssueType.LEADERSHIP_EXAGGERATION_RISK not in _issue_types(result)


def test_tool_claim_not_supported_by_source_is_flagged_conservatively():
    experience = ExperienceEntry(
        experience_id="exp_1",
        experience_type=ExperienceType.PROJECT,
        title="Analysis Project",
        tools_used=["Excel"],
    )
    result = check_truthfulness(
        _content_with_bullet(
            ResumeBullet(
                text="Built analysis with Python.",
                source_experience_id="exp_1",
                evidence_level=EvidenceLevel.USER_PROVIDED,
                metric_status=MetricStatus.NOT_APPLICABLE,
            ),
            experience,
        )
    )

    assert TruthfulnessIssueType.TOOL_OR_METHOD_NOT_SUPPORTED in _issue_types(result)


def test_supported_tool_claim_is_not_flagged():
    experience = ExperienceEntry(
        experience_id="exp_1",
        experience_type=ExperienceType.PROJECT,
        title="Analysis Project",
        tools_used=["Python"],
    )
    result = check_truthfulness(
        _content_with_bullet(
            ResumeBullet(
                text="Built analysis with Python.",
                source_experience_id="exp_1",
                evidence_level=EvidenceLevel.USER_PROVIDED,
                metric_status=MetricStatus.NOT_APPLICABLE,
            ),
            experience,
        )
    )

    assert TruthfulnessIssueType.TOOL_OR_METHOD_NOT_SUPPORTED not in _issue_types(result)


def test_gap_analysis_warnings_are_converted_to_issues():
    gap_result = GapAnalysisResult(
        profile_id="profile_1",
        overall_match_level=MatchLevel.WEAK,
        criteria_results=[
            CriteriaMatchResult(
                criterion_id="criterion_1",
                match_level=MatchLevel.WEAK,
                risk_level=RiskLevel.MEDIUM,
            )
        ],
        truthfulness_warnings=["Unsupported metric should be reviewed."],
    )
    result = check_truthfulness(
        _content_with_bullet(
            ResumeBullet(
                text="Analyzed data.",
                evidence_level=EvidenceLevel.USER_PROVIDED,
                metric_status=MetricStatus.NOT_APPLICABLE,
            )
        ),
        gap_result,
    )

    assert TruthfulnessIssueType.GAP_ANALYSIS_WARNING in _issue_types(result)


def test_checker_does_not_mutate_resume_content():
    content = _content_with_bullet(
        ResumeBullet(
            text="Analyzed data.",
            evidence_level=EvidenceLevel.USER_PROVIDED,
            metric_status=MetricStatus.NOT_APPLICABLE,
        )
    )
    before = deepcopy(content)

    check_truthfulness(content)

    assert content == before


def test_safe_to_proceed_true_when_no_high_risk_issues():
    content = ResumeContent(
        resume_type=ResumeType.DATA_SCIENCE_RESUME,
        experiences=[
            ExperienceEntry(
                experience_id="exp_1",
                experience_type=ExperienceType.PROJECT,
                title="Analysis Project",
                tools_used=["Python"],
                metrics=[Metric(name="accuracy", value="0.82", source_note="user provided")],
            )
        ],
        sections=[
            ResumeSection(
                heading="Projects",
                bullets=[
                    ResumeBullet(
                        text="Used Python in an analysis project.",
                        source_experience_id="exp_1",
                        evidence_level=EvidenceLevel.USER_PROVIDED,
                        metric_status=MetricStatus.NOT_APPLICABLE,
                    )
                ],
            )
        ],
    )

    result = check_truthfulness(content)

    assert result.high_risk_count == 0
    assert result.safe_to_proceed is True
