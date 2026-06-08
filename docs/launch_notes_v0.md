# Launch Notes v0

## What This Project Does

`resume_pdf_agent` generates structured resume HTML/PDF artifacts from local sample or user-provided JSON data. It also includes a fully local LLM candidate review chain for mock rewrite suggestions: review UI, decision summary, application plan, preview UI, strict validation, manual patch preview, manual approval checklist, and human final edit instructions.

## What It Intentionally Does Not Do

- It does not automatically apply LLM rewrite candidates.
- It does not mutate final resume artifacts from LLM candidate artifacts.
- It does not generate executable patches.
- It does not grant final approval.
- It does not call a real LLM API in the mock workflow.
- It does not export DOCX/JPG/PNG.
- It does not predict recruiting outcomes.
- It does not claim access to internal screening systems.

## Who It Is For

- Developers demonstrating safe AI workflow design.
- Students or early-career candidates who want a transparent resume artifact pipeline.
- Reviewers evaluating human-in-the-loop AI product boundaries.
- Open-source readers interested in deterministic, test-heavy Python workflows.

## How To Run It

Quick start:

```bash
py -m resume_pdf_agent run-sample --output-dir outputs/quickstart --pdf-backend mock --write-frontend-page
```

Full release demo:

```bash
py scripts/run_demo_workflow.py --output-dir outputs/release_demo --pdf-backend mock --include-llm-mock --write-llm-review-ui --write-llm-review-decision-summary --write-llm-application-plan --write-llm-application-preview-ui --write-llm-pre-application-validation --write-llm-manual-patch-preview --write-llm-manual-approval-checklist --write-llm-human-final-edit-pack
```

## Current Limitations

- The release demo uses mock LLM candidates.
- The default PDF backend can be mock for deterministic validation.
- The LLM candidate chain produces manual review artifacts only.
- Browser pages are local static pages, not hosted product surfaces.
- Real user feedback is still needed before deciding the next product iteration.

## Next Step

Launch v0.1.0 publicly, collect first user feedback, and decide the next iteration from actual usage.
