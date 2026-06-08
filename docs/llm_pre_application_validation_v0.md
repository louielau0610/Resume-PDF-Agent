# LLM Pre-Application Validation v0

## 概述 / Overview

M26 严格预应用验证层是一个确定性验证器，用于检查 M24 LLM 候选应用计划项是否有资格进入未来的人工补丁预览阶段。

该验证器：
- 读取 M24 应用计划 JSON
- 可选交叉检查 M16 LLM 改写结果、M22 审阅决策、M23 决策摘要
- 对每个候选执行严格的安全检查
- 生成 JSON 和 Markdown 验证报告
- 不应用任何候选、不生成补丁、不修改最终简历

M26 provides a strict deterministic validation layer for M24 application plans. It checks whether planned items are eligible for a future manual patch-preview stage. It does NOT apply candidates, generate patches, or modify the final resume.

## CLI / 命令行

```
py -m resume_pdf_agent validate-llm-pre-application \
  --plan outputs/m25_llm_mock/llm_rewrite_application_plan.json \
  --result outputs/m25_llm_mock/llm_rewrite_result.json \
  --decisions outputs/m25_llm_mock/llm_rewrite_review_decisions.json \
  --summary outputs/m25_llm_mock/llm_rewrite_review_decision_summary.json \
  --output-json outputs/m26_validation/llm_rewrite_pre_application_validation.json \
  --output-md outputs/m26_validation/llm_rewrite_pre_application_validation.md \
  --strict
```

## 验证行为 / Validation Behavior

- `plan_only=True` 必须为 true
- 候选文本中的不安全声明指示符（如 "guaranteed"、"100%"）会被检测
- 需要确认的候选会被阻塞
- 缺少原文或候选文本的候选会被阻塞
- 缺少目标映射的候选会被阻塞
- 需要人工编辑的候选保持需要人工编辑
- 已拒绝/忽略/排除的候选保持排除
- 未映射的候选保持未映射
- 候选文本与原文相同会产生警告
- 过长或过短的候选文本会被标记

## 安全 / Safety

- 此验证器仅用于验证目的
- 未应用任何 LLM 候选
- 未生成任何补丁
- 最终简历未被修改
- 通过验证不意味着事实验证
- M5 真实性检查和 M14 确认门控仍然适用
- 不调用任何真实 LLM API
- 不预测招聘概率

## 限制 / Limitations

- 不安全声明检测是基于确定性关键词的，不能捕获所有语义问题
- 交叉检查仅在提供可选文件时执行
- 此验证器不防止未来的手动补丁错误

## 相关模块 / Related Modules

- `src/resume_pdf_agent/llm_pre_application_validation/` — M26 包
- `src/resume_pdf_agent/models/llm_pre_application_validation.py` — M26 数据模型
- `src/resume_pdf_agent/cli.py` — `validate-llm-pre-application` 命令
- `src/resume_pdf_agent/models/llm_application_plan.py` — M24 应用计划模型
