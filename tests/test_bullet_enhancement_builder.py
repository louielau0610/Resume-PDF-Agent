from resume_pdf_agent.enhancement import build_enhanced_bullet_text
from resume_pdf_agent.enhancement.bullet_builder import (
    build_metric_phrase,
    select_action_verb,
)
from resume_pdf_agent.models import ExperienceEntry, ExperienceType, Metric


def test_build_enhanced_bullet_text_can_be_imported():
    assert callable(build_enhanced_bullet_text)


def test_valid_project_evidence_builds_conservative_bullet():
    experience = ExperienceEntry(
        experience_id="exp_1",
        experience_type=ExperienceType.PROJECT,
        title="Data Cleaning Project",
        raw_description="Prepared structured datasets for model evaluation",
        tools_used=["Python", "pandas"],
        methods_used=["Data cleaning"],
        outcomes=["support downstream model evaluation"],
    )

    bullet = build_enhanced_bullet_text(experience)

    assert bullet is not None
    assert "Python" in bullet
    assert "pandas" in bullet
    assert bullet.endswith(".")
    assert len(bullet.split()) <= 35


def test_builder_does_not_fabricate_metrics():
    experience = ExperienceEntry(
        experience_id="exp_1",
        experience_type=ExperienceType.PROJECT,
        title="Analysis Project",
        tools_used=["Python"],
    )

    bullet = build_enhanced_bullet_text(experience)

    assert bullet is not None
    assert "30%" not in bullet
    assert "user-provided metric" not in bullet


def test_user_provided_metric_may_be_included_when_source_supported():
    experience = ExperienceEntry(
        experience_id="exp_1",
        experience_type=ExperienceType.PROJECT,
        title="Model Evaluation",
        tools_used=["Python"],
        metrics=[Metric(name="accuracy", value="0.82", context="validation set", source_note="user provided")],
    )

    assert build_metric_phrase(experience) is not None
    assert "accuracy" in build_enhanced_bullet_text(experience)


def test_leadership_action_not_generated_from_generic_project():
    experience = ExperienceEntry(
        experience_id="exp_1",
        experience_type=ExperienceType.PROJECT,
        title="Team Project",
        raw_description="Assisted with data analysis",
    )

    bullet = build_enhanced_bullet_text(experience)

    assert bullet is not None
    assert "Led" not in bullet
    assert select_action_verb(experience.experience_type, [], []) != "Led"


def test_builder_avoids_strong_impact_verbs_without_outcome_or_metric():
    experience = ExperienceEntry(
        experience_id="exp_1",
        experience_type=ExperienceType.PROJECT,
        title="Optimization Project",
        raw_description="Optimized draft workflow",
        tools_used=["Python"],
    )

    bullet = build_enhanced_bullet_text(experience)

    assert bullet is not None
    assert "Optimized" not in bullet
