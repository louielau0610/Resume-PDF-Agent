# Project Status

## M30 Release Consolidation / Scope Freeze

M30 completes the release landing pack for v0.1.0. This milestone does not add runtime features, checklist layers, LLM modules, patch generation, or resume mutation behavior. It consolidates release documentation, README positioning, demo instructions, validation reporting, launch notes, and promotion copy.

## Current Release Candidate

- Release candidate: v0.1.0
- Current baseline before M30 validation: `1023 passed, 2 skipped`
- Current completed scope: M0-M29, with M30 documentation/release consolidation in progress
- README.md remains Chinese-first
- README.en.md remains English
- ExportFormat remains `['pdf']`

## Completed Milestones

- M0-M13: project foundation, schemas, deterministic workflow, rendering, PDF generation, frontend dashboard, docs/demo packaging
- M14: user confirmation workflow
- M15: user-provided JD parser with compliance checks
- M16/M16.1: optional mock LLM-assisted rewrite candidates and validation
- M17-M18.1: PDF backend verification and visual regression support
- M19/M19.1: optional API layer and docs
- M20-M21.1: browser confirmation UI and JD upload UI
- M22/M22.1: browser LLM rewrite review UI and autoescape hardening
- M23: LLM review decision loader and advisory summary
- M24: candidate application planning layer
- M25: manual candidate application preview UI
- M26/M26.1: strict pre-application validation and verification
- M27/M27.1: manual patch preview without resume mutation and strict validation
- M28: manual patch approval checklist
- M29: human-only final edit instruction pack
- M30: release consolidation, landing pack, and scope freeze

## Safety Boundaries

- LLM candidates are never automatically applied.
- Final resume artifacts are not modified by the LLM candidate chain.
- No executable patch files are generated.
- No final approval is granted by the system.
- Human review is required for every LLM-derived edit.
- Real LLM provider integration is not required for the mock workflow.
- Export remains PDF-only.
- No DOCX/JPG/PNG export is implemented.
- No more checklist layers are planned before v0.1.0.

## Release Freeze

No further feature milestones are planned before v0.1.0. Future work should be decided from real user feedback, not additional speculative checklist layers.
