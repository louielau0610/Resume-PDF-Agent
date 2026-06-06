"""Demo workflow runner script for M13.

Runs the existing CLI/programmatic workflow with built-in sample data
and prints a concise summary.  Does NOT duplicate core workflow logic.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def _find_sample_input() -> Path:
    """Locate the built-in sample-data JSON file."""
    # Search relative to this script first, then relative to cwd.
    candidates = [
        Path(__file__).resolve().parent.parent
        / "data"
        / "sample_inputs"
        / "sample_data_science_user.json",
        Path("data/sample_inputs/sample_data_science_user.json"),
    ]
    for cand in candidates:
        if cand.is_file():
            return cand
    print(
        "Error: Cannot locate sample input file "
        "(data/sample_inputs/sample_data_science_user.json).",
        file=sys.stderr,
    )
    sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the resume_pdf_agent demo workflow.",
    )
    parser.add_argument(
        "--output-dir",
        default="outputs/demo_run",
        help="Output directory (default: outputs/demo_run).",
    )
    parser.add_argument(
        "--pdf-backend",
        default="mock",
        choices=("mock", "weasyprint", "playwright"),
        help="PDF backend (default: mock).",
    )
    parser.add_argument(
        "--write-frontend-page",
        action="store_true",
        default=True,
        help="Generate static index.html dashboard (default: True).",
    )
    parser.add_argument(
        "--no-frontend-page",
        action="store_true",
        help="Skip frontend page generation.",
    )
    parser.add_argument(
        "--include-jd",
        action="store_true",
        default=False,
        help="Also run with user-provided JD from sample file.",
    )
    parser.add_argument(
        "--include-llm-mock",
        action="store_true",
        default=False,
        help="Also run with mock LLM rewriting enabled.",
    )
    parser.add_argument(
        "--strict-confirmation-gate",
        action="store_true",
        default=False,
        help="Require confirmation before PDF generation.",
    )
    args = parser.parse_args()

    sample_input = _find_sample_input()

    # ------------------------------------------------------------------
    # Import workflow modules (lazy, so argparse --help is fast).
    # ------------------------------------------------------------------
    from resume_pdf_agent.models.pdf import PDFBackend
    from resume_pdf_agent.workflow.io import (
        ensure_output_dir,
        load_workflow_input_from_json,
    )
    from resume_pdf_agent.workflow.orchestrator import run_resume_workflow

    # --- Load input ----------------------------------------------------
    print(f"Loading sample input: {sample_input}")
    workflow_input = load_workflow_input_from_json(sample_input)

    # Apply CLI overrides
    workflow_input.output_dir = args.output_dir
    workflow_input.pdf_backend = PDFBackend(args.pdf_backend)

    # M15 JD mode
    if args.include_jd:
        jd_path = Path("data/sample_inputs/sample_data_science_jd.txt")
        if jd_path.is_file():
            workflow_input.use_user_provided_jd = True
            workflow_input.jd_file_path = str(jd_path)
            print(f"JD mode enabled: {jd_path}")
        else:
            print("Warning: JD sample file not found, skipping JD mode.")
    # M16 LLM mock mode
    if args.include_llm_mock:
        workflow_input.enable_llm_rewriting = True
        workflow_input.llm_provider = "mock"
        print("LLM mock mode enabled.")
    # M14 confirmation gate
    if args.strict_confirmation_gate:
        workflow_input.require_confirmation_before_pdf = True
        print("Strict confirmation gate enabled.")

    # --- Run workflow --------------------------------------------------
    print(f"Running workflow (pdf_backend={args.pdf_backend}) ...")
    output_dir = ensure_output_dir(args.output_dir)
    result = run_resume_workflow(workflow_input)

    # --- Summary -------------------------------------------------------
    print()
    print("=" * 60)
    print("  DEMO WORKFLOW SUMMARY")
    print("=" * 60)
    print(f"  Status:              {result.status.value}")
    print(f"  Output directory:    {output_dir}")
    print(f"  Criteria profile:    {result.selected_criteria_profile_id or 'N/A'}")
    primary_type = (
        result.primary_resume_type.value
        if result.primary_resume_type
        else "N/A"
    )
    print(f"  Primary resume type: {primary_type}")
    print(f"  Selected template:   {result.selected_template_id or 'N/A'}")
    print(f"  HTML output:         {result.html_output_path or 'N/A'}")
    print(f"  PDF output:          {result.pdf_output_path or 'N/A'}")
    print(f"  Warnings:            {len(result.warnings)}")
    print(f"  Errors:              {len(result.errors)}")
    if result.confirmation_packet_path:
        print(f"  Confirmation packet: {result.confirmation_packet_path}")
    if result.parsed_jd_path:
        print(f"  Parsed JD:           {result.parsed_jd_path}")
    if result.jd_criteria_profile_path:
        print(f"  JD criteria profile: {result.jd_criteria_profile_path}")
    if result.llm_rewrite_result_path:
        print(f"  LLM rewrite result:  {result.llm_rewrite_result_path}")

    # --- Frontend page ------------------------------------------------
    index_path: str | None = None
    write_frontend = args.write_frontend_page and not args.no_frontend_page
    if write_frontend:
        try:
            from resume_pdf_agent.frontend import render_frontend_workflow_page

            page_result = render_frontend_workflow_page(
                workflow_input=workflow_input,
                workflow_result=result,
                output_path=Path(args.output_dir) / "index.html",
            )
            if page_result.output_path:
                index_path = str(page_result.output_path)
                print(f"  Frontend page:       {index_path}")
        except Exception as exc:
            print(f"  Frontend page:       ERROR ({exc})")

    print("=" * 60)

    # --- Quick self-check ---------------------------------------------
    checks_ok = True
    if not Path(args.output_dir, "resume.html").is_file():
        print("[WARN] resume.html not found in output directory.")
        checks_ok = False
    if not Path(args.output_dir, "resume.pdf").is_file():
        print("[WARN] resume.pdf not found in output directory.")
        checks_ok = False
    if write_frontend and not index_path:
        print("[WARN] Frontend page was not generated.")
        checks_ok = False

    if checks_ok:
        print("[OK] Key output artifacts present.")

    # Non-zero exit if workflow itself failed.
    from resume_pdf_agent.models.workflow import WorkflowRunStatus

    if result.status == WorkflowRunStatus.FAILED:
        sys.exit(1)


if __name__ == "__main__":
    main()
