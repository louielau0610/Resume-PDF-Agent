# Resume Type Classifier v0

## 它做什么

Resume Type Classifier v0 是 M3 新增的 deterministic、rule-based 分类器。它根据用户画像、可选简历内容和 M2 selected criteria profiles，判断当前用户更适合哪一种简历类型。

输出包括：

- primary resume type
- ranked alternatives
- confidence
- recommended sections
- explanation
- warnings

## 为什么 M3 使用规则而不是机器学习

M3 的目标是建立可解释、可测试、可控的基础分类能力。规则分类器更适合当前阶段：

- 不需要训练数据。
- 不调用 LLM 或外部 API。
- 行为稳定，便于单元测试。
- 可以清楚解释哪些 signal 影响了分类。

后续如果需要更复杂的判断，可以在保留规则基线的前提下引入更丰富的评估集或可选 AI 辅助解释。

## 输入信号

分类器会使用以下 deterministic signals：

- target roles
- target industries
- target companies
- major
- core courses
- skills
- awards
- experience types
- experience titles
- tools used
- methods used
- selected criteria profiles from M2

## 输出结构

`ResumeTypeClassificationResult` 包含：

- `primary_resume_type`
- `ranked_types`
- `confidence`
- `recommended_sections`
- `explanation`
- `warnings`

`ranked_types` 中每个 `ResumeTypeScore` 都包含 resume type、score 和匹配到的 `ClassificationSignal`。

## 支持的 Resume Types

- `technical_resume`
- `data_science_resume`
- `finance_business_resume`
- `consulting_resume`
- `research_cv`
- `product_manager_resume`
- `design_portfolio_resume`
- `general_student_resume`

## M2 Criteria Profiles 如何影响分类

如果调用方传入 M2 的 `RoleCriteriaProfile`，分类器会把 profile 中的 recommended `resume_types` 作为额外信号。例如，Data Science Intern criteria profile 会增强 `data_science_resume`、`technical_resume` 和 `general_student_resume` 的分数。

这只是 deterministic scoring signal，不是 gap analysis，也不是岗位匹配结论。

## 不是 hiring probability model

分类器不预测 hiring success、interview probability 或 offer probability。它只判断简历内容组织形式更接近哪一种 resume type。

## 不知道内部公司筛选规则

本项目不声称知道任何公司的内部简历筛选算法。M3 分类器只使用用户提供的信息、M2 静态 public role-fit criteria 和本地规则。

## 已知限制

- 关键词规则可能漏掉同义词。
- 多语言能力有限。
- 对复杂跨领域 profile 的判断可能偏粗。
- confidence 是规则信号强弱，不是录取概率。
- 不做真实 JD analysis。
- 不做 gap analysis。

## 未来改进

- User-provided JD signal extraction。
- Configurable weights。
- Multilingual keyword expansion。
- Richer classifier evaluation set。
- Optional LLM-assisted explanation in a later milestone。
