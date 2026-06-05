"""Decision application for M14 user confirmation workflow.

Loads user decisions and applies them to a confirmation packet,
producing a ConfirmationReviewResult.
"""

from __future__ import annotations

import json
from pathlib import Path

from resume_pdf_agent.models.confirmation import (
    ConfirmationDecision,
    ConfirmationDecisionSet,
    ConfirmationDecisionType,
    ConfirmationItem,
    ConfirmationItemStatus,
    ConfirmationPacket,
    ConfirmationPriority,
    ConfirmationReviewResult,
)


def load_confirmation_decisions(path: str | Path) -> ConfirmationDecisionSet:
    """Load a ConfirmationDecisionSet from a JSON file.

    Parameters
    ----------
    path : str | Path
        Path to a JSON file containing a ConfirmationDecisionSet.

    Returns
    -------
    ConfirmationDecisionSet
        Parsed decision set.
    """
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    return ConfirmationDecisionSet(**raw)


def apply_confirmation_decisions(
    packet: ConfirmationPacket,
    decision_set: ConfirmationDecisionSet,
) -> ConfirmationReviewResult:
    """Apply user decisions to a confirmation packet.

    Creates copies of items before modification — does NOT mutate the
    original packet.

    Parameters
    ----------
    packet : ConfirmationPacket
        The confirmation packet to review.
    decision_set : ConfirmationDecisionSet
        User decisions to apply.

    Returns
    -------
    ConfirmationReviewResult
        Result summarizing the applied decisions.
    """
    import copy

    # Build a lookup of decisions by item_id
    decision_map: dict[str, ConfirmationDecision] = {}
    for d in decision_set.decisions:
        decision_map[d.item_id] = d

    resolved: list[ConfirmationItem] = []
    rejected: list[ConfirmationItem] = []
    needs_editing: list[ConfirmationItem] = []
    unresolved: list[ConfirmationItem] = []
    review_warnings: list[str] = []

    for item in packet.items:
        # Work on a copy to avoid mutating the original packet
        item = copy.deepcopy(item)
        decision = decision_map.get(item.item_id)

        if decision is None:
            # No decision provided — stays pending/unresolved
            unresolved.append(item)
            continue

        if decision.decision == ConfirmationDecisionType.APPROVE:
            item.status = ConfirmationItemStatus.RESOLVED
            resolved.append(item)

        elif decision.decision == ConfirmationDecisionType.REJECT:
            item.status = ConfirmationItemStatus.REJECTED
            rejected.append(item)

        elif decision.decision == ConfirmationDecisionType.NEEDS_EDITING:
            item.status = ConfirmationItemStatus.NEEDS_EDITING
            needs_editing.append(item)

        elif decision.decision == ConfirmationDecisionType.PROVIDE_EVIDENCE:
            if decision.provided_evidence:
                item.status = ConfirmationItemStatus.RESOLVED
                resolved.append(item)
            else:
                # Should not happen due to model validator, but be safe
                item.status = ConfirmationItemStatus.PENDING
                unresolved.append(item)
                review_warnings.append(
                    f"Item {item.item_id}: provide_evidence decision missing evidence"
                )

        elif decision.decision == ConfirmationDecisionType.IGNORE_FOR_NOW:
            if item.blocks_final_pdf:
                # Blocking items cannot be resolved by ignoring
                item.status = ConfirmationItemStatus.BLOCKED
                unresolved.append(item)
                review_warnings.append(
                    f"Item {item.item_id}: cannot ignore blocking item"
                )
            else:
                item.status = ConfirmationItemStatus.IGNORED
                # Ignored items are not unresolved
                resolved.append(item)

    # Check for decisions on unknown item IDs
    known_ids = {i.item_id for i in packet.items}
    for did in decision_map:
        if did not in known_ids:
            review_warnings.append(
                f"Decision references unknown item_id: {did}"
            )

    # Determine if we can generate final PDF
    blocking_unresolved = sum(
        1 for i in unresolved if i.blocks_final_pdf
    )
    can_generate = blocking_unresolved == 0

    # Build summary
    summary_parts = [
        f"已应用 {len(decision_set.decisions)} 条决策。",
        f"已解决: {len(resolved)} 项，已拒绝: {len(rejected)} 项，",
        f"需编辑: {len(needs_editing)} 项，未处理: {len(unresolved)} 项。",
    ]
    if can_generate:
        summary_parts.append("可以生成最终 PDF。")
    else:
        summary_parts.append(
            f"仍有 {blocking_unresolved} 个阻塞项未解决，无法生成最终 PDF。"
        )

    return ConfirmationReviewResult(
        packet_id=packet.packet_id,
        decisions_applied=len(decision_set.decisions),
        unresolved_items=unresolved,
        resolved_items=resolved,
        rejected_items=rejected,
        needs_editing_items=needs_editing,
        can_generate_final_pdf=can_generate,
        warnings=review_warnings,
        summary="".join(summary_parts),
    )
