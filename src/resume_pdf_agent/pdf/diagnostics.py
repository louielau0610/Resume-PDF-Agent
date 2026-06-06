"""PDF backend diagnostics for M17.

Provides production-readiness checks for PDF backends without requiring
any backend to be installed. All checks are import-safe and do not
install packages or make network calls.
"""

from __future__ import annotations

from importlib.util import find_spec

from resume_pdf_agent.models.pdf import PDFBackend


def check_mock_backend_diagnostics() -> dict:
    """Diagnostics for the mock PDF backend.

    The mock backend is always available and is used for deterministic
    testing. It writes minimal PDF-like output without real rendering.
    """
    return {
        "backend": PDFBackend.MOCK.value,
        "available": True,
        "production_recommended": False,
        "package_import_ok": True,
        "error": None,
        "setup_hint": "Mock backend requires no installation. Always available for testing.",
        "notes": [
            "Mock backend writes minimal valid PDF-like bytes.",
            "Suitable for deterministic tests and CI/CD.",
            "Does NOT produce real rendered PDF output.",
            "Use WeasyPrint or Playwright for production PDF generation.",
        ],
    }


def check_weasyprint_diagnostics() -> dict:
    """Diagnostics for the WeasyPrint PDF backend.

    WeasyPrint is the preferred production backend for HTML-to-PDF
    conversion. This check only verifies import availability; it does
    NOT install WeasyPrint or any system dependencies.
    """
    package_ok = find_spec("weasyprint") is not None

    if package_ok:
        try:
            from weasyprint import HTML  # noqa: F401
            import_ok = True
            error_msg = None
        except Exception as exc:
            import_ok = False
            error_msg = f"WeasyPrint import failed: {exc}"
    else:
        import_ok = False
        error_msg = "WeasyPrint package is not installed."

    setup_hint = (
        "Install WeasyPrint: pip install weasyprint"
        if not package_ok
        else (
            "WeasyPrint is installed but may need system dependencies. "
            "See https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#installation"
            if not import_ok
            else "WeasyPrint is available and ready for PDF generation."
        )
    )

    return {
        "backend": PDFBackend.WEASYPRINT.value,
        "available": import_ok,
        "production_recommended": True,
        "package_import_ok": import_ok,
        "error": error_msg,
        "setup_hint": setup_hint,
        "notes": [
            "WeasyPrint is the preferred production PDF backend.",
            "Requires system libraries (GTK, Pango, etc.) on some platforms.",
            "Consult official WeasyPrint docs for OS-specific setup.",
            "Not required for tests — mock backend is used by default.",
        ],
    }


def check_playwright_diagnostics() -> dict:
    """Diagnostics for the Playwright PDF backend.

    Playwright is an alternative backend using browser-based rendering.
    This check only verifies import availability; it does NOT install
    browsers or make network calls.
    """
    package_ok = find_spec("playwright") is not None

    if package_ok:
        try:
            from playwright.sync_api import sync_playwright  # noqa: F401
            import_ok = True
            error_msg = None
        except Exception as exc:
            import_ok = False
            error_msg = f"Playwright import failed: {exc}"
    else:
        import_ok = False
        error_msg = "Playwright package is not installed."

    setup_hint = (
        "Install Playwright: pip install playwright && playwright install chromium"
        if not package_ok
        else "Playwright is installed."
    )

    return {
        "backend": PDFBackend.PLAYWRIGHT.value,
        "available": import_ok,
        "production_recommended": False,
        "package_import_ok": import_ok,
        "error": error_msg,
        "setup_hint": setup_hint,
        "notes": [
            "Playwright provides browser-based PDF rendering.",
            "Requires browser binaries (chromium).",
            "Not the default production backend — WeasyPrint is preferred.",
            "Available as an alternative for complex CSS/layout scenarios.",
        ],
    }


def get_pdf_backend_diagnostics(backend: PDFBackend) -> dict:
    """Get diagnostics for a specific PDF backend.

    Parameters
    ----------
    backend : PDFBackend
        Which backend to check.

    Returns
    -------
    dict
        Diagnostic information as a dictionary.
    """
    if backend == PDFBackend.MOCK:
        return check_mock_backend_diagnostics()
    elif backend == PDFBackend.WEASYPRINT:
        return check_weasyprint_diagnostics()
    elif backend == PDFBackend.PLAYWRIGHT:
        return check_playwright_diagnostics()
    else:
        return {
            "backend": str(backend),
            "available": False,
            "production_recommended": False,
            "package_import_ok": False,
            "error": f"Unknown backend: {backend}",
            "setup_hint": "Use one of: mock, weasyprint, playwright.",
            "notes": [],
        }


def get_all_pdf_backend_diagnostics() -> dict[str, dict]:
    """Get diagnostics for all supported PDF backends.

    Returns
    -------
    dict[str, dict]
        Mapping of backend name to diagnostic dict.
    """
    return {
        PDFBackend.MOCK.value: check_mock_backend_diagnostics(),
        PDFBackend.WEASYPRINT.value: check_weasyprint_diagnostics(),
        PDFBackend.PLAYWRIGHT.value: check_playwright_diagnostics(),
    }


def summarize_pdf_backend_status() -> str:
    """Return a human-readable summary of all PDF backend statuses.

    Returns
    -------
    str
        Multi-line summary string.
    """
    all_diag = get_all_pdf_backend_diagnostics()
    lines: list[str] = []
    lines.append("PDF Backend Status Summary")
    lines.append("=" * 40)

    for name, diag in all_diag.items():
        status = "AVAILABLE" if diag["available"] else "UNAVAILABLE"
        prod = " (production recommended)" if diag["production_recommended"] else ""
        lines.append(f"  {name}: {status}{prod}")
        if diag["error"]:
            lines.append(f"    Error: {diag['error']}")
        lines.append(f"    Hint: {diag['setup_hint']}")

    lines.append("")
    lines.append("Default for tests: mock (always available, deterministic)")
    lines.append("Recommended for production: weasyprint")
    return "\n".join(lines)
