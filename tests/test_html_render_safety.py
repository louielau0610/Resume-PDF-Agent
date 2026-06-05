from resume_pdf_agent.models import (
    BulletEnhancementMode,
    BulletEnhancementResult,
    BulletEnhancementStatus,
    EnhancedBulletCandidate,
    EvidenceLevel,
    ExperienceEnhancementResult,
    MetricStatus,
    ResumeBullet,
    ResumeContent,
    ResumeSection,
    ResumeType,
)
from resume_pdf_agent.rendering import render_resume_html
from resume_pdf_agent.rendering.safety import escape_html_text, is_safe_render_item
from resume_pdf_agent.sample_data import SAMPLE_RESUME_CONTENT, SAMPLE_USER_PROFILE
from resume_pdf_agent.templates import select_internal_template


def test_escape_html_text_escapes_script_input():
    assert escape_html_text("<script>alert(1)</script>") == "&lt;script&gt;alert(1)&lt;/script&gt;"


def test_rendered_html_escapes_user_provided_script_content():
    content = SAMPLE_RESUME_CONTENT.model_copy(
        update={
            "sections": [
                ResumeSection(
                    heading="Projects",
                    bullets=[
                        ResumeBullet(
                            text="<script>alert('x')</script> Built a safe parser.",
                            evidence_level=EvidenceLevel.USER_PROVIDED,
                            metric_status=MetricStatus.NOT_APPLICABLE,
                        )
                    ],
                )
            ]
        },
        deep=True,
    )
    selection = select_internal_template(SAMPLE_USER_PROFILE, content)

    result = render_resume_html(SAMPLE_USER_PROFILE, content, selection)

    assert "<script>" not in result.html
    assert "&lt;script&gt;" in result.html


def test_safe_enhanced_bullet_candidates_are_used_when_available():
    selection = select_internal_template(SAMPLE_USER_PROFILE, SAMPLE_RESUME_CONTENT)
    enhancement = BulletEnhancementResult(
        resume_type=ResumeType.DATA_SCIENCE_RESUME,
        experience_results=[
            ExperienceEnhancementResult(
                experience_id="exp_project_course_recommender",
                title="Course Recommendation Analysis Project",
                candidates=[
                    EnhancedBulletCandidate(
                        candidate_id="cand_1",
                        source_experience_id="exp_project_course_recommender",
                        original_text="Original project bullet.",
                        enhanced_text="Enhanced safe project bullet using Python and reproducible analysis.",
                        mode=BulletEnhancementMode.CRITERIA_ALIGNMENT,
                        status=BulletEnhancementStatus.ENHANCED,
                        evidence_level=EvidenceLevel.USER_PROVIDED,
                        metric_status=MetricStatus.NOT_APPLICABLE,
                        rationale="Uses user-provided project evidence.",
                    )
                ],
            )
        ],
        candidates_generated=1,
        candidates_requiring_confirmation=0,
        safe_candidates_count=1,
        summary="Generated one safe candidate.",
    )

    result = render_resume_html(SAMPLE_USER_PROFILE, SAMPLE_RESUME_CONTENT, selection, enhancement)

    assert "Enhanced safe project bullet" in result.html


def test_high_risk_or_confirmation_needed_items_produce_warnings():
    content = SAMPLE_RESUME_CONTENT.model_copy(
        update={
            "sections": [
                ResumeSection(
                    heading="Projects",
                    bullets=[
                        ResumeBullet(
                            text="Claim requiring confirmation.",
                            evidence_level=EvidenceLevel.NEEDS_USER_CONFIRMATION,
                            metric_status=MetricStatus.NOT_APPLICABLE,
                            risk_flags=["truthfulness_risk"],
                        )
                    ],
                )
            ]
        },
        deep=True,
    )
    selection = select_internal_template(SAMPLE_USER_PROFILE, content)

    result = render_resume_html(SAMPLE_USER_PROFILE, content, selection)

    assert result.warnings
    assert any("needs user confirmation" in warning for warning in result.warnings)
    assert any("risk flags" in warning for warning in result.warnings)


def test_is_safe_render_item_blocks_high_risk_and_optional_confirmation():
    assert is_safe_render_item(False, []) is True
    assert is_safe_render_item(False, ["unsupported"]) is False
    assert is_safe_render_item(True, [], include_confirmation_needed=False) is False
