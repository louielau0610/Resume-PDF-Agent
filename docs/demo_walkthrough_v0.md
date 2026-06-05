# 演示导览 (Demo Walkthrough v0)

> 中文优先 | Chinese-first

本文档说明如何在本地完整运行 `resume_pdf_agent` 的确定性演示工作流。

## 环境要求

- Python 3.11+
- Windows（`py` launcher）或 macOS/Linux（`python3`）
- 无需 GPU、无需 LLM API key、无需网络连接

## 安装

```bash
# 克隆仓库
git clone https://github.com/louielau0610/Resume-PDF-Agent.git
cd Resume-PDF-Agent

# 安装项目（开发模式）
pip install -e ".[dev]"
```

## 运行确定性演示

### Windows

```bash
# 1. 编译检查所有 Python 文件
py -m compileall src tests

# 2. 运行全部测试（确认系统正常）
py -m pytest -q

# 3. 运行示例工作流并生成前端仪表板
py -m resume_pdf_agent run-sample --output-dir outputs/demo_run --pdf-backend mock --write-frontend-page
```

### macOS / Linux

```bash
# 1. 编译检查
python -m compileall src tests

# 2. 运行测试
pytest -q

# 3. 运行示例工作流
python -m resume_pdf_agent run-sample --output-dir outputs/demo_run --pdf-backend mock --write-frontend-page
```

## 预期输出

运行成功后，`outputs/demo_run/` 目录将包含以下文件：

| 文件名 | 说明 |
|--------|------|
| `criteria_profile.json` | 匹配到的岗位 criteria profile（如 data_science_intern） |
| `classification.json` | 简历类型分类结果（primary type、置信度、信号） |
| `gap_analysis.json` | Criteria 差距分析（匹配度、优势、弱点） |
| `truthfulness.json` | 真实性检查结果（风险等级、问题项、警告） |
| `enhancement.json` | Bullet 增强候选项（改写建议及状态） |
| `template_selection.json` | 内部模板匹配结果（选中模板、评分原因） |
| `workflow_result.json` | 完整工作流结果汇总 |
| `resume.html` | ATS 友好的结构化简历 HTML |
| `resume.pdf` | 从 HTML 生成的 PDF 简历 |
| `index.html` | 静态工作流仪表板（cinematic dark 主题） |

> **注意**：实际文件名可能因版本略有差异，以上为当前 v0 版本的主要产物。

## 各产物含义

### criteria_profile.json
从 6 个静态 criteria profile（data_science_intern、software_engineering_intern 等）中匹配到的岗位筛选标准，包含多个 `ScreeningCriterion` 条目，每个条目有类别、重要性、证据要求、关键词等字段。

### classification.json
确定性规则分类器对用户简历的类型判定结果，包含主类型（如 `data_science_resume`）和排序后的备选类型列表。

### gap_analysis.json
将用户简历内容与 criteria profile 逐条对比，给出匹配等级（strong/medium/weak/missing）和具体证据。

### truthfulness.json
检测简历中是否存在无证据支撑的声明（unsupported claims）、需要用户确认的内容（needs_user_confirmation），输出风险等级（low/medium/high）和 `safe_to_proceed` 标志。

### enhancement.json
基于 criteria 要求，为每条经历生成增强后的 bullet 候选项，标注证据等级（EvidenceLevel）和指标状态（MetricStatus）。

### template_selection.json
从 8 个内部模板中选出最适合的简历模板，包含评分原因。

### resume.html
使用选中的模板渲染的完整 HTML 简历，包含 CSS 样式，可直接在浏览器中打开查看。

### resume.pdf
从 `resume.html` 转换生成的 PDF 文件。

### index.html
静态工作流仪表板页面，展示完整的工作流执行状态、11 个阶段的进度、警告/错误信息、产物链接。使用 cinematic dark 主题。

## Mock PDF Backend 说明

演示和测试默认使用 `--pdf-backend mock`，生成最小有效 PDF（不依赖 WeasyPrint 或 Playwright）。这确保了：

- 演示可在任何环境下运行，无需额外系统依赖
- 测试结果可复现
- CI/CD 友好

## 使用 WeasyPrint（可选）

如需生成更高质量的 PDF，可安装 WeasyPrint 后使用：

```bash
pip install weasyprint
py -m resume_pdf_agent run-sample --output-dir outputs/demo_run --pdf-backend weasyprint --write-frontend-page
```

> WeasyPrint 在 Windows 上可能需要额外配置 GTK 依赖，详见 WeasyPrint 官方文档。

## 其他 CLI 命令

```bash
# 查看可用的 criteria profile ID 列表
py -m resume_pdf_agent list-criteria

# 查看可用的模板 ID 列表
py -m resume_pdf_agent list-templates

# 从自定义 JSON 输入运行
py -m resume_pdf_agent run --input path/to/input.json --output-dir outputs/my_run --pdf-backend mock
```

## v0 限制

- 无 LLM 调用：所有模块使用确定性规则
- 无真实 JD 解析：使用静态 criteria knowledge base
- 仅 PDF 导出：不支持 Word/JPG/PNG
- 无生产 Web 应用：无 FastAPI/Flask/React
- 无浏览器端工作流执行：所有计算在 Python 后端完成
- Mock PDF backend 用于演示：真实 PDF 渲染需 WeasyPrint 或 Playwright

## 下一步

阅读其他 M13 文档了解更多：
- `architecture_diagram_v0.md` — 架构与流程图
- `github_project_overview_v0.md` — 项目概览
- `limitations_and_roadmap_v0.md` — 限制与路线图
- `release_checklist_v0.md` — 发布检查清单
