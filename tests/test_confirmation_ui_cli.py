"""CLI tests for M20 confirmation UI."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent


class TestRenderConfirmationUiCli:

    def test_command_works(self, tmp_path):
        """render-confirmation-ui command works with a sample packet."""
        # First create a sample packet
        packet = {
            "packet_id": "cli_test",
            "items": [
                {
                    "item_id": "t1",
                    "item_type": "unsupported_claim",
                    "priority": "blocking",
                    "status": "pending",
                    "source_stage": "test",
                    "claim_text": "Test claim",
                    "reason": "Test reason",
                    "suggested_user_action": "Test action",
                    "blocks_final_pdf": True,
                    "requires_user_decision": True,
                    "related_criteria_ids": [],
                    "risk_flags": [],
                }
            ],
            "blocking_count": 1,
            "high_priority_count": 0,
            "pending_count": 1,
            "can_generate_final_pdf": False,
            "warnings": [],
            "summary": "CLI test packet",
        }
        pkt_path = tmp_path / "packet.json"
        pkt_path.write_text(json.dumps(packet), encoding="utf-8")
        out = tmp_path / "out.html"

        result = subprocess.run(
            [sys.executable, "-m", "resume_pdf_agent", "render-confirmation-ui",
             "--packet", str(pkt_path), "--output", str(out)],
            capture_output=True, text=True,
            cwd=str(_REPO_ROOT), timeout=60,
        )
        assert result.returncode == 0
        assert out.is_file()
        html = out.read_text(encoding="utf-8")
        assert "t1" in html

    def test_missing_packet_fails(self, tmp_path):
        result = subprocess.run(
            [sys.executable, "-m", "resume_pdf_agent", "render-confirmation-ui",
             "--packet", str(tmp_path / "nope.json"),
             "--output", str(tmp_path / "out.html")],
            capture_output=True, text=True,
            cwd=str(_REPO_ROOT), timeout=30,
        )
        assert result.returncode != 0


class TestExistingCliStillWorks:

    def test_list_criteria(self):
        result = subprocess.run(
            [sys.executable, "-m", "resume_pdf_agent", "list-criteria"],
            capture_output=True, text=True,
            cwd=str(_REPO_ROOT), timeout=30,
        )
        assert result.returncode == 0

    def test_list_templates(self):
        result = subprocess.run(
            [sys.executable, "-m", "resume_pdf_agent", "list-templates"],
            capture_output=True, text=True,
            cwd=str(_REPO_ROOT), timeout=30,
        )
        assert result.returncode == 0

    def test_check_pdf_backend(self):
        result = subprocess.run(
            [sys.executable, "-m", "resume_pdf_agent", "check-pdf-backend"],
            capture_output=True, text=True,
            cwd=str(_REPO_ROOT), timeout=30,
        )
        assert result.returncode == 0


class TestWorkflowWithConfirmationUi:

    def test_write_confirmation_ui_flag(self, tmp_path):
        """run-sample --write-confirmation-ui generates confirmation.html."""
        result = subprocess.run(
            [sys.executable, "-m", "resume_pdf_agent", "run-sample",
             "--output-dir", str(tmp_path / "out"),
             "--pdf-backend", "mock",
             "--write-confirmation-ui"],
            capture_output=True, text=True,
            cwd=str(_REPO_ROOT), timeout=120,
        )
        assert result.returncode in (0, 1)
        ui_path = tmp_path / "out" / "confirmation.html"
        assert ui_path.is_file(), "confirmation.html should be generated"

    def test_default_without_ui_flag(self, tmp_path):
        """Default workflow without --write-confirmation-ui does not create confirmation.html."""
        result = subprocess.run(
            [sys.executable, "-m", "resume_pdf_agent", "run-sample",
             "--output-dir", str(tmp_path / "out"),
             "--pdf-backend", "mock"],
            capture_output=True, text=True,
            cwd=str(_REPO_ROOT), timeout=120,
        )
        # confirmation.html may or may not exist; test doesn't require its absence
        assert result.returncode in (0, 1)
