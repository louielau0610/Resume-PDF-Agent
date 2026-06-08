# LLM Manual Patch Preview v0

## 概述 / Overview

M27 人工补丁预览是一个确定性预览生成器，可从 M24 应用计划和 M26 预应用验证报告生成人工可读的补丁预览制品。该预览仅用于人工查看和比较 — 不会生成可执行补丁，不会应用任何候选，不会修改最终简历。

M27 provides a deterministic preview generator that creates human-readable patch preview artifacts from M24 application plans and M26 pre-application validation reports. It is preview-only — no executable patch is generated, no candidates are applied, and the final resume is not modified.

## CLI / 命令行

```
py -m resume_pdf_agent preview-llm-manual-patch \
  --plan outputs/m26_1_manual/llm_rewrite_application_plan.json \
  --validation outputs/m26_1_manual/llm_rewrite_pre_application_validation.json \
  --output-json outputs/m27_preview/llm_rewrite_manual_patch_preview.json \
  --output-md outputs/m27_preview/llm_rewrite_manual_patch_preview.md \
  --output-html outputs/m27_preview/llm_rewrite_manual_patch_preview.html
```

## 安全 / Safety

- 此预览仅用于人工查看
- 未生成可执行补丁
- 未应用任何 LLM 候选
- 最终简历未被修改
- M5 真实性检查和 M14 确认门控仍然适用
- 不预测招聘概率
- 不调用真实 LLM API

## 限制 / Limitations

- 仅 M26 验证通过的候选可进入预览就绪状态
- 差异预览基于 Python difflib，为显示专用
- HTML 预览为纯静态本地页面，无网络请求
- 不包含"应用"、"更新简历"、"执行补丁"等控件

## 相关模块 / Related Modules

- `src/resume_pdf_agent/llm_manual_patch_preview/` — M27 包
- `src/resume_pdf_agent/models/llm_manual_patch_preview.py` — M27 数据模型
- `src/resume_pdf_agent/cli.py` — `preview-llm-manual-patch` 命令
