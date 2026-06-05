from resume_pdf_agent.pdf.validation import get_pdf_file_size, validate_pdf_output


def test_validate_pdf_output_detects_missing_file(tmp_path):
    valid, messages = validate_pdf_output(tmp_path / "missing.pdf")

    assert valid is False
    assert "does not exist" in messages[0]


def test_validate_pdf_output_detects_empty_file(tmp_path):
    path = tmp_path / "empty.pdf"
    path.write_bytes(b"")

    valid, messages = validate_pdf_output(path)

    assert valid is False
    assert "empty" in messages[0]
    assert get_pdf_file_size(path) == 0


def test_validate_pdf_output_accepts_non_empty_pdf_header(tmp_path):
    path = tmp_path / "resume.pdf"
    path.write_bytes(b"%PDF-1.4\n%%EOF\n")

    valid, messages = validate_pdf_output(path)

    assert valid is True
    assert messages == []
    assert get_pdf_file_size(path) > 0


def test_validate_pdf_output_rejects_non_pdf_header(tmp_path):
    path = tmp_path / "resume.pdf"
    path.write_text("not a pdf", encoding="utf-8")

    valid, messages = validate_pdf_output(path)

    assert valid is False
    assert "%PDF header" in messages[0]
