from copy import deepcopy

from resume_pdf_agent.enhancement import enhance_resume_bullets
from resume_pdf_agent.models import (
    BulletEnhancementStatus,
    EvidenceLevel,
    ExperienceEntry,
    ExperienceType,
    MetricStatus,
    ResumeContent,
    ResumeType,
    SkillGroup,
    UserProfile,
    EducationEntry,
)
from resume_pdf_agent.sample_data import SAMPLE_CRITERIA_PROFILE, SAMPLE_RESUME_CONTENT, SAMPLE_USER_PROFILE
from resume_pdf_agent.gap_analysis import analyze_criteria_gap


def test_enhance_resume_bullets_can_be_imported():
    assert callable(enhance_resume_bullets)


def test_valid_resume_content_generates_candidates_with_source_and_criteria():
    gap = analyze_criteria_gap(SAMPLE_USER_PROFILE, SAMPLE_CRITERIA_PROFILE, SAMPLE_RESUME_CONTENT)

    result = enhance_resume_bullets(SAMPLE_RESUME_CONTENT, SAMPLE_CRITERIA_PROFILE, gap)

    assert result.candidates_generated >= 1
    candidate = result.experience_results[0].candidates[0]
    assert candidate.source_experience_id == SAMPLE_RESUME_CONTENT.experiences[0].experience_id
    assert candidate.targeted_criteria_ids
    assert candidate.enhanced_text


def test_max_candidates_per_experience_is_respected():
    result = enhance_resume_bullets(SAMPLE_RESUME_CONTENT, SAMPLE_CRITERIA_PROFILE, max_candidates_per_experience=1)

    assert all(len(item.candidates) <= 1 for item in result.experience_results)


def test_counts_are_correct():
    result = enhance_resume_bullets(SAMPLE_RESUME_CONTENT, SAMPLE_CRITERIA_PROFILE)
    candidates = [candidate for item in result.experience_results for candidate in item.candidates]

    assert result.candidates_generated == len(candidates)
    assert result.candidates_requiring_confirmation == sum(c.needs_confirmation for c in candidates)
    assert result.safe_candidates_count == sum(
        1 for c in candidates if c.status == BulletEnhancementStatus.ENHANCED and not c.needs_confirmation
    )


def test_weak_source_evidence_requires_confirmation():
    content = ResumeContent(
        resume_type=ResumeType.DATA_SCIENCE_RESUME,
        experiences=[
            ExperienceEntry(
                experience_id="exp_weak",
                experience_type=ExperienceType.PROJECT,
                title="Data Project",
                tools_used=["Python"],
            )
        ],
    )

    result = enhance_resume_bullets(content)
    candidate = result.experience_results[0].candidates[0]

    assert candidate.needs_confirmation is True
    assert candidate.evidence_level == EvidenceLevel.NEEDS_USER_CONFIRMATION


def test_insufficient_evidence_produces_skipped_reason_or_status():
    content = ResumeContent(
        resume_type=ResumeType.GENERAL_STUDENT_RESUME,
        experiences=[ExperienceEntry(experience_id="exp_empty", experience_type=ExperienceType.OTHER, title="Activity")],
    )

    result = enhance_resume_bullets(content)
    item = result.experience_results[0]

    assert item.skipped_reasons
    assert item.candidates[0].status == BulletEnhancementStatus.INSUFFICIENT_EVIDENCE


def test_engine_does_not_mutate_resume_content():
    content = deepcopy(SAMPLE_RESUME_CONTENT)
    before = deepcopy(content)

    enhance_resume_bullets(content, SAMPLE_CRITERIA_PROFILE)

    assert content == before
