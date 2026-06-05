# Internal Template Matching v0

## 它做什么

M7 Internal Template Matching v0 会从内部 template metadata library 中选择最适合当前用户和简历类型的模板 metadata。它为后续 M8 HTML rendering 和 M9 PDF generation 提供结构化选择结果。

## 为什么使用内部模板

项目使用内部模板 metadata，而不是联网搜索模板，原因是：

- 版权和来源边界更清晰。
- 便于测试 ATS-friendly 结构。
- 避免引入未知网页内容。
- 保持 deterministic 和可审查。

## M7 不做什么

M7 只选择 template metadata，不渲染 HTML，不生成 PDF，不实现前端 UI，也不做在线模板搜索。

## 支持的内部模板

- `ats_student_basic`
- `data_science_technical`
- `software_engineering_technical`
- `finance_business`
- `consulting_business`
- `research_cv`
- `product_manager`
- `design_portfolio_light`

## 输入信号

- Resume type classification
- Criteria profile
- Resume content
- Gap analysis
- Bullet enhancement result
- User profile

## 输出

`TemplateSelectionResult` 包含：

- selected_template_id
- selected_template
- ranked_templates
- recommended_sections
- warnings
- summary

## Scoring 高层逻辑

Selector 会根据 primary resume type、criteria resume types、resume_content resume_type、target roles、research/portfolio/project-heavy signals、ATS-friendly、one-page support 和 truthfulness blockers 进行 deterministic scoring。

如果没有清晰匹配，会回退到 `ats_student_basic`。

## 不是 Hiring Probability

Template selection 不预测 hiring success、interview probability 或 offer probability。

## 不知道内部公司筛选规则

本项目不声称知道任何公司的内部简历筛选算法。M7 只使用内部 template metadata 和用户提供/系统生成的结构化信号。

## 已知限制

- M7 只有 metadata，没有真实 HTML 模板。
- 没有 PDF 输出。
- 没有用户手动 override。
- 设计类模板只是 portfolio-light metadata，不做视觉重 UI。

## 未来改进

- M8 actual HTML templates。
- M9 PDF rendering。
- User-selectable template override。
- Style variants。
- Sample-image-based frontend UI polish later。
