"""Serialization helpers for workflow artifacts."""

from __future__ import annotations

import json
from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from resume_pdf_agent.models.workflow import WorkflowArtifact


def _serialize_value(value: Any) -> Any:
    """Recursively convert values to JSON-serializable primitives."""

    if isinstance(value, Enum):
        return value.value
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, BaseModel):
        return model_to_plain_dict(value)
    if isinstance(value, dict):
        return {str(k): _serialize_value(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_serialize_value(v) for v in value]
    return value


def model_to_plain_dict(model: Any) -> dict:
    """Convert a Pydantic model (or nested models) to a plain dict suitable for JSON.

    Falls back to ``model.dict()`` if Pydantic v1 is detected, otherwise uses
    ``model_dump(mode='python')`` (Pydantic v2).
    """

    if hasattr(model, "model_dump"):
        raw = model.model_dump(mode="python")
    elif hasattr(model, "dict"):
        raw = model.dict()
    else:
        raise TypeError(f"Object {type(model).__name__} is not a Pydantic model")

    return _serialize_value(raw)


def write_json_artifact(data: Any, output_path: str | Path) -> WorkflowArtifact:
    """Serialize *data* to a UTF-8 JSON file and return a WorkflowArtifact.

    *data* can be a Pydantic model, a dict, or a list that is recursively
    converted to plain Python types before serialization.
    """

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    plain = _serialize_value(data)
    output_path.write_text(
        json.dumps(plain, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    return WorkflowArtifact(
        artifact_type="json",
        path=str(output_path),
        description=f"JSON artifact written to {output_path.name}",
    )
