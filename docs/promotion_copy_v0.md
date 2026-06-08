# Promotion Copy v0

## GitHub Short Description

Safety-first resume PDF generator with local LLM rewrite candidate review, plan/preview/validation artifacts, and human-only final edit instructions.

## English GitHub Description

`resume_pdf_agent` is a local Python workflow that generates resume HTML/PDF artifacts and demonstrates a safe human-in-the-loop LLM candidate review chain without automatic resume mutation.

## Chinese Launch Post

我发布了 `resume_pdf_agent` v0.1.0：一个安全优先、人工审阅驱动的简历 PDF 生成与 LLM 改写候选审阅工具。

它可以从结构化资料生成 `resume.html` / `resume.pdf`，也可以用 mock LLM workflow 生成改写候选、本地审阅页面、决策汇总、应用计划、预览、验证、人工补丁预览、审批清单和最终人工编辑指引。

核心边界很明确：系统不会自动应用 LLM 候选，不会生成可执行 patch，不会授予最终批准，也不会修改最终简历。所有候选改写都必须由人类审阅并在系统外手动决定。

## English Launch Post

I released `resume_pdf_agent` v0.1.0: a safety-first resume PDF generator with a local human-in-the-loop LLM rewrite candidate review chain.

It generates structured resume HTML/PDF artifacts and demonstrates local review pages, decision summaries, application plans, preview UI, strict validation, manual patch previews, approval checklists, and final human edit instructions.

The key boundary is deliberate: LLM candidates are never automatically applied, executable patches are not generated, and the system never grants final approval.

## Resume Bullet

Built `resume_pdf_agent`, a Python resume PDF generation and safe LLM candidate review workflow with 1,000+ tests, local static review UIs, deterministic validation artifacts, and strict no-auto-apply safety boundaries.

## LinkedIn-Style Project Summary

`resume_pdf_agent` is a portfolio project focused on safe AI workflow design. It combines deterministic resume PDF generation with a human-reviewed LLM candidate pipeline, producing transparent artifacts for review, planning, validation, manual preview, checklist review, and final edit instructions. The project is intentionally scoped so AI suggestions never mutate the final resume automatically.

## GitHub Topics Suggestions

- python
- resume
- pdf
- jinja2
- typer
- pydantic
- ats
- human-in-the-loop
- ai-safety
- llm-workflow
- static-html
- portfolio-project
