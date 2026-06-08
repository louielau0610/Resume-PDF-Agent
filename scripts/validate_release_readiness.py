"""Release-readiness validation helper for M13.

Checks that required docs, sample inputs, and package modules exist.
Does NOT run pytest or require network access.
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent

_REQUIRED_DOCS: list[str] = [
    "docs/demo_walkthrough_v0.md",
    "docs/architecture_diagram_v0.md",
    "docs/github_project_overview_v0.md",
    "docs/release_checklist_v0.md",
    "docs/limitations_and_roadmap_v0.md",
    "docs/commercial_product_roadmap_v0.md",
    "docs/user_confirmation_workflow_v0.md",
    "docs/user_provided_jd_parser_v0.md",
    "docs/llm_assisted_rewriting_v0.md",
    "docs/production_pdf_backend_setup_v0.md",
    "docs/visual_regression_testing_v0.md",
    "docs/optional_api_layer_v0.md",
    "docs/browser_confirmation_ui_v0.md",
    "docs/browser_jd_upload_ui_v0.md",
    "docs/browser_llm_rewrite_review_ui_v0.md",
    "docs/llm_pre_application_validation_v0.md",
    "examples/README.md",
    "examples/sample_data_science_demo.md",
    "examples/demo_output_manifest_v0.md",
]

_REQUIRED_SCRIPTS: list[str] = [
    "scripts/run_demo_workflow.py",
    "scripts/validate_release_readiness.py",
]

_REQUIRED_READMES: list[str] = [
    "README.md",
    "README.en.md",
]

_REQUIRED_SAMPLE_INPUT: str = (
    "data/sample_inputs/sample_data_science_user.json"
)

_EXPECTED_CORE_PACKAGES: list[str] = [
    "criteria",
    "classifier",
    "gap_analysis",
    "truthfulness",
    "confirmation",
    "enhancement",
    "llm",
    "jd",
    "templates",
    "rendering",
    "pdf",
    "workflow",
    "frontend",
    "api",
    "confirmation_ui",
    "jd_ui",
    "llm_review_ui",
    "llm_review_decisions",
    "llm_application_plan",
    "llm_application_preview_ui",
    "llm_pre_application_validation",
    "llm_manual_patch_preview",
    "llm_manual_approval_checklist",
    "visual_regression",
]

_REQUIRED_SCRIPTS: list[str] = [
    "scripts/run_demo_workflow.py",
    "scripts/validate_release_readiness.py",
    "scripts/run_visual_regression_checks.py",
    "scripts/verify_pdf_backend.py",
    "scripts/run_api_dev_server.py",
]

_REQUIRED_DOCS: list[str] = [
    "docs/demo_walkthrough_v0.md",
    "docs/architecture_diagram_v0.md",
    "docs/github_project_overview_v0.md",
    "docs/release_checklist_v0.md",
    "docs/limitations_and_roadmap_v0.md",
    "docs/commercial_product_roadmap_v0.md",
    "docs/llm_review_decision_summary_v0.md",
    "docs/llm_candidate_application_planning_v0.md",
    "docs/browser_llm_application_preview_ui_v0.md",
    "examples/README.md",
    "examples/sample_data_science_demo.md",
    "examples/demo_output_manifest_v0.md",
]


def _check_file(rel_path: str, label: str) -> bool:
    path = _REPO_ROOT / rel_path
    ok = path.is_file()
    status = "OK" if ok else "MISSING"
    print(f"  [{status}] {label}: {rel_path}")
    return ok


def _check_package(pkg_name: str) -> bool:
    """Check that a sub-package exists under src/resume_pdf_agent/."""
    pkg_path = _REPO_ROOT / "src" / "resume_pdf_agent" / pkg_name
    ok = pkg_path.is_dir() and (pkg_path / "__init__.py").is_file()
    status = "OK" if ok else "MISSING"
    print(f"  [{status}] Package: {pkg_name}")
    return ok


def _check_readme_content(path: str, must_contain: list[str], must_not_contain: list[str]) -> list[str]:
    """Check a README for required and forbidden phrases."""
    full_path = _REPO_ROOT / path
    issues: list[str] = []
    if not full_path.is_file():
        issues.append(f"{path} not found")
        return issues

    text = full_path.read_text(encoding="utf-8").lower()

    for phrase in must_contain:
        if phrase.lower() not in text:
            issues.append(f"{path}: missing required phrase '{phrase}'")

    for phrase in must_not_contain:
        if phrase.lower() in text:
            issues.append(f"{path}: contains forbidden phrase '{phrase}'")

    return issues


def _check_cli_command(command_name: str) -> bool:
    try:
        from resume_pdf_agent.cli import app

        commands = {cmd.name for cmd in app.registered_commands}
        ok = command_name in commands
    except Exception as exc:
        print(f"  [FAIL] CLI command check crashed: {exc}")
        return False
    status = "OK" if ok else "MISSING"
    print(f"  [{status}] CLI command: {command_name}")
    return ok


def _check_export_format_pdf_only() -> bool:
    try:
        from resume_pdf_agent.models.enums import ExportFormat

        values = [item.value for item in ExportFormat]
    except Exception as exc:
        print(f"  [FAIL] ExportFormat check crashed: {exc}")
        return False
    ok = values == ["pdf"]
    status = "OK" if ok else "FAIL"
    print(f"  [{status}] ExportFormat values: {values}")
    return ok


def _check_no_forbidden_core_dependencies() -> bool:
    pyproject = _REPO_ROOT / "pyproject.toml"
    if not pyproject.is_file():
        print("  [FAIL] pyproject.toml not found")
        return False
    text = pyproject.read_text(encoding="utf-8").lower()
    core_section = text.split("[project.optional-dependencies]")[0]
    forbidden = [
        "fastapi",
        "flask",
        "react",
        "vite",
        "next",
        "vue",
        "svelte",
        "streamlit",
        "openai",
        "anthropic",
        "google-generativeai",
    ]
    found = [dep for dep in forbidden if dep in core_section]
    if found:
        print(f"  [FAIL] Forbidden core dependencies found: {', '.join(found)}")
        return False
    print("  [OK] No forbidden core frontend/server/LLM dependencies found.")
    return True


def main() -> int:
    print("Release Readiness Check")
    print("=" * 60)

    all_ok = True

    # --- 1. Docs --------------------------------------------------------
    print("\n[1] Required docs:")
    for rel in _REQUIRED_DOCS:
        if not _check_file(rel, "Doc"):
            all_ok = False

    # --- 2. Scripts -----------------------------------------------------
    print("\n[2] Required scripts:")
    for rel in _REQUIRED_SCRIPTS:
        if not _check_file(rel, "Script"):
            all_ok = False

    # --- 3. READMEs -----------------------------------------------------
    print("\n[3] README files:")
    for rel in _REQUIRED_READMES:
        if not _check_file(rel, "README"):
            all_ok = False

    # --- 4. Sample input ------------------------------------------------
    print("\n[4] Sample input:")
    if not _check_file(_REQUIRED_SAMPLE_INPUT, "Sample"):
        all_ok = False

    # --- 5. Core packages -----------------------------------------------
    print("\n[5] Core packages:")
    for pkg in _EXPECTED_CORE_PACKAGES:
        if not _check_package(pkg):
            all_ok = False

    # --- 6. README content checks ---------------------------------------
    print("\n[6] README content checks:")
    readme_issues: list[str] = []

    # Must contain
    readme_issues.extend(
        _check_readme_content(
            "README.md",
            must_contain=["criteria", "pdf", "resume"],
            must_not_contain=[],
        )
    )

    # Must NOT contain
    readme_issues.extend(
        _check_readme_content(
            "README.md",
            must_contain=[],
            must_not_contain=[
                "internal screening",
                "hiring probability",
                "offer probability",
                "interview probability",
            ],
        )
    )

    if readme_issues:
        for issue in readme_issues:
            print(f"  [FAIL] {issue}")
        all_ok = False
    else:
        print("  [OK] README content checks passed.")

    # --- 7. Architecture doc Mermaid check ------------------------------
    print("\n[7] Architecture doc Mermaid check:")
    arch_path = _REPO_ROOT / "docs/architecture_diagram_v0.md"
    if arch_path.is_file():
        content = arch_path.read_text(encoding="utf-8")
        if "```mermaid" in content:
            print("  [OK] Mermaid code blocks found.")
        else:
            print("  [FAIL] No Mermaid code blocks found in architecture doc.")
            all_ok = False
    else:
        print("  [FAIL] Architecture doc not found.")
        all_ok = False

    # --- 8. No generated output requirement -----------------------------
    print("\n[8] CLI command checks:")
    if not _check_cli_command("summarize-llm-review-decisions"):
        all_ok = False
    if not _check_cli_command("plan-llm-candidate-application"):
        all_ok = False
    if not _check_cli_command("render-llm-application-preview-ui"):
        all_ok = False

    # --- 9. Safety boundary checks --------------------------------------
    print("\n[9] Safety boundary checks:")
    if not _check_export_format_pdf_only():
        all_ok = False
    if not _check_no_forbidden_core_dependencies():
        all_ok = False

    # --- 10. No generated output requirement ----------------------------
    print("\n[10] Generated output directory check:")
    outputs_dir = _REPO_ROOT / "outputs"
    if outputs_dir.is_dir():
        contents = list(outputs_dir.iterdir())
        if contents:
            print(f"  [INFO] outputs/ contains {len(contents)} item(s) - not required for release.")
        else:
            print("  [OK] outputs/ is empty (not required for release).")
    else:
        print("  [OK] outputs/ does not exist (not required for release).")

    # --- Summary --------------------------------------------------------
    print("\n" + "=" * 60)
    if all_ok:
        print("RESULT: All release-readiness checks PASSED.")
        return 0
    else:
        print("RESULT: Some checks FAILED. See details above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
