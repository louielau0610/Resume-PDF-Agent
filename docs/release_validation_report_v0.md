# Release Validation Report v0

## Commit

- Baseline commit validated before M30 docs commit: `75ce4ff` (`M29 add human final edit instruction pack`)
- Branch: `main`

## Validation Commands

### Git Status

```text
git status: working tree contained only M30 release documentation / release-readiness changes before commit.
git branch --show-current: main
git log --oneline -8:
75ce4ff M29 add human final edit instruction pack
5cfef98 M28 add manual approval checklist artifacts
d035fdb M27.1 strict validation report
cdd0a6d M27 add manual patch preview artifacts
f2f6cf0 M26.1 verify pre-application validation workflow
cc2db9c M26 add strict pre-application validation
13d2ade M25 add LLM application preview UI
a399296 M24 add LLM candidate application planning
```

### Syntax

Command:

```bash
py -m compileall src tests scripts
```

Result: passed.

### Full Test Suite

Command:

```bash
py -m pytest -q
```

Result:

```text
1023 passed, 2 skipped in 66.66s (0:01:06)
```

### Release Readiness

Command:

```bash
py scripts/validate_release_readiness.py
```

Result:

```text
RESULT: All release-readiness checks PASSED.
```

The release readiness check confirmed required docs, scripts, README files, sample input, expected packages, CLI commands, `ExportFormat == ['pdf']`, and no forbidden core frontend/server/LLM dependencies.

### Full Release Demo

Command:

```bash
py scripts/run_demo_workflow.py --output-dir outputs/release_demo --pdf-backend mock --include-llm-mock --write-llm-review-ui --write-llm-review-decision-summary --write-llm-application-plan --write-llm-application-preview-ui --write-llm-pre-application-validation --write-llm-manual-patch-preview --write-llm-manual-approval-checklist --write-llm-human-final-edit-pack
```

Result:

```text
Status: completed_with_warnings
Warnings: 8
Errors: 0
M26 passed/blocked: 0/3
M27 ready/blocked: 0/3
M28 review/blocked: 0/3
M29 ready/blocked: 0/3
[OK] Key output artifacts present.
```

The warnings are expected sample-data safety/confirmation warnings.

## Artifact Checks

Confirmed non-empty:

- `outputs/release_demo/resume.html` (4977 bytes)
- `outputs/release_demo/resume.pdf` (406 bytes)
- `outputs/release_demo/index.html` (29551 bytes)
- `outputs/release_demo/llm_rewrite_result.json` (6123 bytes)
- `outputs/release_demo/llm_review.html` (36860 bytes)
- `outputs/release_demo/llm_rewrite_review_decision_summary.json` (2982 bytes)
- `outputs/release_demo/llm_rewrite_application_plan.json` (8968 bytes)
- `outputs/release_demo/llm_rewrite_application_preview.html` (42339 bytes)
- `outputs/release_demo/llm_rewrite_pre_application_validation.json` (7573 bytes)
- `outputs/release_demo/llm_rewrite_manual_patch_preview.json` (9582 bytes)
- `outputs/release_demo/llm_rewrite_manual_patch_approval_checklist.json` (14368 bytes)
- `outputs/release_demo/llm_rewrite_human_final_edit_instruction_pack.json` (14453 bytes)

## Safety Boundary Checks

- `resume.pdf` starts with `%PDF`: passed.
- `ExportFormat` is exactly `['pdf']`: passed.
- No `.patch` files under `outputs/release_demo`: passed.
- No `.diff` files under `outputs/release_demo`: passed.
- Final resume not modified by LLM candidate workflow:
  - baseline `resume.html` SHA256: `ab825686f7851c1911fe861a52ca00f8043f7bd6d18a5c422d18ca3c695ab326`
  - release demo `resume.html` SHA256: `ab825686f7851c1911fe861a52ca00f8043f7bd6d18a5c422d18ca3c695ab326`
  - unchanged: `True`
- `applied_candidates` does not appear in `outputs/release_demo/*.json`: passed.
- `patch_operations` does not appear in `outputs/release_demo/*.json`: passed.
- `final_resume_modified=False` in safety artifacts where present: passed.
- `executable_patch_generated=False` in M27/M28/M29 artifacts where present: passed.

## Scope Freeze

M30 adds release documentation and landing-pack consolidation only. No runtime modules, checklist layers, candidate application, executable patch generation, new export formats, real LLM provider integration, or resume content mutation behavior were added.
