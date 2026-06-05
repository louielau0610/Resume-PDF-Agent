# 项目概览 (GitHub Project Overview v0)

> 中文优先 | Chinese-first

## 中文概览

`resume_pdf_agent` 是一个 **criteria-aware 的 AI 简历 PDF 生成 Agent**。它不依赖 LLM API 调用，而是通过确定性工作流（deterministic workflow）将用户的职业画像与岗位筛选指标（criteria）进行系统比对，经过简历类型分类、差距分析、真实性检查、Bullet 增强、模板匹配、HTML 渲染等 11 个阶段，最终输出 ATS 友好的结构化 PDF 简历和静态工作流仪表板。

## English Overview

`resume_pdf_agent` is a **criteria-aware AI resume PDF generation agent** that follows a deterministic 11-stage pipeline. Rather than calling LLM APIs, it systematically compares a user's career profile against role-specific screening criteria through resume type classification, gap analysis, truthfulness checking, bullet enhancement, template matching, and HTML-to-PDF rendering. It outputs an ATS-friendly structured PDF resume and a static workflow dashboard.

---

## 核心创新 (Core Innovation)

传统简历工具只做"排版美化"。`resume_pdf_agent` 不同：

1. **Criteria-Aware**：以岗位筛选指标（criteria）为导向，而非仅做格式调整
2. **真实性优先**：内置 truthfulness checker，检测无证据支撑的声明，标记 `needs_user_confirmation` 和 `unsupported` 内容
3. **可解释性**：每个决策（分类、模板选择、增强建议）都有明确的 JSON 产物记录原因
4. **确定性 & 安全**：无 LLM 调用、无网络依赖、不上传用户数据，所有计算在本地完成

## 为什么不止是一个简历格式化工具

| 维度 | 传统格式化工具 | resume_pdf_agent |
|------|---------------|------------------|
| 分析方式 | 模板填空 | Criteria 差距分析 |
| 内容质量 | 不做检查 | 真实性检查 + 证据等级标注 |
| 优化策略 | 通用美化 | 按岗位 criteria 定向增强 bullet |
| 模板选择 | 用户手动选 | 基于简历特征自动匹配 |
| 可解释性 | 无 | 每步输出 JSON 产物 |
| 隐私安全 | 云端处理 | 完全本地运行 |

## 核心模块 (Key Modules)

| 模块 | 功能 | 里程碑 |
|------|------|--------|
| `models` | Pydantic 数据模型（用户画像、简历内容、criteria、分析结果） | M1 |
| `criteria` | 静态 criteria knowledge base（6 个角色 profile）和选择器 | M2 |
| `classifier` | 确定性简历类型分类器（8 种类型） | M3 |
| `gap_analysis` | Criteria 差距分析引擎 | M4 |
| `truthfulness` | 真实性和无证据声明检查 | M5 |
| `enhancement` | Criteria 感知的 bullet 增强引擎 | M6 |
| `templates` | 内部模板元数据匹配（8 个模板） | M7 |
| `rendering` | HTML 简历渲染 | M8 |
| `pdf` | PDF 生成管线（Mock / WeasyPrint / Playwright） | M9 |
| `workflow` | 11 阶段确定性工作流编排器 | M10 |
| `frontend` | 静态工作流仪表板（cinematic dark 主题） | M11/M12 |

## 技术栈 (Technical Stack)

- **Python 3.11+**
- **Pydantic v2** — 数据模型与验证
- **Jinja2** — HTML 模板渲染
- **Typer** — CLI 命令行接口
- **WeasyPrint（可选）** — HTML 转 PDF
- **pytest** — 测试框架
- **纯 CSS** — 前端仪表板（无外部 CDN/字体/图片依赖）

## 安全保障 (What Makes It Safe & Trustworthy)

1. **不调用 LLM API**：所有分析使用确定性规则，无 GPT-4/Claude/Gemini 调用
2. **不联网**：不搜索、不抓取、不上传数据
3. **不声称内部标准**：不声称知道任何公司的内部筛选算法
4. **不预测结果**：不预测录用概率、面试概率或 offer 概率
5. **不虚构数据**：所有输出基于用户提供的证据
6. **真实性检查内置**：自动检测 `unsupported` 和 `needs_user_confirmation` 内容

## 当前功能 (What It Currently Does)

- ✅ 用户画像和简历内容 schema（M1）
- ✅ 6 个静态岗位 criteria profile（M2）
- ✅ 8 种简历类型分类（M3）
- ✅ Criteria 差距分析（M4）
- ✅ 真实性检查（M5）
- ✅ Bullet 增强（M6）
- ✅ 8 个内部模板匹配（M7）
- ✅ HTML 简历渲染（M8）
- ✅ PDF 生成（Mock / WeasyPrint / Playwright）（M9）
- ✅ CLI 命令行接口（M10）
- ✅ 静态工作流仪表板（M11）
- ✅ Cinematic dark 仪表板主题（M12）
- ✅ GitHub 就绪文档和演示打包（M13）

## 不做什么 (What It Does NOT Do)

- ❌ 不调用 LLM API
- ❌ 不解析真实 JD（Job Description）
- ❌ 不导出 Word (.docx)
- ❌ 不导出 JPG/PNG
- ❌ 不提供 Web 应用（无 FastAPI/Flask/React）
- ❌ 不提供浏览器端工作流执行
- ❌ 不联网搜索模板
- ❌ 不预测录用结果

## 推荐 GitHub 仓库描述

**中文：**
> 基于岗位筛选指标的 AI 简历 PDF 生成 Agent：从职业画像、岗位 criteria、真实性检查到 HTML/PDF 输出的确定性工作流。

**English：**
> Criteria-aware AI resume PDF generation agent with role-fit analysis, truthfulness checks, template matching, HTML rendering, and deterministic PDF workflow.

---

*详见 `docs/demo_walkthrough_v0.md` 了解本地演示步骤。*
