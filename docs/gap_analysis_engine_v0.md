# Gap Analysis Engine v0

## 它做什么

M4 Gap Analysis Engine v0 是一个 deterministic、rule-based 的诊断模块。它比较候选人的结构化信息和目标岗位 criteria，输出哪些 criteria 已被支持、哪些证据不足、哪些关键词缺失，以及哪些内容可能存在真实性风险。

M4 只做诊断，不生成最终简历内容。

## 输入

- `UserProfile`
- `ResumeContent`，可选
- `RoleCriteriaProfile`
- `ResumeTypeClassificationResult`，可选

## 输出

主要输出是 `GapAnalysisResult`，其中包含：

- `profile_id`
- `overall_match_level`
- `criteria_results`
- `strengths`
- `weaknesses`
- `missing_keywords`
- `truthfulness_warnings`

每个 `CriteriaMatchResult` 包含：

- `criterion_id`
- `match_level`
- `evidence_found`
- `missing_evidence`
- `suggested_actions`
- `risk_level`

## Gap Analysis 和 Resume Rewriting 的区别

Gap analysis 只指出证据和 criteria 之间的差距。例如，它可以建议用户补充 SQL 项目证据，或确认某个指标是否真实。

它不会改写 resume bullets，不会生成新的成就描述，也不会编造指标。Criteria-aware bullet enhancement 是后续 M6 的范围。

## 为什么 M4 是 deterministic 和 rule-based

当前阶段优先保证可测试、可解释和可控。M4 不调用 LLM，不使用 embeddings，也不做在线 JD 解析。所有 matching 都基于本地 schema、静态 criteria 和简单文本匹配规则。

## Evidence 如何提取

Evidence extraction 会从 `UserProfile` 和 `ResumeContent` 中提取可搜索文本：

- target roles 和 industries
- education、major、core courses、honors
- skill groups 和 skills
- awards 和 additional notes
- resume type、summary、experience titles/types
- tools、methods、outcomes、metrics、evidence notes
- section headings、bullet text、targeted criteria ids、risk flags

用户 full name 不会作为 matching evidence 使用。

## Criteria 如何匹配

Matcher 会对以下字段做 deterministic matching：

- criterion keywords
- evidence_required
- positive_signals
- extracted candidate evidence

Match levels 包括 `strong`、`medium`、`weak`、`missing` 和 `not_applicable`。

## Overall Match Level 如何计算

M4 使用 importance-weighted score：

- strong = 1.0
- medium = 0.65
- weak = 0.35
- missing = 0.0
- not_applicable = 0.5

再根据阈值映射到整体 `MatchLevel`。

## Missing Keywords 如何识别

如果 criterion 的重要 keywords 没有出现在候选人的 profile/resume evidence 中，就会进入 `missing_keywords`。结果会去重并保持 deterministic ordering。

## Truthfulness Warnings 如何浮现

M4 会读取 M1 safeguards：

- `EvidenceLevel.unsupported`
- `MetricStatus.unsupported`
- `needs_confirmation`
- `risk_flags`

这些会进入 `truthfulness_warnings`。M4 不是完整 truthfulness checker；M5 会做更系统的 unsupported-claim 检查。

## 不是 Hiring Probability Model

Gap analysis 不预测 hiring success、interview probability 或 offer probability。它只诊断当前结构化材料和 public role-fit criteria 的匹配情况。

## 不知道内部公司筛选规则

本项目不声称知道任何公司的内部简历筛选算法。M4 使用用户提供的信息、M2 静态 public role-fit criteria 和本地规则。

## 已知限制

- 关键词匹配较简单。
- 同义词和多语言支持有限。
- 不解析真实 JD。
- 不做真实 ATS/PDF parsing。
- 不生成 resume bullets。

## 未来改进

- Richer synonym dictionary。
- User-provided JD extraction。
- LLM-assisted explanation in a later milestone。
- More precise ATS parsing after HTML/PDF generation。
- Connection to M5 truthfulness checker。
- Connection to M6 bullet enhancement。
