"""PDF output validation helpers."""

from pathlib import Path


def get_pdf_file_size(output_path: str | Path) -> int | None:
    """Return PDF file size in bytes when the file exists."""

    path = Path(output_path)
    if not path.exists() or not path.is_file():
        return None
    return path.stat().st_size


def validate_pdf_output(output_path: str | Path) -> tuple[bool, list[str]]:
    """Validate deterministic local PDF output checks."""

    path = Path(output_path)
    messages: list[str] = []
    if not path.exists():
        return False, [f"PDF output file does not exist: {path}"]
    if not path.is_file():
        return False, [f"PDF output path is not a file: {path}"]
    size = path.stat().st_size
    if size <= 0:
        return False, [f"PDF output file is empty: {path}"]
    with path.open("rb") as file:
        header = file.read(4)
    if header != b"%PDF":
        messages.append(f"PDF output file does not start with %PDF header: {path}")
    return not messages, messages
