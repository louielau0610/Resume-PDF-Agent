# 项目状态

## Current Milestone

M4 Criteria-based Gap Analysis Engine

## M0 已完成

- 初始化 Python package 结构。
- 创建 README、英文 README、项目状态、TODO、产品说明和架构说明。
- 添加最小 `pyproject.toml`。
- 添加基础配置常量、异常类型和占位 pipeline。
- 添加基础导入测试。

## M1 已完成内容

- 添加 user profile Pydantic schemas。
- 添加 resume content Pydantic schemas。
- 添加 screening criteria Pydantic schemas。
- 添加 criteria match / gap analysis result schemas。
- 添加 criteria-aware enum 类型。
- 添加泛化 sample user profile、sample resume content 和 sample criteria profile。
- 添加 schema design 文档。
- 添加模型和 sample data 测试。

## M2 已完成内容

- 添加 `data/criteria_profiles/` 下的六个静态 criteria profile JSON 文件。
- 支持 Data Science Intern、Software Engineering Intern、Product Manager Intern、Finance Intern、Consulting Intern、Research Assistant / Research CV。
- 添加 `resume_pdf_agent.criteria` package。
- 添加 available profile ID 查询、JSON loader、全部 profile loader 和简单 deterministic selector。
- 添加 criteria knowledge base 文档和测试。

## M3 已完成内容

- 添加 `ResumeTypeClassificationResult`、`ResumeTypeScore` 和 `ClassificationSignal` models。
- 添加 deterministic feature extraction utilities。
- 添加 rule-based resume type keyword mapping 和 source weights。
- 添加 `classify_resume_type` 主函数。
- 支持 M2 criteria profiles 影响分类结果。
- 添加 classifier 文档和测试。

## M4 已完成内容

- 添加 deterministic evidence extraction utilities。
- 添加 criterion-level matcher。
- 添加 `analyze_criteria_gap` 主函数。
- 支持 importance-weighted overall match level。
- 输出 strengths、weaknesses、missing_keywords 和 truthfulness_warnings。
- 对 impact_quantification、truthfulness_risk、ats_readability 和 education_relevance 添加基础 category-specific handling。
- 添加 gap analysis 文档和测试。

## 尚未实现内容

- Full truthfulness checker logic。
- LLM-based bullet enhancement。
- Internal template matching。
- HTML rendering。
- PDF generation。
- CLI/API workflow integration。
- Frontend UI。
- Frontend UI polish based on sample images。

## 重要产品约束

- 不声称知道任何公司的内部简历筛选算法。
- 不抓取机密或内部招聘标准。
- 不绕过登录墙、付费墙、反爬限制或 robots 限制。
- Criteria 应来自公开 JD、官方页面、官方 hiring guide、大学 career guide、用户提供的 JD 或人工整理知识库。
- v0 只支持 PDF 导出。
- 不生成没有用户证据支持的简历成果、指标或经历描述。
- 前端视觉设计将在后续阶段基于用户提供的样例图片处理。

## 当前说明

M4 只是 deterministic gap analysis foundation。当前代码不会调用模型 API，不会分析真实 JD，不会改写简历，不会渲染 HTML，也不会生成 PDF。
