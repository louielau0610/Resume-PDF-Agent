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
    parser.add_argument(
        "--write-confirmation-ui",
        action="store_true",
        default=False,
        help="Write a browser confirmation review page (confirmation.html).",
    )
    parser.add_argument(
        "--write-jd-upload-ui",
        action="store_true",
        default=False,
        help="Write a browser JD upload UI page (jd_upload.html).",
    )
    parser.add_argument(
        "--write-llm-review-ui",
        action="store_true",
        default=False,
        help="Write a browser LLM rewrite review page (llm_review.html). Requires --include-llm-mock.",
    )
    parser.add_argument(
        "--write-llm-review-decision-summary",
        action="store_true",
        default=False,
        help="Create deterministic sample LLM review decisions and write advisory summary artifacts. Requires --include-llm-mock.",
    )
    parser.add_argument(
        "--write-llm-application-plan",
        action="store_true",
        default=False,
        help="Create a plan-only LLM candidate application artifact. Requires --include-llm-mock.",
    )
    parser.add_argument(
        "--write-llm-application-preview-ui",
        action="store_true",
        default=False,
        help="Write a local static manual LLM application preview page. Requires --include-llm-mock.",
    )
    parser.add_argument(
        "--write-llm-pre-application-validation",
        action="store_true",
        default=False,
        help="Run strict pre-application validation and write validation reports. Requires --include-llm-mock.",
    )
    parser.add_argument(
        "--write-llm-manual-patch-preview",
        action="store_true",
        default=False,
        help="Generate manual patch-preview artifacts (JSON/MD/HTML). Requires --include-llm-mock.",
    )
    parser.add_argument(
        "--write-llm-manual-approval-checklist",
        action="store_true",
        default=False,
        help="Build a manual approval checklist from patch preview. Requires --include-llm-mock.",
    )
    parser.add_argument(
        "--write-llm-human-final-edit-pack",
        action="store_true",
        default=False,
        help="Build a human-only final edit instruction pack from checklist. Requires --include-llm-mock.",
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
    # M20 confirmation UI
    if args.write_confirmation_ui:
        workflow_input.write_confirmation_ui = True
        print("Confirmation UI enabled.")
    # M21 JD upload UI
    if args.write_jd_upload_ui:
        try:
            from resume_pdf_agent.jd_ui import render_jd_upload_ui_page

            jd_ui_path = Path(args.output_dir) / "jd_upload.html"
            jd_ui_result = render_jd_upload_ui_page(jd_ui_path)
            if jd_ui_result.output_path:
                print(f"JD Upload UI page:    {jd_ui_result.output_path}")
        except Exception as exc:
            print(f"JD Upload UI page:    ERROR ({exc})")
    # M22 LLM review UI (requires --include-llm-mock)
    if args.write_llm_review_ui:
        if not args.include_llm_mock:
            print("Warning: --write-llm-review-ui requires --include-llm-mock. Skipping.")
        else:
            workflow_input.write_llm_review_ui = True
            print("LLM review UI enabled (post-workflow).")
    if args.write_llm_review_decision_summary and not args.include_llm_mock:
        print("Warning: --write-llm-review-decision-summary requires --include-llm-mock. Skipping.")
    if args.write_llm_application_plan and not args.include_llm_mock:
        print("Warning: --write-llm-application-plan requires --include-llm-mock. Skipping.")
    if args.write_llm_application_preview_ui and not args.include_llm_mock:
        print("Warning: --write-llm-application-preview-ui requires --include-llm-mock. Skipping.")

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
    if result.llm_review_ui_path:
        print(f"  LLM review UI:       {result.llm_review_ui_path}")

    if (
        args.write_llm_review_decision_summary
        or args.write_llm_application_plan
        or args.write_llm_application_preview_ui
        or args.write_llm_pre_application_validation
        or args.write_llm_manual_patch_preview
        or args.write_llm_manual_approval_checklist
        or args.write_llm_human_final_edit_pack
    ) and args.include_llm_mock:
        try:
            import json

            from resume_pdf_agent.llm_application_plan import (
                plan_llm_candidate_application_to_files,
            )
            from resume_pdf_agent.llm_application_preview_ui import (
                render_llm_application_preview_ui_from_plan_file,
            )
            from resume_pdf_agent.llm_review_decisions import (
                summarize_llm_review_decisions_to_files,
            )

            result_path = Path(result.llm_rewrite_result_path or "")
            if not result_path.is_file():
                raise FileNotFoundError("LLM rewrite result was not generated.")
            raw_result = json.loads(result_path.read_text(encoding="utf-8"))
            candidate_ids = [c["candidate_id"] for c in raw_result.get("candidates", [])]
            action_cycle = [
                "approve_candidate",
                "reject_candidate",
                "needs_editing",
                "provide_note",
                "ignore_for_now",
            ]
            decisions = []
            for idx, candidate_id in enumerate(candidate_ids):
                action = action_cycle[idx % len(action_cycle)]
                decisions.append(
                    {
                        "candidate_id": candidate_id,
                        "decision": action,
                        "reviewer_note": (
                            f"Demo note for {candidate_id}"
                            if action == "provide_note"
                            else None
                        ),
                        "replacement_text": None,
                    }
                )
            decisions_path = Path(args.output_dir) / "llm_rewrite_review_decisions.json"
            decisions_path.write_text(
                json.dumps(
                    {
                        "reviewer_name": "demo",
                        "reviewed_at": "demo-static",
                        "notes": "Deterministic demo decisions; advisory only.",
                        "decisions": decisions,
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )
            summary_json = Path(args.output_dir) / "llm_rewrite_review_decision_summary.json"
            summary_md = Path(args.output_dir) / "llm_rewrite_review_decision_summary.md"
            summarize_llm_review_decisions_to_files(
                decisions_path=decisions_path,
                result_path=result_path,
                output_json_path=summary_json,
                output_md_path=summary_md,
            )
            print(f"  LLM decisions:       {decisions_path}")
            print(f"  LLM summary JSON:    {summary_json}")
            print(f"  LLM summary MD:      {summary_md}")
            if args.write_llm_application_plan or args.write_llm_application_preview_ui:
                plan_json = Path(args.output_dir) / "llm_rewrite_application_plan.json"
                plan_md = Path(args.output_dir) / "llm_rewrite_application_plan.md"
                if not plan_json.is_file() or not plan_md.is_file():
                    plan_llm_candidate_application_to_files(
                        result_path=result_path,
                        decisions_path=decisions_path,
                        summary_path=summary_json,
                        output_json_path=plan_json,
                        output_md_path=plan_md,
                    )
                print(f"  LLM app plan JSON:   {plan_json}")
                print(f"  LLM app plan MD:     {plan_md}")
                if args.write_llm_application_preview_ui:
                    preview_html = (
                        Path(args.output_dir) / "llm_rewrite_application_preview.html"
                    )
                    preview_result = render_llm_application_preview_ui_from_plan_file(
                        plan_json,
                        preview_html,
                    )
                    if preview_result.output_path:
                        print(f"  LLM app preview UI:  {preview_result.output_path}")
                    if preview_result.errors:
                        print(f"  LLM app preview UI:  ERROR ({'; '.join(preview_result.errors)})")
                if args.write_llm_pre_application_validation:
                    from resume_pdf_agent.llm_pre_application_validation import (
                        write_pre_application_validation_to_files,
                    )
                    val_json = Path(args.output_dir) / "llm_rewrite_pre_application_validation.json"
                    val_md = Path(args.output_dir) / "llm_rewrite_pre_application_validation.md"
                    val_report = write_pre_application_validation_to_files(
                        plan_path=plan_json,
                        output_json_path=val_json,
                        output_md_path=val_md,
                        result_path=result_path,
                        decisions_path=decisions_path,
                        summary_path=summary_json,
                    )
                    print(f"  M26 validation JSON: {val_json}")
                    print(f"  M26 validation MD:   {val_md}")
                    print(f"  M26 passed/blocked:  {val_report.passed_count}/{val_report.blocked_count}")
                if args.write_llm_manual_patch_preview:
                    from resume_pdf_agent.llm_manual_patch_preview import (
                        write_manual_patch_preview_to_files,
                    )
                    val_for_m27 = Path(args.output_dir) / "llm_rewrite_pre_application_validation.json"
                    pv_json = Path(args.output_dir) / "llm_rewrite_manual_patch_preview.json"
                    pv_md = Path(args.output_dir) / "llm_rewrite_manual_patch_preview.md"
                    pv_html = Path(args.output_dir) / "llm_rewrite_manual_patch_preview.html"
                    pv_report = write_manual_patch_preview_to_files(
                        plan_path=plan_json,
                        validation_path=val_for_m27,
                        output_json_path=pv_json,
                        output_md_path=pv_md,
                        output_html_path=pv_html,
                    )
                    print(f"  M27 preview JSON:    {pv_json}")
                    print(f"  M27 preview MD:      {pv_md}")
                    print(f"  M27 preview HTML:    {pv_html}")
                    print(f"  M27 ready/blocked:   {pv_report.preview_ready_count}/{pv_report.blocked_count}")
                if args.write_llm_manual_approval_checklist:
                    from resume_pdf_agent.llm_manual_approval_checklist import (
                        write_manual_approval_checklist_to_files,
                    )
                    pv_for_cl = Path(args.output_dir) / "llm_rewrite_manual_patch_preview.json"
                    cl_json = Path(args.output_dir) / "llm_rewrite_manual_patch_approval_checklist.json"
                    cl_md = Path(args.output_dir) / "llm_rewrite_manual_patch_approval_checklist.md"
                    cl_html = Path(args.output_dir) / "llm_rewrite_manual_patch_approval_checklist.html"
                    cl_report = write_manual_approval_checklist_to_files(
                        preview_path=pv_for_cl,
                        output_json_path=cl_json,
                        output_md_path=cl_md,
                        output_html_path=cl_html,
                    )
                    print(f"  M28 checklist JSON:  {cl_json}")
                    print(f"  M28 checklist MD:    {cl_md}")
                    print(f"  M28 checklist HTML:  {cl_html}")
                    print(f"  M28 review/blocked:  {cl_report.review_required_count}/{cl_report.blocked_count}")
                if args.write_llm_human_final_edit_pack:
                    from resume_pdf_agent.llm_human_final_edit_pack import (
                        write_human_final_edit_pack_to_files,
                    )
                    cl_for_ep = Path(args.output_dir) / "llm_rewrite_manual_patch_approval_checklist.json"
                    ep_json = Path(args.output_dir) / "llm_rewrite_human_final_edit_instruction_pack.json"
                    ep_md = Path(args.output_dir) / "llm_rewrite_human_final_edit_instruction_pack.md"
                    ep_html = Path(args.output_dir) / "llm_rewrite_human_final_edit_instruction_pack.html"
                    ep_report = write_human_final_edit_pack_to_files(
                        checklist_path=cl_for_ep,
                        output_json_path=ep_json,
                        output_md_path=ep_md,
                        output_html_path=ep_html,
                    )
                    print(f"  M29 edit pack JSON:  {ep_json}")
                    print(f"  M29 edit pack MD:    {ep_md}")
                    print(f"  M29 edit pack HTML:  {ep_html}")
                    print(f"  M29 ready/blocked:   {ep_report.instruction_ready_count}/{ep_report.blocked_count}")
        except Exception as exc:
            print(f"  LLM planning:        ERROR ({exc})")

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
