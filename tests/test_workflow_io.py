"""Tests for workflow I/O helpers."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from resume_pdf_agent.models import PDFBackend
from resume_pdf_agent.models.workflow import ResumeWorkflowInput
from resume_pdf_agent.workflow.io import (
    ensure_output_dir,
    load_workflow_input_from_json,
    write_text_artifact,
)


def test_load_workflow_input_from_json_can_be_imported():
    """load_workflow_input_from_json is importable."""
    assert callable(load_workflow_input_from_json)


def test_load_workflow_input_from_sample_json():
    """Sample data_science_user.json loads into ResumeWorkflowInput."""
    sample_path = (
        Path(__file__).resolve().parent.parent
        / "data"
        / "sample_inputs"
        / "sample_data_science_user.json"
    )
    result = load_workflow_input_from_json(sample_path)
    assert isinstance(result, ResumeWorkflowInput)
    assert result.user_profile.full_name == "Alex Chen"
    assert len(result.resume_content.experiences) == 2
    assert result.pdf_backend == PDFBackend.MOCK


def test_load_workflow_input_missing_user_profile(tmp_path: Path):
    """Loading JSON without user_profile raises ValueError."""
    bad_path = tmp_path / "bad.json"
    bad_path.write_text(json.dumps({"resume_content": {}}))
    with pytest.raises(ValueError, match="user_profile"):
        load_workflow_input_from_json(bad_path)


def test_load_workflow_input_missing_resume_content(tmp_path: Path):
    """Loading JSON without resume_content raises ValueError."""
    bad_path = tmp_path / "bad.json"
    bad_path.write_text(json.dumps({"user_profile": {}}))
    with pytest.raises(ValueError, match="resume_content"):
        load_workflow_input_from_json(bad_path)


def test_load_workflow_input_file_not_found():
    """Loading a non-existent file raises FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        load_workflow_input_from_json("nonexistent_file.json")


def test_ensure_output_dir_creates(tmp_path: Path):
    """ensure_output_dir creates the directory and returns Path."""
    d = tmp_path / "nested" / "output"
    result = ensure_output_dir(d)
    assert result.is_dir()
    assert result == d


def test_ensure_output_dir_existing(tmp_path: Path):
    """ensure_output_dir works on existing directories."""
    d = tmp_path / "existing"
    d.mkdir()
    result = ensure_output_dir(d)
    assert result.is_dir()
    assert result == d


def test_write_text_artifact(tmp_path: Path):
    """write_text_artifact writes a file and returns a WorkflowArtifact."""
    art = write_text_artifact(
        "hello world",
        tmp_path / "test.txt",
        artifact_type="text",
        description="Text file artifact",
    )
    assert art.artifact_type == "text"
    assert art.path == str(tmp_path / "test.txt")
    assert art.description == "Text file artifact"
    assert (tmp_path / "test.txt").read_text(encoding="utf-8") == "hello world"


def test_write_text_artifact_creates_parents(tmp_path: Path):
    """write_text_artifact creates parent directories."""
    art = write_text_artifact(
        "content",
        tmp_path / "deep" / "nested" / "file.txt",
        artifact_type="log",
        description="Deep file",
    )
    assert (tmp_path / "deep" / "nested" / "file.txt").is_file()
