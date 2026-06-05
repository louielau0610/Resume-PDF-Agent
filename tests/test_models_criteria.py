import pytest
from pydantic import ValidationError as PydanticValidationError

from resume_pdf_agent.models import (
    CriteriaCategory,
    ExportFormat,
    MatchLevel,
    RiskLevel,
    RoleCriteriaProfile,
    ScreeningCriterion,
    SourceMetadata,
    SourceType,
)
from resume_pdf_agent.models.analysis import CriteriaMatchResult, GapAnalysisResult


def _valid_source() -> SourceMetadata:
    return SourceMetadata(source_type=SourceType.MANUALLY_CURATED)


def _valid_criterion(**overrides) -> ScreeningCriterion:
    data = {
        "criterion_id": "criterion_1",
        "category": CriteriaCategory.SKILL_COVERAGE,
        "name": "Python skill coverage",
        "description": "Evidence of Python use in data analysis.",
        "importance": 4,
        "source": _valid_source(),
        "confidence": 0.8,
    }
    data.update(overrides)
    return ScreeningCriterion(**data)


def test_criteria_models_can_be_imported():
    profile = RoleCriteriaProfile(
        profile_id="criteria_profile_1",
        role_title="Data Science Intern",
        criteria=[_valid_criterion()],
    )

    assert profile.profile_id == "criteria_profile_1"
    assert profile.criteria[0].importance == 4


def test_analysis_models_can_be_imported():
    result = GapAnalysisResult(
        profile_id="criteria_profile_1",
        overall_match_level=MatchLevel.MEDIUM,
        criteria_results=[
            CriteriaMatchResult(
                criterion_id="criterion_1",
                match_level=MatchLevel.WEAK,
                risk_level=RiskLevel.MEDIUM,
            )
        ],
    )

    assert result.criteria_results[0].criterion_id == "criterion_1"


def test_screening_criterion_rejects_empty_required_fields():
    with pytest.raises(PydanticValidationError):
        _valid_criterion(criterion_id="")

    with pytest.raises(PydanticValidationError):
        _valid_criterion(name="")

    with pytest.raises(PydanticValidationError):
        _valid_criterion(description="")


def test_role_criteria_profile_rejects_empty_required_fields():
    with pytest.raises(PydanticValidationError):
        RoleCriteriaProfile(profile_id="", role_title="Data Science Intern")

    with pytest.raises(PydanticValidationError):
        RoleCriteriaProfile(profile_id="criteria_profile_1", role_title="")


def test_screening_criterion_rejects_importance_below_1():
    with pytest.raises(PydanticValidationError):
        _valid_criterion(importance=0)


def test_screening_criterion_rejects_importance_above_5():
    with pytest.raises(PydanticValidationError):
        _valid_criterion(importance=6)


def test_screening_criterion_rejects_confidence_below_0():
    with pytest.raises(PydanticValidationError):
        _valid_criterion(confidence=-0.1)


def test_screening_criterion_rejects_confidence_above_1():
    with pytest.raises(PydanticValidationError):
        _valid_criterion(confidence=1.1)


def test_export_format_only_includes_pdf():
    assert [item.value for item in ExportFormat] == ["pdf"]
