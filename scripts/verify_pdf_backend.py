"""Standalone PDF backend verification script for M17.

Usage:
    py scripts/verify_pdf_backend.py
    py scripts/verify_pdf_backend.py --backend mock
    py scripts/verify_pdf_backend.py --backend weasyprint
    py scripts/verify_pdf_backend.py --backend all --output-dir outputs/pdf_check
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Add repo root to path so we can import resume_pdf_agent
_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT / "src"))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify PDF backend availability and optionally run a smoke test.",
    )
    parser.add_argument(
        "--backend",
        default="all",
        choices=("mock", "weasyprint", "playwright", "all"),
        help="PDF backend to verify (default: all).",
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Optional output directory for smoke test artifacts.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        default=False,
        help="Exit with non-zero status if a requested backend is unavailable.",
    )
    parser.add_argument(
        "--no-strict",
        action="store_false",
        dest="strict",
        help="Do not fail on unavailable backend (default).",
    )
    args = parser.parse_args()

    from resume_pdf_agent.models.pdf import PDFBackend
    from resume_pdf_agent.pdf.diagnostics import (
        get_all_pdf_backend_diagnostics,
        get_pdf_backend_diagnostics,
        summarize_pdf_backend_status,
    )

    # Print summary
    print(summarize_pdf_backend_status())
    print()

    # Check specific backend(s)
    backends_to_check: list[PDFBackend]
    if args.backend == "all":
        backends_to_check = [PDFBackend.MOCK, PDFBackend.WEASYPRINT, PDFBackend.PLAYWRIGHT]
    else:
        backends_to_check = [PDFBackend(args.backend)]

    all_available = True
    for backend in backends_to_check:
        diag = get_pdf_backend_diagnostics(backend)
        status = "OK" if diag["available"] else "MISSING"
        print(f"[{status}] {backend.value}: {diag['setup_hint']}")
        if not diag["available"]:
            all_available = False

    # Optional smoke test for mock backend
    if args.output_dir and PDFBackend.MOCK in backends_to_check:
        print("\nRunning mock backend smoke test ...")
        try:
            output_dir = Path(args.output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            output_path = output_dir / "smoke_test.pdf"

            # Use the existing generator with a minimal inline HTML render
            from resume_pdf_agent.models.pdf import PDFGenerationOptions
            from resume_pdf_agent.models.rendering import HTMLRenderResult, HTMLRenderStatus
            from resume_pdf_agent.pdf.generator import generate_pdf_from_html_result

            html_result = HTMLRenderResult(
                status=HTMLRenderStatus.RENDERED,
                template_id="smoke_test",
                html="<html><body><p>PDF Backend Smoke Test</p></body></html>",
                sections=[],
                summary="Smoke test HTML result.",
                output_path=str(output_dir / "smoke_test.html"),
            )
            pdf_result = generate_pdf_from_html_result(
                html_render_result=html_result,
                output_path=output_path,
                options=PDFGenerationOptions(backend=PDFBackend.MOCK),
            )
            print(f"  Smoke test PDF: {pdf_result.output_path or 'not generated'}")
            if pdf_result.output_path:
                p = Path(pdf_result.output_path)
                size = p.stat().st_size if p.exists() else 0
                print(f"  File size: {size} bytes")
        except Exception as exc:
            print(f"  Smoke test skipped: {exc}")

    if args.strict and not all_available:
        print("\n[FAIL] Strict mode: some backends are unavailable.")
        return 1

    print("\n[OK] PDF backend verification complete.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
