"""M27 Manual Patch Preview — preview-only, no resume mutation."""

from resume_pdf_agent.llm_manual_patch_preview.builder import (
    build_manual_patch_preview,
)
from resume_pdf_agent.llm_manual_patch_preview.diffing import (
    compute_diff_preview_lines,
    compute_unified_diff_preview,
)
from resume_pdf_agent.llm_manual_patch_preview.io import (
    write_manual_patch_preview_to_files,
)
from resume_pdf_agent.llm_manual_patch_preview.markdown import (
    render_manual_patch_preview_markdown,
)
from resume_pdf_agent.llm_manual_patch_preview.renderer import (
    render_manual_patch_preview_html,
)

__all__ = [
    "build_manual_patch_preview",
    "compute_diff_preview_lines",
    "compute_unified_diff_preview",
    "render_manual_patch_preview_html",
    "render_manual_patch_preview_markdown",
    "write_manual_patch_preview_to_files",
]
