# resume_pdf_agent

## M23 LLM 审阅决策摘要

M23 已新增本地 `llm_rewrite_review_decisions.json` 读取与摘要能力，可生成 `llm_rewrite_review_decision_summary.json` 和 `.md`，用于统计 approved / rejected / needs editing / ignored / notes / unknown IDs / duplicate entries。该能力仅生成 advisory summary，不会自动应用 LLM candidates，不会修改最终简历，也不会绕过 M5 真实性检查或 M14 确认门控。

## M22.1 安全加固说明

M22.1 已完成浏览器端 LLM 改写审阅 UI 的安全加固：`llm_review.html` 现在在 Jinja2 模板层启用 autoescape，并继续保持纯本地静态页面。LLM 候选内容仍然只是审阅建议，不会自动应用到简历，不会调用真实 LLM API，也不会绕过 M5 真实性检查或 M14 用户确认门控。

> 基于岗位筛选指标的 AI 简历 PDF 生成 Agent：从职业画像、岗位 criteria、真实性检查到 HTML/PDF 输出的确定性工作流。

`resume_pdf_agent` 是一个 **criteria-aware 的 AI 简历 PDF 生成 Agent**。它不调用 LLM API，而是通过 11 阶段确定性工作流，将用户职业画像与岗位筛选指标（criteria）进行系统比对，经过分类、差距分析、真实性检查、Bullet 增强、模板匹配、HTML 渲染等步骤，最终输出 ATS 友好的结构化 PDF 简历和静态工作流仪表板。

## 当前状态：M19

M19 新增可选 API 层（Optional API Layer），通过 API 风格的请求/响应模型包装现有工作流，FastAPI/uvicorn 为可选依赖。

**已完成里程碑**：M0→M1→M2→M3→M4→M5→M6→M7→M8→M9→M10→M11→M12→M13→M14→M15→M16→M17→M18→**M19** ✅

## 架构概要

```
用户 JSON 输入
→ Criteria 选择（6 个角色 profile）
→ 简历类型分类（8 种类型）
→ 差距分析
→ 真实性检查
→ Bullet 增强
→ 模板匹配（8 个模板）
→ HTML 渲染
→ PDF 生成（Mock/WeasyPrint/Playwright）
→ 前端仪表板（cinematic dark 主题）
```

详见 [`docs/architecture_diagram_v0.md`](docs/architecture_diagram_v0.md) 查看完整 Mermaid 架构图。

## 核心特性

| 特性 | 说明 |
|------|------|
| 🎯 Criteria-Aware | 以岗位筛选指标为导向，非简单模板填空 |
| 🔍 真实性优先 | 内置 truthfulness checker，检测无证据声明 |
| 📊 可解释性 | 每个决策都有 JSON 产物记录原因 |
| 🔒 完全本地 | 无 LLM API 调用、无网络依赖、不上传数据 |
| 🎨 Cinematic Dark 仪表板 | 纯 CSS 静态工作流仪表板，无外部依赖 |
| 🧪 305+ 测试 | 完整测试覆盖，确定性可复现 |

## 快速开始

### 环境要求

- Python 3.11+
- 无需 GPU、无需 LLM API key、无需网络

### 安装

```bash
git clone https://github.com/louielau0610/Resume-PDF-Agent.git
cd Resume-PDF-Agent
pip install -e ".[dev]"
```

### 运行演示

**Windows：**

```bash
# 编译检查
py -m compileall src tests

# 运行测试
py -m pytest -q

# 运行示例工作流并生成仪表板
py -m resume_pdf_agent run-sample --output-dir outputs/demo_run --pdf-backend mock --write-frontend-page
```

**macOS / Linux：**

```bash
python -m compileall src tests
pytest -q
python -m resume_pdf_agent run-sample --output-dir outputs/demo_run --pdf-backend mock --write-frontend-page
```

### 在浏览器中查看

```bash
# 查看简历 HTML
# 打开 outputs/demo_run/resume.html

# 查看工作流仪表板
# 打开 outputs/demo_run/index.html
```

## CLI 命令

```bash
# 使用内置示例数据运行
py -m resume_pdf_agent run-sample --output-dir outputs/my_run --pdf-backend mock --write-frontend-page

# 使用自定义 JSON 输入运行
py -m resume_pdf_agent run --input path/to/input.json --output-dir outputs/my_run

# 查看可用的 criteria profile
py -m resume_pdf_agent list-criteria

# 查看可用的模板
py -m resume_pdf_agent list-templates
```

## 输出产物

运行演示后，`outputs/demo_run/` 目录包含：

| 产物 | 说明 |
|------|------|
| `criteria_profile.json` | 匹配的岗位 criteria profile |
| `classification.json` | 简历类型分类结果 |
| `gap_analysis.json` | Criteria 差距分析 |
| `truthfulness.json` | 真实性检查结果 |
| `enhancement.json` | Bullet 增强候选项 |
| `template_selection.json` | 模板匹配结果 |
| `workflow_result.json` | 完整工作流结果 |
| `resume.html` | ATS 友好的结构化 HTML 简历 |
| `resume.pdf` | PDF 简历 |
| `index.html` | 静态工作流仪表板 |

## 支持的 Criteria Profile

- `data_science_intern` — 数据科学实习
- `software_engineering_intern` — 软件工程实习
- `product_manager_intern` — 产品经理实习
- `finance_intern` — 金融实习
- `consulting_intern` — 咨询实习
- `research_assistant` — 研究助理

## 支持的模板

- `data_science_technical` — 数据科学技术类
- `software_engineering_technical` — 软件工程技术类
- `finance_business` — 金融商务类
- `consulting_business` — 咨询商务类
- `research_cv` — 学术研究 CV
- `product_manager` — 产品经理
- `design_portfolio_light` — 设计作品集轻量版
- `ats_student_basic` — ATS 基础学生模板

## 安全边界

✅ **我们做的：**
- 确定性规则分析（无 LLM 幻觉风险）
- 完全本地运行（无数据上传）
- 真实性检查（标注 unsupported claims）
- 所有决策可追溯（JSON 产物）

❌ **我们不做的：**
- 不调用 LLM API（GPT-4、Claude、Gemini 等）
- 不声称知道任何公司的内部筛选标准
- 不预测录用概率、面试概率或 offer 概率
- 不导出 Word (.docx)、JPG、PNG
- 不提供 Web 应用（无 FastAPI/Flask/React）
- 不联网搜索或抓取数据

## 已知限制

- 静态 criteria knowledge base（6 个角色 profile）
- 无真实 JD（岗位描述）解析
- 无 LLM 辅助改写
- Mock PDF backend 用于演示（WeasyPrint 可选）
- 仅 PDF 导出格式
- 静态前端仪表板（无浏览器端工作流执行）
- ~~无用户确认工作流~~ → M14 已实现 ✅
- 无视觉回归测试
- 无浏览器端确认 UI

详见 [`docs/limitations_and_roadmap_v0.md`](docs/limitations_and_roadmap_v0.md)。

## 路线图

| 里程碑 | 内容 | 状态 |
|--------|------|------|
| M0-M19 | 项目基础 → 完整管线 + 文档 + API 层 | ✅ 已完成 |
| M20 | 浏览器端确认 UI | 🔜 规划中 |

## 测试

```bash
# Windows
py -m compileall src tests scripts
py -m pytest -q

# macOS / Linux
python -m compileall src tests scripts
pytest -q
```

## 项目结构

```
resume_pdf_agent/
├── src/resume_pdf_agent/   # 核心源代码
│   ├── models/             # Pydantic 数据模型 (M1)
│   ├── criteria/           # Criteria knowledge base (M2)
│   ├── classifier/         # 简历类型分类 (M3)
│   ├── gap_analysis/       # 差距分析 (M4)
│   ├── truthfulness/       # 真实性检查 (M5)
│   ├── enhancement/        # Bullet 增强 (M6)
│   ├── templates/          # 模板匹配 (M7)
│   ├── rendering/          # HTML 渲染 (M8)
│   ├── pdf/                # PDF 生成 (M9)
│   ├── workflow/           # 工作流编排 (M10)
│   └── frontend/           # 前端仪表板 (M11/M12)
├── data/                   # 示例输入和 profile 数据
├── docs/                   # 文档 (M13)
├── examples/               # 示例说明 (M13)
├── scripts/                # 演示和验证脚本 (M13)
└── tests/                  # 测试
```

## 文档索引

- [`docs/demo_walkthrough_v0.md`](docs/demo_walkthrough_v0.md) — 演示导览
- [`docs/architecture_diagram_v0.md`](docs/architecture_diagram_v0.md) — 架构图
- [`docs/github_project_overview_v0.md`](docs/github_project_overview_v0.md) — 项目概览
- [`docs/limitations_and_roadmap_v0.md`](docs/limitations_and_roadmap_v0.md) — 限制与路线图
- [`docs/release_checklist_v0.md`](docs/release_checklist_v0.md) — 发布检查清单
- [`PROJECT_STATUS.md`](PROJECT_STATUS.md) — 项目状态
- [`TODO.md`](TODO.md) — 待办与路线图

## 许可证

MIT
