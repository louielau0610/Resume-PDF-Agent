"""Load M23 LLM review decision inputs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from resume_pdf_agent.models.llm import LLMRewriteResult
from resume_pdf_agent.models.llm_review_decisions import (
    LLMReviewDecisionFile,
)


def _read_json_object(path: str | Path) -> Any:
    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError(f"File not found: {p}")
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in {p}: {exc}") from exc


def load_llm_review_decision_file(
    path: str | Path,
    *,
    strict: bool = False,
) -> LLMReviewDecisionFile:
    """Load and normalize an llm_rewrite_review_decisions.json file."""

    raw = _read_json_object(path)
    try:
        decision_file = LLMReviewDecisionFile(**raw)
    except ValidationError as exc:
        raise ValueError(f"Invalid LLM review decisions file: {exc}") from exc

    if strict:
        unknown = [
            f"{d.candidate_id}: {d.action}"
            for d in decision_file.decisions
            if d.normalized_action is None
        ]
        if unknown:
            raise ValueError(
                "Unknown LLM review decision action(s): " + ", ".join(unknown)
            )

    return decision_file


def load_llm_rewrite_result_file(path: str | Path) -> LLMRewriteResult:
    """Load an M16 llm_rewrite_result.json file."""

    raw = _read_json_object(path)
    try:
        return LLMRewriteResult(**raw)
    except ValidationError as exc:
        raise ValueError(f"Invalid LLM rewrite result file: {exc}") from exc
