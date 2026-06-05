from resume_pdf_agent.models import (
    EvidenceLevel,
    HTMLRenderStatus,
    MetricStatus,
    PDFBackend,
    PDFGenerationOptions,
    PDFGenerationStatus,
    ResumeBullet,
    ResumeSection,
)
from resume_pdf_agent.pdf import (
    generate_pdf_from_html_result,
    generate_resume_pdf,
    is_pdf_backend_available,
)
from resume_pdf_agent.rendering import render_resume_html
from resume_pdf_agent.sample_data import SAMPLE_RESUME_CONTENT, SAMPLE_USER_PROFILE
from resume_pdf_agent.templates import select_internal_template


def test_pdf_generation_functions_can_be_imported():
    assert callable(is_pdf_backend_available)
    assert callable(generate_pdf_from_html_result)
    assert callable(generate_resume_pdf)


def test_is_pdf_backend_available_returns_boolean():
    assert isinstance(is_pdf_backend_available(PDFBackend.WEASYPRINT), bool)
    assert is_pdf_backend_available(PDFBackend.MOCK) is True


def test_generate_pdf_from_html_result_with_mock_backend_writes_pdf(tmp_path):
    selection = select_internal_template(SAMPLE_USER_PROFILE, SAMPLE_RESUME_CONTENT)
    html_result = render_resume_html(SAMPLE_USER_PROFILE, SAMPLE_RESUME_CONTENT, selection)
    output_path = tmp_path / "resume.pdf"

    result = generate_pdf_from_html_result(
        html_result,
        output_path,
        PDFGenerationOptions(backend=PDFBackend.MOCK),
    )

    assert result.status == PDFGenerationStatus.GENERATED_WITH_WARNINGS
    assert result.output_path == str(output_path)
    assert result.file_size_bytes and result.file_size_bytes > 0
    assert output_path.read_bytes().startswith(b"%PDF")
    assert "Mock PDF backend" in " ".join(result.warnings)


def test_generate_resume_pdf_uses_m8_rendering_and_mock_backend(tmp_path):
    selection = select_internal_template(SAMPLE_USER_PROFILE, SAMPLE_RESUME_CONTENT)

    result = generate_resume_pdf(
        SAMPLE_USER_PROFILE,
        SAMPLE_RESUME_CONTENT,
        selection,
        output_path=tmp_path / "resume.pdf",
        pdf_options=PDFGenerationOptions(backend=PDFBackend.MOCK),
    )

    assert result.status == PDFGenerationStatus.GENERATED_WITH_WARNINGS
    assert result.output_path is not None
    assert result.file_size_bytes and result.file_size_bytes > 0


def test_html_render_warnings_are_preserved_in_pdf_result(tmp_path):
    content = SAMPLE_RESUME_CONTENT.model_copy(
        update={
            "sections": [
                ResumeSection(
                    heading="Projects",
                    bullets=[
                        ResumeBullet(
                            text="Claim requiring confirmation.",
                            evidence_level=EvidenceLevel.NEEDS_USER_CONFIRMATION,
                            metric_status=MetricStatus.NOT_APPLICABLE,
                            risk_flags=["truthfulness_risk"],
                        )
                    ],
                )
            ]
        },
        deep=True,
    )
    selection = select_internal_template(SAMPLE_USER_PROFILE, content)
    html_result = render_resume_html(SAMPLE_USER_PROFILE, content, selection)

    result = generate_pdf_from_html_result(
        html_result,
        tmp_path / "resume.pdf",
        PDFGenerationOptions(backend=PDFBackend.MOCK),
    )

    assert any("needs user confirmation" in warning for warning in result.warnings)
    assert any("risk flags" in warning for warning in result.warnings)


def test_non_successful_html_result_fails_without_pdf_output(tmp_path):
    selection = select_internal_template(SAMPLE_USER_PROFILE, SAMPLE_RESUME_CONTENT)
    html_result = render_resume_html(SAMPLE_USER_PROFILE, SAMPLE_RESUME_CONTENT, selection)
    skipped_html = html_result.model_copy(update={"status": HTMLRenderStatus.SKIPPED_DUE_TO_INSUFFICIENT_CONTENT})

    result = generate_pdf_from_html_result(
        skipped_html,
        tmp_path / "resume.pdf",
        PDFGenerationOptions(backend=PDFBackend.MOCK),
    )

    assert result.status == PDFGenerationStatus.FAILED
    assert result.output_path is None
    assert not (tmp_path / "resume.pdf").exists()


def test_backend_unavailable_returns_skipped_when_not_fail_fast(tmp_path):
    selection = select_internal_template(SAMPLE_USER_PROFILE, SAMPLE_RESUME_CONTENT)
    html_result = render_resume_html(SAMPLE_USER_PROFILE, SAMPLE_RESUME_CONTENT, selection)

    result = generate_pdf_from_html_result(
        html_result,
        tmp_path / "resume.pdf",
        PDFGenerationOptions(backend=PDFBackend.PLAYWRIGHT, fail_on_backend_unavailable=False),
    )

    if is_pdf_backend_available(PDFBackend.PLAYWRIGHT):
        assert result.status == PDFGenerationStatus.FAILED
        assert "not implemented" in " ".join(result.errors)
    else:
        assert result.status == PDFGenerationStatus.SKIPPED_BACKEND_UNAVAILABLE
        assert result.output_path is None


def test_backend_unavailable_returns_failed_when_fail_fast(tmp_path):
    selection = select_internal_template(SAMPLE_USER_PROFILE, SAMPLE_RESUME_CONTENT)
    html_result = render_resume_html(SAMPLE_USER_PROFILE, SAMPLE_RESUME_CONTENT, selection)

    result = generate_pdf_from_html_result(
        html_result,
        tmp_path / "resume.pdf",
        PDFGenerationOptions(backend=PDFBackend.PLAYWRIGHT, fail_on_backend_unavailable=True),
    )

    if is_pdf_backend_available(PDFBackend.PLAYWRIGHT):
        assert result.status == PDFGenerationStatus.FAILED
        assert "not implemented" in " ".join(result.errors)
    else:
        assert result.status == PDFGenerationStatus.FAILED
        assert "unavailable" in " ".join(result.errors)


def test_conversion_reminder_is_metadata_not_in_html_body(tmp_path):
    selection = select_internal_template(SAMPLE_USER_PROFILE, SAMPLE_RESUME_CONTENT)
    html_result = render_resume_html(SAMPLE_USER_PROFILE, SAMPLE_RESUME_CONTENT, selection)

    result = generate_pdf_from_html_result(
        html_result,
        tmp_path / "resume.pdf",
        PDFGenerationOptions(backend=PDFBackend.MOCK),
    )

    assert result.conversion_reminder is not None
    assert "Word, JPG, or PNG" in result.conversion_reminder
    assert "Word, JPG, or PNG" not in html_result.html
