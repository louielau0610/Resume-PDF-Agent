"""Analyze M23 LLM review decisions without applying candidates."""

from __future__ import annotations

from collections import Counter

from resume_pdf_agent.models.llm import LLMRewriteResult
from resume_pdf_agent.models.llm_review_decisions import (
    LLMReviewCandidateDecisionSummary,
    LLMReviewDecisionAction,
    LLMReviewDecisionFile,
    LLMReviewDecisionSummary,
)

_SAFETY_NOTICE = (
    "LLM review decisions are advisory only. This summary does not apply "
    "candidates, does not insert approved text into the resume, does not "
    "verify factual truth, and does not bypass M5 truthfulness checks or "
    "the M14 confirmation gate."
)


def _append_unique(values: list[str], value: str) -> None:
    if value not in values:
        values.append(value)


def analyze_llm_review_decisions(
    decision_file: LLMReviewDecisionFile,
    rewrite_result: LLMRewriteResult | None = None,
    *,
    result_path: str | None = None,
    decisions_path: str | None = None,
) -> LLMReviewDecisionSummary:
    """Compare LLM review decisions with optional M16 rewrite candidates."""

    candidate_ids = [c.candidate_id for c in rewrite_result.candidates] if rewrite_result else []
    known_ids = set(candidate_ids)
    decision_ids = [d.candidate_id for d in decision_file.decisions]
    duplicate_ids = sorted([cid for cid, count in Counter(decision_ids).items() if count > 1])

    approved: list[str] = []
    rejected: list[str] = []
    needs_edit: list[str] = []
    note_ids: list[str] = []
    ignored: list[str] = []
    unknown: list[str] = []
    invalid: list[str] = []
    warnings: list[str] = []
    summaries: list[LLMReviewCandidateDecisionSummary] = []

    for d in decision_file.decisions:
        action = d.normalized_action
        known = True if rewrite_result is None else d.candidate_id in known_ids
        duplicate = d.candidate_id in duplicate_ids

        if rewrite_result is not None and not known:
            _append_unique(unknown, d.candidate_id)
        if action is None:
            invalid.append(f"{d.candidate_id}: unknown action '{d.action}'")
        elif action == LLMReviewDecisionAction.APPROVE_CANDIDATE:
            _append_unique(approved, d.candidate_id)
        elif action == LLMReviewDecisionAction.REJECT_CANDIDATE:
            _append_unique(rejected, d.candidate_id)
        elif action == LLMReviewDecisionAction.NEEDS_EDITING:
            _append_unique(needs_edit, d.candidate_id)
        elif action == LLMReviewDecisionAction.PROVIDE_NOTE:
            _append_unique(note_ids, d.candidate_id)
        elif action == LLMReviewDecisionAction.IGNORE_FOR_NOW:
            _append_unique(ignored, d.candidate_id)

        if d.has_note:
            _append_unique(note_ids, d.candidate_id)

        summaries.append(
            LLMReviewCandidateDecisionSummary(
                candidate_id=d.candidate_id,
                action=d.action,
                normalized_action=action.value if action else None,
                known_candidate=known,
                duplicate=duplicate,
                has_note=d.has_note,
                note=d.note,
                replacement_text=d.replacement_text,
            )
        )

    undecided = sorted([cid for cid in candidate_ids if cid not in set(decision_ids)])

    if rewrite_result is None:
        warnings.append(
            "No llm_rewrite_result.json was provided; candidate ID cross-checking was skipped."
        )
    if not decision_file.decisions:
        warnings.append("No review decisions were found in the decisions file.")
    if duplicate_ids:
        warnings.append(
            "Duplicate decision entries found for candidate IDs: " + ", ".join(duplicate_ids)
        )
    if unknown:
        warnings.append(
            "Decisions reference unknown candidate IDs: " + ", ".join(sorted(unknown))
        )
    if undecided:
        warnings.append(
            "Some LLM rewrite candidates do not have decisions: " + ", ".join(undecided)
        )
    if invalid:
        warnings.append("Some decisions use unknown actions and were not counted.")

    warnings.append(
        "Approved LLM candidates remain advisory and are not automatically applied to resume.html or resume.pdf."
    )

    summary_text = (
        f"LLM review decision summary: {len(candidate_ids)} candidates, "
        f"{len(decision_file.decisions)} decisions, {len(approved)} approved, "
        f"{len(rejected)} rejected, {len(needs_edit)} needs editing, "
        f"{len(note_ids)} with notes, {len(ignored)} ignored."
    )

    return LLMReviewDecisionSummary(
        total_candidates=len(candidate_ids),
        total_decisions=len(decision_file.decisions),
        approved_count=len(approved),
        rejected_count=len(rejected),
        needs_edit_count=len(needs_edit),
        note_count=len(note_ids),
        ignored_count=len(ignored),
        approved_candidate_ids=sorted(approved),
        rejected_candidate_ids=sorted(rejected),
        needs_edit_candidate_ids=sorted(needs_edit),
        note_candidate_ids=sorted(note_ids),
        ignored_candidate_ids=sorted(ignored),
        undecided_candidate_ids=undecided,
        unknown_candidate_ids=sorted(unknown),
        duplicate_candidate_ids=duplicate_ids,
        invalid_decisions=invalid,
        candidate_summaries=summaries,
        warnings=warnings,
        safety_notice=_SAFETY_NOTICE,
        result_path=result_path,
        decisions_path=decisions_path,
        summary=summary_text,
    )
