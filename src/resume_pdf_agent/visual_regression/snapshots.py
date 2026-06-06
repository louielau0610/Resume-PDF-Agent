"""Snapshot normalization helpers for M18 visual regression."""

from __future__ import annotations

import json
import re
from pathlib import Path


def normalize_html_for_snapshot(html: str) -> str:
    """Normalize HTML for stable snapshot comparison.

    - Collapses whitespace
    - Removes dynamic timestamps
    - Normalizes paths
    """
    # Collapse whitespace
    html = re.sub(r"[ \t]+", " ", html)
    html = re.sub(r"\n{3,}", "\n\n", html)

    # Remove timestamps (ISO format)
    html = re.sub(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?", "[TIMESTAMP]", html)

    return html.strip()


def extract_stable_snapshot_sections(html: str) -> dict[str, str]:
    """Extract stable semantic sections from dashboard/resume HTML.

    Returns a dict of section_name -> content for snapshot comparison.
    """
    sections: dict[str, str] = {}

    # Extract CSS classes used
    classes = set(re.findall(r'class=["\']([^"\']+)["\']', html))
    sections["css_classes"] = ", ".join(sorted(classes))

    # Extract stage names from dashboard
    stage_names = re.findall(r'<div class="stage-name">([^<]+)</div>', html)
    if stage_names:
        sections["stage_names"] = ", ".join(stage_names)

    # Extract artifact labels
    artifact_labels = re.findall(r'<span class="artifact-label">\s*<div>([^<]+)</div>', html)
    if artifact_labels:
        sections["artifact_labels"] = ", ".join(artifact_labels)

    # Extract section headings
    headings = re.findall(r'<h2 class="[^"]*">([^<]+)</h2>', html)
    if headings:
        sections["section_headings"] = ", ".join(headings)

    return sections


def write_snapshot(snapshot_data: dict | str, output_path: str | Path) -> None:
    """Write snapshot data to a file."""
    p = Path(output_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(snapshot_data, dict):
        p.write_text(json.dumps(snapshot_data, indent=2, ensure_ascii=False), encoding="utf-8")
    else:
        p.write_text(str(snapshot_data), encoding="utf-8")


def compare_snapshot_text(
    current: str,
    expected: str,
    max_allowed_line_changes: int = 0,
) -> tuple[bool, list[str]]:
    """Compare two snapshot texts line by line.

    Parameters
    ----------
    current : str
        Current text to check.
    expected : str
        Expected baseline text.
    max_allowed_line_changes : int
        Maximum number of differing lines allowed.

    Returns
    -------
    tuple[bool, list[str]]
        (is_match, list of differences)
    """
    current_lines = current.strip().split("\n")
    expected_lines = expected.strip().split("\n")
    diffs: list[str] = []

    max_len = max(len(current_lines), len(expected_lines))
    for i in range(max_len):
        cl = current_lines[i].strip() if i < len(current_lines) else "(missing)"
        el = expected_lines[i].strip() if i < len(expected_lines) else "(missing)"
        if cl != el:
            diffs.append(f"Line {i + 1}: expected '{el[:80]}' got '{cl[:80]}'")

    is_match = len(diffs) <= max_allowed_line_changes
    return is_match, diffs
