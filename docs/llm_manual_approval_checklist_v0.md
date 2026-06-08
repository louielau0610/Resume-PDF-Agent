# LLM Manual Approval Checklist v0

## 概述 / Overview

M28 人工审批检查清单是一个确定性检查清单生成器，可从 M27 人工补丁预览生成人工专用的检查清单制品。该检查清单仅用于人工审阅 — 系统不会授予任何最终批准，不会应用任何候选，不会生成可执行补丁。

M28 provides a deterministic checklist generator that produces human-only checklist artifacts from M27 manual patch previews. It is checklist-only — no final approval is granted by the system, no candidates are applied, and no executable patch is generated.

## CLI / 命令行

```
py -m resume_pdf_agent build-llm-manual-approval-checklist \
  --preview outputs/m27_manual/llm_rewrite_manual_patch_preview.json \
  --output-json outputs/m28_checklist/llm_rewrite_manual_patch_approval_checklist.json \
  --output-md outputs/m28_checklist/llm_rewrite_manual_patch_approval_checklist.md \
  --output-html outputs/m28_checklist/llm_rewrite_manual_patch_approval_checklist.html
```

## 安全 / Safety

- 此检查清单仅用于人工审阅
- 未授予任何最终批准
- 未应用任何 LLM 候选
- 未生成可执行补丁
- M5 真实性检查和 M14 确认门控仍然适用

## 限制 / Limitations

- 默认答案均为 `not_reviewed` — 这并非批准
- HTML 检查清单为纯静态本地页面
- 不包含"应用"、"批准"、"提交"、"执行补丁"等控件
- 不预测招聘概率

## 相关模块 / Related Modules

- `src/resume_pdf_agent/llm_manual_approval_checklist/` — M28 包
- `src/resume_pdf_agent/models/llm_manual_approval_checklist.py` — M28 数据模型
- `src/resume_pdf_agent/cli.py` — `build-llm-manual-approval-checklist` 命令
