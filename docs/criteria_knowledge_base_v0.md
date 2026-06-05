# Criteria Knowledge Base v0

## 它是什么

Static Criteria Knowledge Base v0 是 `resume_pdf_agent` 在 M2 阶段新增的本地静态岗位 criteria 知识库。它由一组 JSON 文件组成，每个文件都会验证为 M1 中定义的 `RoleCriteriaProfile`。

这些 profile 的作用是把常见学生和早期职业岗位的公开 role-fit indicators 表示成结构化 criteria，供后续模块复用。

## 为什么需要它

项目后续需要根据目标岗位判断简历是否覆盖关键能力、证据是否充分、表述是否清晰、指标是否真实。直接让 LLM 自由判断会难以测试，也容易引入不可追踪的假设。

静态 knowledge base 可以先提供可审查、可测试、可版本化的标准输入，为后续 resume type classifier、gap analysis、truthfulness checker 和 bullet enhancement 打基础。

## 为什么 M2 使用人工整理静态 profiles，而不是 scraping

M2 不实现 live web scraping，也不解析真实 JD。原因包括：

- 避免误用受限、付费、登录墙或 robots 限制内容。
- 避免把未验证网页内容当成可靠标准。
- 避免让早期系统范围膨胀。
- 先保证 schema、验证、loader 和 selector 稳定。

M2 的 criteria 只表示人工整理的 public role-fit guidance，不代表任何公司的内部招聘规则。

## 支持的 role profiles

- Data Science Intern
- Software Engineering Intern
- Product Manager Intern
- Finance Intern
- Consulting Intern
- Research Assistant / Research CV

## Criteria 如何组织

每个 `ScreeningCriterion` 包含：

- `criterion_id`：稳定 ID。
- `category`：criteria 类别，例如 skill_coverage、role_fit、truthfulness_risk。
- `name` 和 `description`：可读名称和说明。
- `importance`：1 到 5 的重要性。
- `evidence_required`：需要用户提供的证据类型。
- `keywords`：可能帮助 ATS 或 role-fit 判断的关键词。
- `positive_signals`：好的证据表现。
- `negative_signals`：风险或弱证据表现。
- `source`：来源类型和备注。
- `confidence`：0.0 到 1.0 的人工置信度。

## SourceType 和 confidence 如何理解

M2 大多数 criteria 使用 `manually_curated`，表示由项目人工整理的通用岗位适配信号。它不是公司内部标准。

如果未来使用 `public_job_description`，也必须明确它来自公开 JD 模式或用户提供文本，而不是隐藏招聘标准。

`confidence` 表示当前 criteria 作为通用 role-fit indicator 的可靠程度。它不是命中率、录取概率或公司筛选算法权重。

## 不是内部公司筛选规则

本项目不声称知道任何公司的内部简历筛选算法，不抓取机密招聘标准，也不绕过登录墙、付费墙、反爬限制或 robots 限制。

M2 profiles 只是公开岗位能力要求的结构化总结。它们不能被解释为任何雇主的私有筛选规则。

## 未来模块如何使用

- M3 resume type classifier 可以根据目标岗位和 profile resume_types 选择候选方向。
- M4 gap analysis engine 可以比较用户证据和 criteria。
- M5 truthfulness checker 可以结合 negative_signals 标记 unsupported claims。
- M6 bullet enhancement engine 可以在不编造事实的前提下优化 bullet。
- M7+ rendering 模块可以使用通过检查的结构化内容生成 HTML 和 PDF。

## 已知限制

- M2 不解析真实 JD。
- M2 不调用 LLM。
- M2 不做真实 gap analysis。
- M2 不判断录取概率。
- M2 不覆盖所有行业和地区。
- M2 criteria 粒度仍然较粗，需要后续版本扩展和审核。

## 未来扩展计划

- User-provided JD parsing。
- Official hiring guide integration。
- Public JD ingestion with compliance checks。
- Criteria versioning。
- Role-specific localization。
- 按国家、学校阶段、语言和行业细分 criteria。
