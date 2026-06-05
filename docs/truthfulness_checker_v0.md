# Truthfulness Checker v0

## 它做什么

M5 Truthfulness and Unsupported-claim Checker v0 是一个 deterministic、rule-based 的安全诊断模块。它分析 `ResumeContent` 和可选 `GapAnalysisResult`，找出 unsupported claim、unsupported metric、需要用户确认的 bullet 和其他真实性风险。

## 为什么需要 Truthfulness Checking

简历生成系统必须避免编造经历、夸大成果、发明指标或暗示用户没有实际做过的工具和方法。Truthfulness checker 在内容增强和 PDF 生成之前提供安全闸门。

## 输入

- `ResumeContent`
- `GapAnalysisResult`，可选

## 输出

- `TruthfulnessCheckResult`
- `TruthfulnessIssue`
- `ResumeClaim`

## Truthfulness Checking 和 Resume Rewriting 的区别

M5 只诊断风险，不改写 resume bullets，不生成新的成就描述，也不补造指标。后续 M6 才会处理 criteria-aware bullet enhancement，并且必须遵守 M5 的安全结果。

## Unsupported Evidence 如何检测

如果 `ResumeBullet.evidence_level == unsupported`，M5 会生成 high severity 的 `unsupported_evidence` issue，并要求用户删除、确认或提供证据。

## Unsupported Metrics 如何检测

如果 `ResumeBullet.metric_status == unsupported`，M5 会生成 high severity 的 `unsupported_metric` issue，并要求用户移除指标或提供可验证来源。

## Needs Confirmation 如何处理

如果 `needs_confirmation = true`，M5 会生成 medium severity 的 `needs_confirmation` issue，提醒在最终简历生成前必须由用户确认。

## Risk Flags 如何浮现

非空 `risk_flags` 会转换为 `risk_flag` issues。每个 risk flag 都会保留在 issue reason 和 suggested action 中。

## Quantified Claims 如何检查

M5 会检测包含百分比、数字和强 impact wording 的 claim，例如 increased、reduced、improved、saved、generated、accuracy、runtime 等。如果没有 user-provided metric evidence，会生成 unverifiable quantified claim 或 metric without source issue。

M5 不会自动删除 claim，也不会发明指标。

## Leadership Exaggeration Risk 如何保守检测

如果 bullet 使用 led、owned、managed、spearheaded、architected 等强 ownership wording，但 source experience 只显示 assisted、supported、contributed、participated、helped 或 team project 等弱贡献信号，M5 会生成 leadership exaggeration risk。

如果 source experience 本身支持 leadership wording，则不会自动标记。

## Checker 不能独立验证现实世界真伪

M5 只能根据结构化输入和 metadata 判断风险。它不能访问现实世界证据，也不能证明用户是否真的完成了某件事。

## 不预测 Hiring Success

M5 不预测 hiring success、interview probability 或 offer probability。

## 不知道内部公司筛选标准

本项目不声称知道任何公司的内部简历筛选算法。M5 只检查用户内容中的真实性和证据风险。

## 已知限制

- 规则较保守，可能漏掉复杂夸大表达。
- Tool/method 检查只覆盖一小组常见术语。
- 不能独立验证外部事实。
- 不做语义级重写。

## 未来改进

- User confirmation workflow。
- Richer metric provenance tracking。
- LLM-assisted claim explanation in a later milestone。
- Integration with M6 bullet enhancement。
- Final pre-PDF safety gate。
