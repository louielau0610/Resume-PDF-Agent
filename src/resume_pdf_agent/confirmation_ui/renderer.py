"""Renderer for M20 browser confirmation UI page."""

from __future__ import annotations

import json
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from resume_pdf_agent.confirmation_ui.context import build_confirmation_ui_context
from resume_pdf_agent.models.confirmation import ConfirmationPacket
from resume_pdf_agent.models.confirmation_ui import (
    ConfirmationUIOptions,
    ConfirmationUIResult,
    ConfirmationUIStatus,
)

_TEMPLATE_DIR = Path(__file__).resolve().parent / "templates"
_STATIC_DIR = Path(__file__).resolve().parent / "static"


def _create_env() -> Environment:
    return Environment(
        loader=FileSystemLoader(str(_TEMPLATE_DIR)),
        autoescape=False,
        trim_blocks=True,
        lstrip_blocks=True,
    )


def _read_static(filename: str) -> str:
    path = _STATIC_DIR / filename
    if path.is_file():
        return path.read_text(encoding="utf-8")
    return ""


def render_confirmation_ui_page(
    packet: ConfirmationPacket,
    output_path: str | Path,
    options: ConfirmationUIOptions | None = None,
) -> ConfirmationUIResult:
    """Render a static confirmation review HTML page.

    Parameters
    ----------
    packet : ConfirmationPacket
        The confirmation packet to render.
    output_path : str | Path
        Where to write the HTML file.
    options : ConfirmationUIOptions | None
        UI rendering options.

    Returns
    -------
    ConfirmationUIResult
    """
    output_path = Path(output_path)
    opts = options or ConfirmationUIOptions()
    warnings: list[str] = []
    errors: list[str] = []

    try:
        env = _create_env()
        template = env.get_template("confirmation_page.html.j2")
        css = _read_static("confirmation_page.css")
        js = _read_static("confirmation_page.js")
        context = build_confirmation_ui_context(packet, opts)
        context["css"] = css
        context["js"] = js

        html = template.render(**context)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(html, encoding="utf-8")

        return ConfirmationUIResult(
            status=ConfirmationUIStatus.RENDERED,
            output_path=str(output_path),
            html=html,
            warnings=warnings,
            errors=errors,
            item_count=len(packet.items),
            blocking_count=packet.blocking_count,
            summary=f"Confirmation UI rendered to {output_path}",
        )
    except Exception as exc:
        errors.append(str(exc))
        return ConfirmationUIResult(
            status=ConfirmationUIStatus.FAILED,
            warnings=warnings,
            errors=errors,
            item_count=len(packet.items) if packet else 0,
            blocking_count=packet.blocking_count if packet else 0,
            summary=f"Failed to render confirmation UI: {exc}",
        )


def render_confirmation_ui_from_packet_file(
    packet_path: str | Path,
    output_path: str | Path,
    options: ConfirmationUIOptions | None = None,
) -> ConfirmationUIResult:
    """Load a confirmation packet JSON and render the UI page.

    Parameters
    ----------
    packet_path : str | Path
        Path to confirmation_packet.json.
    output_path : str | Path
        Where to write the HTML file.
    options : ConfirmationUIOptions | None
        UI rendering options.

    Returns
    -------
    ConfirmationUIResult
    """
    packet_path = Path(packet_path)
    if not packet_path.is_file():
        return ConfirmationUIResult(
            status=ConfirmationUIStatus.FAILED,
            errors=[f"Packet file not found: {packet_path}"],
            summary=f"Packet file not found: {packet_path}",
        )

    data = json.loads(packet_path.read_text(encoding="utf-8"))
    packet = ConfirmationPacket(**data)
    return render_confirmation_ui_page(packet, output_path, options)
