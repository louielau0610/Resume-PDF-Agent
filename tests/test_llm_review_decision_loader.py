"""Tests for M23 LLM review decision loader."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from resume_pdf_agent.llm_review_decisions.loader import load_llm_review_decision_file


def _write_json(path: Path, data: object) -> Path:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def test_missing_file_raises_clear_error(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        load_llm_review_decision_file(tmp_path / "missing.json")


def test_invalid_json_raises_value_error(tmp_path: Path):
    path = tmp_path / "bad.json"
    path.write_text("{not json", encoding="utf-8")
    with pytest.raises(ValueError, match="Invalid JSON"):
        load_llm_review_decision_file(path)


def test_empty_decisions_file_loads(tmp_path: Path):
    path = _write_json(tmp_path / "decisions.json", {"decisions": []})
    decision_file = load_llm_review_decision_file(path)
    assert decision_file.decisions == []


def test_valid_browser_export_shape_loads(tmp_path: Path):
    path = _write_json(
        tmp_path / "decisions.json",
        {
            "reviewer_name": "local",
            "reviewed_at": "2026-06-08T00:00:00Z",
            "decisions": [
                {
                    "candidate_id": "c1",
                    "decision": "approve_candidate",
                    "reviewer_note": "ok",
                    "replacement_text": None,
                }
            ],
        },
    )
    decision_file = load_llm_review_decision_file(path)
    assert decision_file.decisions[0].candidate_id == "c1"
    assert decision_file.decisions[0].action == "approve_candidate"
    assert decision_file.decisions[0].note == "ok"


def test_duplicate_candidate_ids_load_for_analyzer_warning(tmp_path: Path):
    path = _write_json(
        tmp_path / "decisions.json",
        {
            "decisions": [
                {"candidate_id": "c1", "decision": "approve_candidate"},
                {"candidate_id": "c1", "decision": "reject_candidate"},
            ]
        },
    )
    decision_file = load_llm_review_decision_file(path)
    assert [d.candidate_id for d in decision_file.decisions] == ["c1", "c1"]


def test_unknown_action_loads_in_non_strict_mode(tmp_path: Path):
    path = _write_json(
        tmp_path / "decisions.json",
        {"decisions": [{"candidate_id": "c1", "decision": "custom"}]},
    )
    decision_file = load_llm_review_decision_file(path)
    assert decision_file.decisions[0].normalized_action is None


def test_unknown_action_fails_in_strict_mode(tmp_path: Path):
    path = _write_json(
        tmp_path / "decisions.json",
        {"decisions": [{"candidate_id": "c1", "decision": "custom"}]},
    )
    with pytest.raises(ValueError, match="Unknown"):
        load_llm_review_decision_file(path, strict=True)
