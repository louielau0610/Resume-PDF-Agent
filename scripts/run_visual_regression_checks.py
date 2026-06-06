"""Standalone visual regression check script for M18.

Usage:
    py scripts/run_visual_regression_checks.py --output-dir outputs/visual_regression_check
    py scripts/run_visual_regression_checks.py --output-dir outputs/vr_check --capture-screenshots
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT / "src"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Run visual regression checks on generated outputs.")
    parser.add_argument("--output-dir", default="outputs/visual_regression_check", help="Output directory.")
    parser.add_argument("--capture-screenshots", action="store_true", default=False, help="Capture screenshots if Playwright is available.")
    parser.add_argument("--no-capture-screenshots", action="store_false", dest="capture_screenshots")
    parser.add_argument("--include-jd-mode", action="store_true", default=False, help="Also test JD mode workflow.")
    parser.add_argument("--include-llm-mock", action="store_true", default=False, help="Also test mock LLM workflow.")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    all_passed = True

    # ── 1. Run baseline workflow ──────────────────────────────────────
    print("=== 1. Running baseline workflow ===")
    from resume_pdf_agent.workflow.io import load_workflow_input_from_json
    from resume_pdf_agent.workflow.orchestrator import run_resume_workflow

    sample_path = _REPO_ROOT / "data" / "sample_inputs" / "sample_data_science_user.json"
    wf_input = load_workflow_input_from_json(sample_path)
    wf_input.output_dir = str(output_dir)

    result = run_resume_workflow(wf_input)
    print(f"  Status: {result.status.value}")
    print(f"  HTML: {result.html_output_path or 'N/A'}")
    print(f"  PDF: {result.pdf_output_path or 'N/A'}")

    # ── 2. HTML structure checks ──────────────────────────────────────
    print("\n=== 2. HTML structure checks ===")

    from resume_pdf_agent.visual_regression.html_checks import (
        check_dashboard_html_structure,
        check_resume_html_structure,
    )

    # We need to generate the frontend page for dashboard checks
    # First, generate it
    try:
        from resume_pdf_agent.frontend import render_frontend_workflow_page
        page_result = render_frontend_workflow_page(
            workflow_input=wf_input,
            workflow_result=result,
            output_path=output_dir / "index.html",
        )
        print(f"  Frontend page: {page_result.output_path or 'N/A'}")
    except Exception as exc:
        print(f"  Frontend page error: {exc}")

    # Check index.html
    indexPath = output_dir / "index.html"
    if indexPath.is_file():
        html = indexPath.read_text(encoding="utf-8")
        dash_issues = check_dashboard_html_structure(html)
        if dash_issues:
            print("  Dashboard issues:")
            for i in dash_issues:
                print(f"    - {i}")
            all_passed = False
        else:
            print("  Dashboard structure: OK")
    else:
        print("  index.html not found!")
        all_passed = False

    # Check resume.html
    resumePath = output_dir / "resume.html"
    if resumePath.is_file():
        html = resumePath.read_text(encoding="utf-8")
        resume_issues = check_resume_html_structure(html)
        if resume_issues:
            print("  Resume HTML issues:")
            for i in resume_issues:
                print(f"    - {i}")
            all_passed = False
        else:
            print("  Resume HTML structure: OK")
    else:
        print("  resume.html not found!")
        all_passed = False

    # ── 3. Artifact validation ────────────────────────────────────────
    print("\n=== 3. Artifact validation ===")
    from resume_pdf_agent.visual_regression.artifacts import (
        collect_expected_visual_artifacts,
        validate_pdf_artifact,
    )
    arts = collect_expected_visual_artifacts(output_dir)
    for name, exists in arts.items():
        if name in ("index.html", "resume.html", "resume.pdf"):
            status = "OK" if exists else "MISSING"
            print(f"  [{status}] {name}")
            if not exists:
                all_passed = False

    pdf_issues = validate_pdf_artifact(output_dir / "resume.pdf")
    if pdf_issues:
        for i in pdf_issues:
            print(f"  - {i}")
        all_passed = False
    else:
        print("  PDF artifact: OK")

    # ── 4. Optional screenshots ───────────────────────────────────────
    if args.capture_screenshots:
        print("\n=== 4. Screenshot capture ===")
        from resume_pdf_agent.visual_regression.optional_screenshots import (
            capture_html_screenshot_if_available,
            is_playwright_available,
        )
        if is_playwright_available():
            ok, warns = capture_html_screenshot_if_available(
                output_dir / "index.html",
                output_dir / "screenshot_dashboard.png",
            )
            print(f"  Dashboard screenshot: {'OK' if ok else 'skipped'}")
            ok, warns = capture_html_screenshot_if_available(
                output_dir / "resume.html",
                output_dir / "screenshot_resume.png",
            )
            print(f"  Resume screenshot: {'OK' if ok else 'skipped'}")
        else:
            print("  Playwright not available — screenshots skipped.")

    # ── Result ────────────────────────────────────────────────────────
    print(f"\n{'='*40}")
    if all_passed:
        print("RESULT: All visual regression checks PASSED.")
        return 0
    else:
        print("RESULT: Some visual regression checks FAILED.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
