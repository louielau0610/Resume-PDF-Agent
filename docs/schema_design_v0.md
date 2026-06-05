# Schema Design v0

## 为什么需要 schemas

`resume_pdf_agent` 的核心不是让模型自由生成一份简历，而是把用户信息、岗位标准、证据、风险和最终简历内容拆成可验证的数据结构。Schemas 可以让后续模块在清晰边界内工作，并让测试覆盖关键约束。

M1 的目标是先建立数据基础，不实现真实 gap analysis、LLM 改写、模板匹配或 PDF 生成。

## User Profile、Raw Experience、Resume Content 和 Screening Criteria 的区别

User Profile 表示用户的基础职业画像，例如姓名、联系方式、教育背景、目标岗位、技能、语言和奖项。

Raw Experience 是用户提供的经历事实来源，例如项目、实习、科研、课程、竞赛或志愿经历。它应该保留用户原始描述、工具、方法、结果和证据备注。

Resume Content 是未来渲染到简历里的结构化内容，包括经历、section 和 bullet。它必须记录 bullet 来自哪个经历、对应哪些 criteria、证据等级和指标状态。

Screening Criteria 表示公开、官方、用户提供或人工整理的岗位筛选信号，例如 Python 数据分析能力、SQL 熟悉度、统计推理、行动-结果清晰度、ATS 可读性和真实性风险。

## Criteria 来源原则

Screening criteria 必须来自公开、官方、用户提供或人工整理的来源，例如：

- Public job descriptions。
- Official company career pages。
- Official hiring guides。
- University career guides。
- User-provided JD text。
- Manually curated criteria knowledge base。

项目不得声称知道任何公司的内部简历筛选规则，也不得抓取机密或内部招聘标准。项目不得绕过登录墙、付费墙、反爬限制或 robots 限制。

高置信度 criteria 通常应来自 `official_company_page`、`official_hiring_guide`、`public_job_description`、`university_career_guide`、`user_provided_jd` 或 `manually_curated`。M1 暂不在代码里强制这个规则，后续 knowledge base 和审核流程会处理。

## EvidenceLevel 设计

`EvidenceLevel` 用来说明 bullet 或 claim 的证据强度：

- `user_provided`：用户明确提供了该信息。
- `reasonably_inferred`：可以从用户信息中合理推断，但仍需要谨慎。
- `needs_user_confirmation`：需要用户确认后才能用于最终简历。
- `unsupported`：当前没有证据支持，不应直接进入最终简历。

当 evidence level 是 `needs_user_confirmation` 或 `unsupported` 时，`needs_confirmation` 必须为 true。

## MetricStatus 设计

`MetricStatus` 用来防止系统发明数字：

- `user_provided`：指标由用户提供。
- `missing`：该经历可能适合补充指标，但用户还没有提供。
- `not_applicable`：该 bullet 不需要指标。
- `unsupported`：指标没有证据支持。

当 metric status 是 `unsupported` 时，`needs_confirmation` 必须为 true。系统不应自动补造百分比、金额、排名或效率提升。

## MatchLevel 设计

`MatchLevel` 用于未来 gap analysis：

- `strong`：用户证据强匹配 criteria。
- `medium`：部分匹配，但可以补充细节。
- `weak`：只有弱相关证据。
- `missing`：缺少相关证据。
- `not_applicable`：该 criteria 对当前场景不适用。

M1 只定义数据结构，不实现匹配逻辑。

## RiskLevel 设计

`RiskLevel` 用于表达真实性或表达质量风险：

- `low`：风险较低。
- `medium`：需要检查或补充证据。
- `high`：不建议直接用于最终简历。

后续 truthfulness checker 会结合 `EvidenceLevel`、`MetricStatus`、`risk_flags` 和用户证据生成风险提示。

## 未来模块如何使用这些 schemas

- Static criteria knowledge base 会输出 `RoleCriteriaProfile`。
- Resume type classifier 会输出 `ResumeType`。
- Gap analysis engine 会读取 `UserProfile`、`ResumeContent` 和 `RoleCriteriaProfile`，输出 `GapAnalysisResult`。
- Truthfulness checker 会标记 unsupported claims、invented metrics 和 unclear evidence。
- Bullet enhancement engine 会生成或修改 `ResumeBullet`，但必须保留 evidence metadata。
- Renderer 会读取经过检查的 `ResumeContent`，再进入 HTML 和 PDF 渲染。

## 如何防止简历幻觉和 unsupported achievements

M1 schema 通过以下字段让风险可见：

- `EvidenceLevel`：说明 claim 的证据来源强度。
- `MetricStatus`：说明指标是否由用户提供。
- `needs_confirmation`：强制标记需要用户确认的内容。
- `risk_flags`：记录具体风险，例如 unsupported_metric、unclear_scope、exaggerated_leadership。

这些字段不会自动保证内容真实，但会让后续模块不能轻易把不确定内容伪装成确定事实。任何 unsupported claim 都必须在数据结构中显式可见，并在最终输出前被确认、删除或降级。
