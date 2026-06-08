"""Deterministic text diff preview helpers for M27. Display-only — no executable patches."""

from __future__ import annotations

import difflib

_SAFETY = "DISPLAY-ONLY: This diff is for human review only. It is NOT an executable patch and must NOT be applied automatically."


def compute_unified_diff_preview(
    original: str,
    proposed: str,
    label_a: str = "Original",
    label_b: str = "Proposed",
) -> str:
    """Return a display-only unified diff string. Not a .patch file."""
    if original == proposed:
        return f"{_SAFETY}\n(No differences — texts are identical.)"

    diff = difflib.unified_diff(
        original.splitlines(keepends=True),
        proposed.splitlines(keepends=True),
        fromfile=label_a,
        tofile=label_b,
        lineterm="",
    )
    lines = list(diff)
    if not lines:
        return f"{_SAFETY}\n(No differences detected.)"
    return _SAFETY + "\n" + "\n".join(lines)


def compute_diff_preview_lines(
    original: str,
    proposed: str,
) -> list[str]:
    """Return a list of display-only diff lines for embedding in reports."""
    result = compute_unified_diff_preview(original, proposed)
    return result.splitlines()
