from resume_pdf_agent.classifier import classify_resume_type
from resume_pdf_agent.gap_analysis import analyze_criteria_gap
from resume_pdf_agent.models import (
    EducationEntry,
    EvidenceLevel,
    ExportFormat,
    MatchLevel,
    MetricStatus,
    ResumeBullet,
    ResumeContent,
    ResumeSection,
    ResumeType,
    UserProfile,
)
from resume_pdf_agent.pipeline import run_resume_pipeline
from resume_pdf_agent.sample_data import SAMPLE_CRITERIA_PROFILE, SAMPLE_USER_PROFILE


def _content_with_bullet(**overrides):
    data = {
        "text": "Claim needs review.",
        "evidence_level": EvidenceLevel.USER_PROVIDED,
        "metric_status": MetricStatus.NOT_APPLICABLE,
        "needs_confirmation": False,
        "risk_flags": [],
    }
    data.update(overrides)
    return ResumeContent(
        resume_type=ResumeType.DATA_SCIENCE_RESUME,
        sections=[ResumeSection(heading="Projects", bullets=[ResumeBullet(**data)])],
    )


def test_unsupported_evidence_level_produces_truthfulness_warning():
    result = analyze_criteria_gap(
        SAMPLE_USER_PROFILE,
        SAMPLE_CRITERIA_PROFILE,
        _content_with_bullet(evidence_level=EvidenceLevel.UNSUPPORTED),
    )

    assert any("unsupported evidence" in warning.lower() for warning in result.truthfulness_warnings)


def test_unsupported_metric_status_produces_truthfulness_warning():
    result = analyze_criteria_gap(
        SAMPLE_USER_PROFILE,
        SAMPLE_CRITERIA_PROFILE,
        _content_with_bullet(metric_status=MetricStatus.UNSUPPORTED),
    )

    assert any("unsupported metric" in warning.lower() for warning in result.truthfulness_warnings)


def test_needs_confirmation_produces_truthfulness_warning():
    result = analyze_criteria_gap(
        SAMPLE_USER_PROFILE,
        SAMPLE_CRITERIA_PROFILE,
        _content_with_bullet(needs_confirmation=True),
    )

    assert any("needs_confirmation" in warning for warning in result.truthfulness_warnings)


def test_risk_flags_produce_truthfulness_warning():
    result = analyze_criteria_gap(
        SAMPLE_USER_PROFILE,
        SAMPLE_CRITERIA_PROFILE,
        _content_with_bullet(risk_flags=["unsupported_metric"]),
    )

    assert any("risk flag" in warning.lower() for warning in result.truthfulness_warnings)


def test_ats_readability_does_not_parse_pdf_files():
    result = analyze_criteria_gap(SAMPLE_USER_PROFILE, SAMPLE_CRITERIA_PROFILE, None)
    ats_result = next(item for item in result.criteria_results if item.criterion_id == "ds_ats_readability")

    assert ats_result.match_level in {MatchLevel.WEAK, MatchLevel.NOT_APPLICABLE}
    assert "PDF" not in " ".join(ats_result.evidence_found + ats_result.suggested_actions)


def test_classification_result_mismatch_creates_warning():
    profile = UserProfile(
        full_name="Mismatch",
        education=[
            EducationEntry(
                institution="Example University",
                degree="Bachelor",
                major="Finance",
            )
        ],
        target_roles=["Finance Intern"],
    )
    classification = classify_resume_type(profile)

    result = analyze_criteria_gap(
        SAMPLE_USER_PROFILE,
        SAMPLE_CRITERIA_PROFILE,
        classification_result=classification,
    )

    assert any("primary resume type is not listed" in warning for warning in result.truthfulness_warnings)


def test_gap_analysis_output_avoids_probability_and_internal_access_claims():
    result = analyze_criteria_gap(SAMPLE_USER_PROFILE, SAMPLE_CRITERIA_PROFILE, None)
    text = " ".join(
        [
            " ".join(result.strengths),
            " ".join(result.weaknesses),
            " ".join(result.missing_keywords),
            " ".join(result.truthfulness_warnings),
            *[
                " ".join(item.evidence_found + item.missing_evidence + item.suggested_actions)
                for item in result.criteria_results
            ],
        ]
    ).lower()

    assert "hiring probability" not in text
    assert "offer probability" not in text
    assert "internal company screening" not in text


def test_pipeline_placeholder_still_includes_gap_analysis_and_criteria_aware_stages():
    result = run_resume_pipeline({"target_role": "data science intern"})

    assert "gap_analysis" in result["stages"]
    assert "criteria_aware_content_enhancement" in result["stages"]
    assert "resume_type_classification" in result["stages"]
    assert "M10 integrated" in result["message"]


def test_export_format_still_only_includes_pdf():
    assert [item.value for item in ExportFormat] == ["pdf"]
