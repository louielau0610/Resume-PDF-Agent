# 示例目录 (Examples)

> 中文优先 | Chinese-first

本目录包含 `resume_pdf_agent` 的示例文件和演示说明。

## 目录结构

```
examples/
├── README.md                        # 本文件
└── sample_data_science_demo.md      # 内置数据科学示例说明
```

## 示例输入文件

内置示例输入文件位于：

```
data/sample_inputs/sample_data_science_user.json
```

该文件包含一个模拟的数据科学实习生候选人的用户画像和简历内容。

## 如何运行示例

### Windows

```bash
# 运行内置示例工作流
py -m resume_pdf_agent run-sample --output-dir outputs/demo_run --pdf-backend mock --write-frontend-page
```

### macOS / Linux

```bash
python -m resume_pdf_agent run-sample --output-dir outputs/demo_run --pdf-backend mock --write-frontend-page
```

## 输出位置

所有产物输出到 `outputs/demo_run/`（或其他你指定的 `--output-dir`）目录。

## 为什么输出目录通常不提交

- `outputs/` 目录已在 `.gitignore` 中忽略
- 生成的文件包含 PDF、HTML 等二进制产物，不适合版本控制
- 所有产物可通过运行 CLI 命令随时重新生成
- 保持仓库体积小、干净

## 如何查看生成的产物

### HTML 简历

直接用浏览器打开 `outputs/demo_run/resume.html`。

### PDF 简历

直接用 PDF 阅读器打开 `outputs/demo_run/resume.pdf`。

### 工作流仪表板

直接用浏览器打开 `outputs/demo_run/index.html`。

### JSON 中间产物

用任意文本编辑器或 JSON 查看器打开 `outputs/demo_run/` 下的 `.json` 文件，了解每个阶段的分析结果。

## 自定义示例

如需用自己的数据运行工作流，参考以下步骤：

1. 准备符合 `ResumeWorkflowInput` schema 的 JSON 文件（参考 `data/sample_inputs/sample_data_science_user.json`）
2. 运行：

```bash
py -m resume_pdf_agent run --input path/to/your_input.json --output-dir outputs/my_run --pdf-backend mock --write-frontend-page
```

3. 查看 `outputs/my_run/` 下的产物

## 相关文档

- `docs/demo_walkthrough_v0.md` — 完整演示导览
- `docs/architecture_diagram_v0.md` — 架构与流程图
- `data/sample_inputs/` — 示例输入文件
