"""Safety tests for M20 confirmation UI."""

from __future__ import annotations

from pathlib import Path

from resume_pdf_agent.confirmation_ui.renderer import render_confirmation_ui_page
from resume_pdf_agent.confirmation_ui.safety import (
    escape_confirmation_ui_text,
    validate_confirmation_packet_for_ui,
)
from resume_pdf_agent.models.confirmation import (
    ConfirmationItem,
    ConfirmationItemType,
    ConfirmationPacket,
    ConfirmationPriority,
)


class TestEscapeConfirmationUiText:

    def test_escapes_script_tag(self):
        result = escape_confirmation_ui_text("<script>alert(1)</script>")
        assert "<script>" not in result
        assert "&lt;script&gt;" in result

    def test_escapes_quotes(self):
        result = escape_confirmation_ui_text('claim with "quotes"')
        assert "&quot;" in result

    def test_escapes_ampersand(self):
        result = escape_confirmation_ui_text("A & B")
        assert "&amp;" in result

    def test_normal_text_passes(self):
        result = escape_confirmation_ui_text("Normal claim text")
        assert result == "Normal claim text"


class TestValidateConfirmationPacketForUi:

    def test_valid_packet(self):
        packet = ConfirmationPacket(
            packet_id="test",
            items=[
                ConfirmationItem(
                    item_id="i1",
                    item_type=ConfirmationItemType.UNSUPPORTED_CLAIM,
                    priority=ConfirmationPriority.HIGH,
                    source_stage="test",
                    claim_text="test",
                    reason="test",
                    suggested_user_action="test",
                ),
            ],
            blocking_count=0,
            high_priority_count=1,
            pending_count=1,
            can_generate_final_pdf=True,
            summary="ok",
        )
        issues = validate_confirmation_packet_for_ui(packet)
        assert issues == []

    def test_empty_items_warns(self):
        packet = ConfirmationPacket(
            packet_id="empty",
            items=[],
            blocking_count=0,
            high_priority_count=0,
            pending_count=0,
            can_generate_final_pdf=True,
            summary="empty",
        )
        issues = validate_confirmation_packet_for_ui(packet)
        assert len(issues) > 0


class TestJsSafety:

    _JS_PATH = (
        Path(__file__).resolve().parent.parent
        / "src" / "resume_pdf_agent" / "confirmation_ui"
        / "static" / "confirmation_page.js"
    )

    def test_js_exists(self):
        assert self._JS_PATH.is_file()

    def test_js_no_network_calls(self):
        js = self._JS_PATH.read_text(encoding="utf-8")
        assert "fetch(" not in js
        assert "XMLHttpRequest" not in js
        assert "navigator.sendBeacon" not in js

    def test_js_no_eval(self):
        js = self._JS_PATH.read_text(encoding="utf-8")
        assert "eval(" not in js

    def test_js_no_import(self):
        js = self._JS_PATH.read_text(encoding="utf-8")
        assert "import(" not in js

    def test_js_no_external_urls(self):
        js = self._JS_PATH.read_text(encoding="utf-8")
        assert "https://" not in js
        assert "http://" not in js

    def test_js_contains_decision_generation(self):
        js = self._JS_PATH.read_text(encoding="utf-8")
        assert "generateDecisions" in js or "confirmation_decisions" in js


class TestCssSafety:

    _CSS_PATH = (
        Path(__file__).resolve().parent.parent
        / "src" / "resume_pdf_agent" / "confirmation_ui"
        / "static" / "confirmation_page.css"
    )

    def test_css_exists(self):
        assert self._CSS_PATH.is_file()

    def test_css_no_external_imports(self):
        css = self._CSS_PATH.read_text(encoding="utf-8")
        assert "@import url(" not in css


class TestHtmlSafety:

    def test_no_form_submission(self, tmp_path):
        """Rendered confirmation page must not submit forms to a server."""
        packet = ConfirmationPacket(
            packet_id="test",
            items=[
                ConfirmationItem(
                    item_id="i1",
                    item_type=ConfirmationItemType.UNSUPPORTED_CLAIM,
                    priority=ConfirmationPriority.HIGH,
                    source_stage="test",
                    claim_text="test",
                    reason="test",
                    suggested_user_action="test",
                ),
            ],
            blocking_count=0,
            high_priority_count=1,
            pending_count=1,
            can_generate_final_pdf=True,
            summary="ok",
        )
        out = tmp_path / "test.html"
        result = render_confirmation_ui_page(packet, out)
        assert "<form " not in result.html.lower() or "action=" not in result.html.lower()

    def test_no_react_vite_markers(self, tmp_path):
        packet = ConfirmationPacket(
            packet_id="test",
            items=[
                ConfirmationItem(
                    item_id="i1",
                    item_type=ConfirmationItemType.UNSUPPORTED_CLAIM,
                    priority=ConfirmationPriority.HIGH,
                    source_stage="test",
                    claim_text="test",
                    reason="test",
                    suggested_user_action="test",
                ),
            ],
            blocking_count=0,
            high_priority_count=1,
            pending_count=1,
            can_generate_final_pdf=True,
            summary="ok",
        )
        out = tmp_path / "test.html"
        result = render_confirmation_ui_page(packet, out)
        html = result.html.lower()
        assert "react" not in html
        assert "vite" not in html
        assert "__NEXT" not in html
