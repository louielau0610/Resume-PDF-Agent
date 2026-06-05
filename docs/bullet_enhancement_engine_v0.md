# Bullet Enhancement Engine v0

## 它做什么

M6 Bullet Enhancement Engine v0 根据已有用户证据生成 criteria-aware bullet candidates。它不是最终简历渲染器，也不是 LLM 改写器。

## 输入

- `ResumeContent`
- `RoleCriteriaProfile`，可选
- `GapAnalysisResult`，可选
- `TruthfulnessCheckResult`，可选

## 输出

- `BulletEnhancementResult`
- `ExperienceEnhancementResult`
- `EnhancedBulletCandidate`

## 和最终 Resume Rendering 的区别

M6 只生成候选 bullet。最终 section 顺序、版式、HTML/PDF 渲染和模板匹配属于后续 milestones。

## 为什么 M6 是 deterministic 和 rule-based

当前阶段优先保证安全、可测试和可追踪。M6 不调用 LLM，不解析真实 JD，也不生成最终简历内容。

## Criteria 如何指导生成

如果传入 criteria profile 或 gap analysis result，M6 会把相关 criterion IDs 写入 candidate，帮助后续模块知道 bullet 试图覆盖哪些 role-fit signals。

## Truthfulness Safeguards 如何使用

M6 会读取 M5 truthfulness result。如果 source experience 有 high-risk issue，会跳过或阻止 unsafe enhancement。M6 不会把 unsupported claim 润色成看起来更可信的 bullet。

## Metrics 规则

指标只能在 source `Metric` 有明确 value 且有 source_note 或 context 时使用。M6 不会发明百分比、排名、用户数、收入或效率提升。

## 不预测 Hiring Success

M6 不预测 hiring success、interview probability 或 offer probability。

## 不知道内部公司筛选规则

本项目不声称知道任何公司的内部简历筛选算法。M6 只使用用户提供的结构化内容和公开 role-fit criteria。

## 已知限制

- 生成规则保守，表达变化有限。
- 不做语义级风格优化。
- 不独立验证现实世界真伪。
- 不生成最终 verified resume bullets。

## 未来改进

- User confirmation workflow。
- Optional LLM-assisted rewrites after safeguards。
- Tone/style variants。
- Role-specific bullet templates。
- Integration with template matching。
- Integration with HTML/PDF rendering。
