# TODO

## M1: Core Schemas for User Profile, Resume Content, and Screening Criteria

- 已完成用户画像 schema。
- 已完成简历内容 schema。
- 已完成岗位 criteria schema。
- 已完成 criteria matching / gap analysis result schema。
- 已完成 sample data 和基础测试。

## M2: Static Criteria Knowledge Base v0

- 已完成六个静态 role criteria profiles。
- 已完成 criteria loader。
- 已完成简单 deterministic selector。
- 已完成来源和置信度说明文档。

## M3: Resume Type Classifier

- 已完成 deterministic rule-based classifier。
- 已完成 profile/resume content/criteria profile feature extraction。
- 已完成 ranked resume type 输出、confidence、recommended sections、explanation 和 warnings。

## M4: Criteria-Based Gap Analysis Engine

- 已完成 deterministic evidence extraction。
- 已完成 criterion-level matching。
- 已完成 `GapAnalysisResult` 聚合。
- 已完成 missing keywords、strengths、weaknesses 和基础 truthfulness warnings。

## M5: Truthfulness and Unsupported-Claim Checker

- 检测 unsupported claims。
- 标记虚构指标、夸大成果和证据不足的描述。
- 要求用户补充证据或确认。

## M6: Criteria-Aware Bullet Enhancement Engine

- 根据岗位 criteria 优化 bullet。
- 保持真实、简洁、可追溯。
- 不编造用户未提供的指标。

## M7: Internal Template Matching

- 匹配内部模板。
- 不联网搜索或抓取模板。

## M8: HTML Resume Rendering

- 将结构化内容渲染为稳定 HTML。
- 控制版式、section 顺序和内容长度。

## M9: PDF Generation Pipeline

- 将 HTML 转换为 PDF。
- 添加 PDF-only 导出提醒。

## M10: CLI or API Workflow Integration

- 提供最小可用 CLI 或 API。
- 串联 intake、criteria selection、gap analysis、truthfulness check、rendering 和 export。

## M11: Frontend Basic Workflow Page

- 建立基础前端工作流页面。
- 支持用户输入和结果下载入口。

## M12: Frontend UI Polish Based on User-Provided Sample Images

- 根据用户提供的样例图片优化视觉风格。
- 保持专业、清晰、适合简历生成工作流。
