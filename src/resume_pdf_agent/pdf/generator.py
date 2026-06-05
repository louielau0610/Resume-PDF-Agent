"""PDF generation adapters for rendered resume HTML."""

from importlib.util import find_spec
from pathlib import Path

from resume_pdf_agent.models import (
    BulletEnhancementResult,
    HTMLRenderOptions,
    HTMLRenderResult,
    HTMLRenderStatus,
    PDFBackend,
    PDFGenerationOptions,
    PDFGenerationResult,
    PDFGenerationStatus,
    ResumeContent,
    TemplateSelectionResult,
    UserProfile,
)
from resume_pdf_agent.pdf.options import build_conversion_reminder, default_pdf_generation_options
from resume_pdf_agent.pdf.validation import get_pdf_file_size, validate_pdf_output
from resume_pdf_agent.rendering import render_resume_html

SUCCESSFUL_HTML_STATUSES = {
    HTMLRenderStatus.RENDERED,
    HTMLRenderStatus.RENDERED_WITH_WARNINGS,
}


def is_pdf_backend_available(
    backend: PDFBackend = PDFBackend.WEASYPRINT,
) -> bool:
    """Return whether a PDF backend appears available without runtime installation."""

    if backend == PDFBackend.MOCK:
        return True
    if backend == PDFBackend.WEASYPRINT:
        if find_spec("weasyprint") is None:
            return False
        try:
            from weasyprint import HTML  # noqa: F401
        except Exception:
            return False
        return True
    if backend == PDFBackend.PLAYWRIGHT:
        return find_spec("playwright") is not None
    return False


def _backend_unavailable_result(
    output_path: Path,
    options: PDFGenerationOptions,
    errors: list[str],
    warnings: list[str],
) -> PDFGenerationResult:
    status = (
        PDFGenerationStatus.FAILED
        if options.fail_on_backend_unavailable
        else PDFGenerationStatus.SKIPPED_BACKEND_UNAVAILABLE
    )
    return PDFGenerationResult(
        status=status,
        backend=options.backend,
        output_path=None,
        file_size_bytes=None,
        page_format=options.page_format,
        warnings=warnings,
        errors=errors,
        conversion_reminder=build_conversion_reminder(options.include_conversion_reminder),
        summary=(
            f"PDF generation did not create '{output_path}' because backend "
            f"'{options.backend.value}' is unavailable."
        ),
    )


def _write_mock_pdf(html: str, output_path: Path) -> None:
    escaped_note = html[:80].replace("\n", " ").replace("(", "[").replace(")", "]")
    content = (
        b"%PDF-1.4\n"
        b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
        b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n"
        b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] "
        b"/Contents 4 0 R >>\nendobj\n"
        + f"4 0 obj\n<< /Length {len(escaped_note) + 32} >>\nstream\n"
        f"BT /F1 12 Tf 72 720 Td (Mock PDF: {escaped_note}) Tj ET\n"
        "endstream\nendobj\ntrailer\n<< /Root 1 0 R >>\n%%EOF\n".encode("utf-8")
    )
    output_path.write_bytes(content)


def _generate_with_weasyprint(html: str, output_path: Path, options: PDFGenerationOptions) -> None:
    from weasyprint import CSS, HTML

    page_css = (
        f"@page {{ size: {options.page_format.value}; "
        f"margin: {options.margin_top_mm}mm {options.margin_right_mm}mm "
        f"{options.margin_bottom_mm}mm {options.margin_left_mm}mm; }}"
    )
    HTML(string=html, base_url=str(output_path.parent)).write_pdf(
        str(output_path),
        stylesheets=[CSS(string=page_css)],
        presentational_hints=options.print_background,
    )


def _generate_with_backend(html: str, output_path: Path, options: PDFGenerationOptions) -> list[str]:
    warnings: list[str] = []
    if options.backend == PDFBackend.MOCK:
        _write_mock_pdf(html, output_path)
        warnings.append("Mock PDF backend used for tests; this is not production PDF rendering.")
        return warnings
    if options.backend == PDFBackend.WEASYPRINT:
        _generate_with_weasyprint(html, output_path, options)
        return warnings
    if options.backend == PDFBackend.PLAYWRIGHT:
        raise RuntimeError("Playwright PDF backend adapter is not implemented in M9.")
    raise RuntimeError(f"Unsupported PDF backend: {options.backend.value}")


def generate_pdf_from_html_result(
    html_render_result: HTMLRenderResult,
    output_path: str | Path,
    options: PDFGenerationOptions | None = None,
) -> PDFGenerationResult:
    """Generate a local PDF from an M8 HTML render result."""

    pdf_options = options or default_pdf_generation_options()
    path = Path(output_path)
    warnings = list(html_render_result.warnings)
    conversion_reminder = build_conversion_reminder(pdf_options.include_conversion_reminder)

    if html_render_result.status not in SUCCESSFUL_HTML_STATUSES:
        return PDFGenerationResult(
            status=PDFGenerationStatus.FAILED,
            backend=pdf_options.backend,
            output_path=None,
            file_size_bytes=None,
            page_format=pdf_options.page_format,
            warnings=warnings,
            errors=[f"HTML render result status is not renderable: {html_render_result.status.value}"],
            conversion_reminder=conversion_reminder,
            summary="PDF generation failed because HTML rendering did not succeed.",
        )
    if not is_pdf_backend_available(pdf_options.backend):
        return _backend_unavailable_result(
            path,
            pdf_options,
            errors=[f"PDF backend '{pdf_options.backend.value}' is unavailable."],
            warnings=warnings,
        )

    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        backend_warnings = _generate_with_backend(html_render_result.html, path, pdf_options)
        warnings.extend(backend_warnings)
    except Exception as exc:
        return PDFGenerationResult(
            status=PDFGenerationStatus.FAILED,
            backend=pdf_options.backend,
            output_path=None,
            file_size_bytes=None,
            page_format=pdf_options.page_format,
            warnings=warnings,
            errors=[f"PDF backend '{pdf_options.backend.value}' failed: {exc}"],
            conversion_reminder=conversion_reminder,
            summary="PDF generation failed during backend conversion.",
        )

    valid, validation_messages = validate_pdf_output(path)
    if not valid:
        return PDFGenerationResult(
            status=PDFGenerationStatus.FAILED,
            backend=pdf_options.backend,
            output_path=str(path),
            file_size_bytes=get_pdf_file_size(path),
            page_format=pdf_options.page_format,
            warnings=warnings,
            errors=validation_messages,
            conversion_reminder=conversion_reminder,
            summary="PDF generation failed output validation.",
        )

    status = PDFGenerationStatus.GENERATED_WITH_WARNINGS if warnings else PDFGenerationStatus.GENERATED
    return PDFGenerationResult(
        status=status,
        backend=pdf_options.backend,
        output_path=str(path),
        file_size_bytes=get_pdf_file_size(path),
        page_format=pdf_options.page_format,
        warnings=warnings,
        errors=[],
        conversion_reminder=conversion_reminder,
        summary=(
            f"Generated local PDF at '{path}' from M8 HTML output using "
            f"backend '{pdf_options.backend.value}'."
        ),
    )


def generate_resume_pdf(
    user_profile: UserProfile,
    resume_content: ResumeContent,
    template_selection_result: TemplateSelectionResult,
    bullet_enhancement_result: BulletEnhancementResult | None = None,
    output_path: str | Path = "outputs/resume.pdf",
    html_options: HTMLRenderOptions | None = None,
    pdf_options: PDFGenerationOptions | None = None,
) -> PDFGenerationResult:
    """Render resume HTML with M8 and convert it to a local PDF."""

    html_result = render_resume_html(
        user_profile=user_profile,
        resume_content=resume_content,
        template_selection_result=template_selection_result,
        bullet_enhancement_result=bullet_enhancement_result,
        options=html_options,
    )
    return generate_pdf_from_html_result(
        html_render_result=html_result,
        output_path=output_path,
        options=pdf_options,
    )
