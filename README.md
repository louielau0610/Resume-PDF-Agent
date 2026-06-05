# resume_pdf_agent

`resume_pdf_agent` 是一个 criteria-aware 的 AI 简历 PDF 生成 Agent，目标是帮助学生、实习申请者和早期职业候选人，把职业画像、公开岗位要求、官方招聘指导、用户提供的 JD 文本和人工整理的岗位标准，转化为真实、ATS 友好的 PDF 简历内容。

本项目不是通用的“简历美化聊天机器人”。它是一个工作流驱动的简历生成系统，围绕公开、可解释、可追踪的 role-specific screening criteria 来诊断和优化简历，而不是声称掌握任何公司的内部筛选算法。

## 项目定位

项目长期目标是建立从用户信息、岗位标准、证据匹配、真实性检查到 PDF 简历输出的可控流程。

重要约束：

- 不声称知道任何公司的内部简历筛选算法。
- 不抓取机密或内部招聘标准。
- 不绕过登录墙、付费墙、反爬限制或 robots 限制。
- 后续只使用公开 JD、官方职业页面、官方招聘指导、大学 career guide、用户提供的 JD 文本和人工整理的岗位标准。
- 不编造用户成就，不发明没有证据支持的指标。
- v0 只导出 PDF，不生成 Word、JPG 或 PNG。
- 如用户需要 Word/JPG/PNG，可使用外部 AI 工具或 PDF 转换工具。
- 前端 UI polish 暂不处理，后续会基于用户提供的样例图进行。

## 长期 Pipeline

1. User Intake
2. Criteria Retrieval / Selection
3. Criteria Extraction / Normalization
4. Candidate Profile Structuring
5. Gap Analysis
6. Truthfulness Check
7. Criteria-aware Bullet Enhancement
8. Resume Type Classification
9. Internal Template Matching
10. HTML Rendering
11. PDF Generation
12. Reminder Panel

## 当前 M4 阶段

M4 添加 Criteria-based Gap Analysis Engine v0：一个 deterministic、rule-based 的诊断模块。它会比较 `UserProfile`、可选 `ResumeContent` 和一个 M2 `RoleCriteriaProfile`，输出 criteria-level match results、strengths、weaknesses、missing keywords、diagnostic suggested actions 和基础 truthfulness warnings。

M4 可以诊断：

- 哪些 criteria 有较强用户证据支持。
- 哪些 criteria 只有部分、较弱或缺失证据。
- 当前 profile/resume content 缺少哪些重要关键词。
- 哪些内容存在 unsupported evidence、unsupported metric、needs_confirmation 或 risk_flags。
- 用户应补充哪些真实证据，但不会生成或改写最终 resume bullets。

Gap analysis 不预测 hiring success，不代表任何公司内部筛选规则，也不会改写简历。

M4 仍然不实现 LLM 改写、真实 JD 动态分析、resume bullet rewriting、HTML rendering、PDF 生成、模板匹配或前端 UI。v0 仍然只面向 PDF 导出。

## 后续 Milestones

- M5：Truthfulness and unsupported-claim checker。
- M6：Criteria-aware bullet enhancement engine。
- M7：Internal template matching。
- M8：HTML resume rendering。
- M9：PDF generation pipeline。
- M10：CLI or API workflow integration。
- M11：Frontend basic workflow page。
- M12：Frontend UI polish based on user-provided sample images。

## 本地开发

建议使用 Python 3.11 或更高版本。

Windows:

```bash
py -m venv .venv
.venv\Scripts\activate
py -m pip install -e ".[dev]"
```

如果 `python` 命令在 Windows 环境不可用，请使用 `py -m ...`。

macOS 或 Linux:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

## 测试命令

Windows:

```bash
py -m compileall src tests
py -m pytest -q
```

macOS 或 Linux:

```bash
python -m compileall src tests
pytest -q
```

## 当前限制

当前 M4 版本只是 deterministic gap analysis foundation。它不会调用 LLM，不会分析真实 JD，不会改写简历，不会搜索模板，不会渲染 HTML，不会生成 PDF，也不会实现前端 UI。
