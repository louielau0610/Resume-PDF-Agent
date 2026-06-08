# LLM Human Final Edit Instruction Pack v0

## 概述 / Overview

M29 人工最终编辑指引包是一个确定性指引生成器，可从 M28 审批检查清单生成人工专用的最终编辑指引制品。该指引包仅用于人工操作 — 系统不会授予任何最终批准，不会应用任何候选，不会生成可执行补丁。

M29 provides a deterministic instruction generator that produces human-only final edit instruction artifacts from M28 approval checklists. It is instructions-only — no final approval is granted, no candidates are applied, and no executable patch is generated.

## CLI / 命令行

```
py -m resume_pdf_agent build-llm-human-final-edit-pack \
  --checklist outputs/m28_manual/llm_rewrite_manual_patch_approval_checklist.json \
  --output-json outputs/m29_pack/llm_rewrite_human_final_edit_instruction_pack.json \
  --output-md outputs/m29_pack/llm_rewrite_human_final_edit_instruction_pack.md \
  --output-html outputs/m29_pack/llm_rewrite_human_final_edit_instruction_pack.html
```

## 安全 / Safety

- 此指引包仅用于人工操作
- 未授予任何最终批准
- 未应用任何 LLM 候选
- 任何实际编辑必须由人类在系统外部手动完成

## 相关模块 / Related Modules

- `src/resume_pdf_agent/llm_human_final_edit_pack/` — M29 包
- `src/resume_pdf_agent/models/llm_human_final_edit_pack.py` — M29 数据模型
- `src/resume_pdf_agent/cli.py` — `build-llm-human-final-edit-pack` 命令
