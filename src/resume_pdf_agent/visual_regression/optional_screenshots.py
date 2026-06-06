"""Optional screenshot diagnostics for M18 visual regression.

Playwright-based screenshot capture is entirely optional. All functions
return gracefully if Playwright is not available.
"""

from __future__ import annotations

from importlib.util import find_spec
from pathlib import Path


def is_playwright_available() -> bool:
    """Check if Playwright is installed and importable.

    Does NOT install packages or browsers.
    """
    if find_spec("playwright") is None:
        return False
    try:
        from playwright.sync_api import sync_playwright  # noqa: F401
        return True
    except Exception:
        return False


def capture_html_screenshot_if_available(
    html_path: str | Path,
    output_path: str | Path,
    viewport_width: int = 1440,
    viewport_height: int = 1000,
) -> tuple[bool, list[str]]:
    """Capture a screenshot of a local HTML file if Playwright is available.

    Parameters
    ----------
    html_path : str | Path
        Path to the local HTML file.
    output_path : str | Path
        Where to save the screenshot (PNG).
    viewport_width : int
        Viewport width in pixels.
    viewport_height : int
        Viewport height in pixels.

    Returns
    -------
    tuple[bool, list[str]]
        (success, warnings)
    """
    warnings: list[str] = []

    if not is_playwright_available():
        warnings.append(
            "Playwright is not installed. Screenshot capture skipped. "
            "Install with: pip install playwright && playwright install chromium"
        )
        return False, warnings

    html_path = Path(html_path)
    if not html_path.is_file():
        warnings.append(f"HTML file not found: {html_path}")
        return False, warnings

    try:
        from playwright.sync_api import sync_playwright

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(viewport={"width": viewport_width, "height": viewport_height})
            page.goto(f"file:///{html_path.as_posix()}")
            page.screenshot(path=str(output_path), full_page=True)
            browser.close()

        return True, warnings
    except Exception as exc:
        warnings.append(f"Screenshot capture failed: {exc}")
        return False, warnings
