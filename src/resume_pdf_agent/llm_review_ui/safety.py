"""Safety helpers for M22 browser LLM rewrite review UI."""

from __future__ import annotations

import html as _html
from pathlib import Path

from resume_pdf_agent.models.llm import LLMRewriteResult


def escape_llm_review_ui_text(value: str) -> str:
    return _html.escape(value, quote=True)


def safe_llm_review_output_path(path: str | Path) -> Path:
    return Path(path).resolve()


def validate_llm_rewrite_result_for_ui(result: LLMRewriteResult) -> list[str]:
    issues: list[str] = []
    if not result.candidates:
        issues.append("No candidates in rewrite result; review page will show empty list.")
    for i, c in enumerate(result.candidates):
        if not c.original_text.strip():
            issues.append(f"Candidate {i} has empty original_text.")
        if not c.rewritten_text.strip():
            issues.append(f"Candidate {i} has empty rewritten_text.")
        if not c.candidate_id.strip():
            issues.append(f"Candidate {i} has empty candidate_id.")
    return issues


def get_llm_review_decision_options() -> list[dict]:
    return [
        {
            "value": "approve_candidate",
            "label": "Approve Candidate / 批准候选",
            "description": "Accept this rewrite as a local preference. Does NOT verify truth.",
        },
        {
            "value": "reject_candidate",
            "label": "Reject Candidate / 拒绝候选",
            "description": "Reject this rewrite. Original text will be kept.",
        },
        {
            "value": "needs_editing",
            "label": "Needs Editing / 需要编辑",
            "description": "The rewrite needs manual editing before approval.",
        },
        {
            "value": "provide_note",
            "label": "Provide Note / 添加备注",
            "description": "Add a note without making a decision yet.",
        },
        {
            "value": "ignore_for_now",
            "label": "Ignore for Now / 暂时忽略",
            "description": "Skip this candidate for now without a final decision.",
        },
    ]
