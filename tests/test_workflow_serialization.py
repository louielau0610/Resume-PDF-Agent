"""Tests for workflow serialization helpers."""

from __future__ import annotations

import json
from enum import Enum
from pathlib import Path

import pytest

from resume_pdf_agent.models import (
    EvidenceLevel,
    ExperienceEntry,
    ExperienceType,
    Metric,
    MetricStatus,
    ResumeBullet,
    ResumeContent,
    ResumeSection,
    ResumeType,
    UserProfile,
)
from resume_pdf_agent.models.workflow import (
    ResumeWorkflowInput,
    ResumeWorkflowResult,
    WorkflowArtifact,
    WorkflowRunStatus,
    WorkflowStageName,
    WorkflowStageResult,
    WorkflowStageStatus,
)
from resume_pdf_agent.workflow.serialization import (
    model_to_plain_dict,
    write_json_artifact,
)


class _Color(Enum):
    RED = "red"
    BLUE = "blue"


def test_model_to_plain_dict_handles_enums():
    """Enums are serialized to their values."""
    result = ResumeWorkflowResult(
        status=WorkflowRunStatus.COMPLETED,
        output_dir="/tmp/test",
        primary_resume_type=ResumeType.DATA_SCIENCE_RESUME,
        summary="Test summary",
    )
    d = model_to_plain_dict(result)
    assert d["status"] == "completed"
    assert d["primary_resume_type"] == "data_science_resume"


def test_model_to_plain_dict_handles_nested_models():
    """Nested Pydantic models are recursively serialized."""
    stage = WorkflowStageResult(
        stage=WorkflowStageName.GAP_ANALYSIS,
        status=WorkflowStageStatus.COMPLETED,
        message="Done",
    )
    d = model_to_plain_dict(stage)
    assert d["stage"] == "gap_analysis"
    assert d["status"] == "completed"
    assert d["message"] == "Done"


def test_model_to_plain_dict_handles_lists():
    """Lists of models/enums are serialized."""
    result = ResumeWorkflowResult(
        status=WorkflowRunStatus.COMPLETED_WITH_WARNINGS,
        output_dir="/tmp",
        stages=[
            WorkflowStageResult(
                stage=WorkflowStageName.USER_INTAKE,
                status=WorkflowStageStatus.COMPLETED,
                message="OK",
                warnings=["w1", "w2"],
            )
        ],
        warnings=["global_warning"],
        summary="Test.",
    )
    d = model_to_plain_dict(result)
    assert d["status"] == "completed_with_warnings"
    assert d["stages"][0]["stage"] == "user_intake"
    assert d["stages"][0]["warnings"] == ["w1", "w2"]
    assert d["warnings"] == ["global_warning"]


def test_write_json_artifact_writes_file(tmp_path: Path):
    """write_json_artifact writes a valid JSON file."""
    data = {"key": "value", "nested": {"a": 1}}
    output_path = tmp_path / "test.json"
    art = write_json_artifact(data, output_path)

    assert art.artifact_type == "json"
    assert art.path == str(output_path)
    assert output_path.is_file()

    loaded = json.loads(output_path.read_text(encoding="utf-8"))
    assert loaded == data


def test_write_json_artifact_creates_parent_dirs(tmp_path: Path):
    """write_json_artifact creates parent directories."""
    output_path = tmp_path / "deep" / "nested" / "artifact.json"
    art = write_json_artifact([1, 2, 3], output_path)
    assert output_path.is_file()
    loaded = json.loads(output_path.read_text(encoding="utf-8"))
    assert loaded == [1, 2, 3]


def test_write_json_artifact_with_pydantic_model(tmp_path: Path):
    """write_json_artifact handles Pydantic models."""
    artifact = WorkflowArtifact(
        artifact_type="json",
        path="/some/path.json",
        description="Test artifact",
    )
    output_path = tmp_path / "artifact.json"
    art = write_json_artifact(artifact, output_path)
    assert art.path == str(output_path)
    loaded = json.loads(output_path.read_text(encoding="utf-8"))
    assert loaded["artifact_type"] == "json"
    assert loaded["path"] == "/some/path.json"


def test_write_json_artifact_is_utf8(tmp_path: Path):
    """write_json_artifact writes UTF-8 encoded JSON."""
    data = {"name": "Ålex Chén"}
    output_path = tmp_path / "utf8.json"
    write_json_artifact(data, output_path)
    loaded = json.loads(output_path.read_text(encoding="utf-8"))
    assert loaded["name"] == "Ålex Chén"


def test_write_json_artifact_uses_indent_2(tmp_path: Path):
    """write_json_artifact uses indent=2 formatting."""
    data = {"a": 1, "b": 2}
    output_path = tmp_path / "indent.json"
    write_json_artifact(data, output_path)
    text = output_path.read_text(encoding="utf-8")
    assert '  "a"' in text
    assert '  "b"' in text  # both keys should be indented


def test_serialization_artifact_path_not_empty():
    """WorkflowArtifact requires non-empty path."""
    with pytest.raises(ValueError):
        WorkflowArtifact(artifact_type="json", path="", description="Bad")


def test_serialization_stage_message_not_empty():
    """WorkflowStageResult requires non-empty message."""
    with pytest.raises(ValueError):
        WorkflowStageResult(
            stage=WorkflowStageName.USER_INTAKE,
            status=WorkflowStageStatus.COMPLETED,
            message="",
        )
