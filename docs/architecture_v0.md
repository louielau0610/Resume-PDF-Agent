# Architecture v0

## 高层架构

`resume_pdf_agent` 计划采用分阶段 pipeline 架构。每个阶段接收结构化输入，输出明确的数据对象，避免让单个模型调用直接决定全部简历内容和版式。

计划阶段：

1. User Intake
2. Profile Structuring
3. Resume Type Classification
4. Content Enhancement
5. Truthfulness Check
6. Internal Template Matching
7. HTML Resume Rendering
8. PDF Rendering
9. Reminder Panel

## 数据流

用户输入先进入 intake 层，随后被转换为结构化 profile。结构化 profile 会进入分类器，得到 resume_type。内容增强模块基于原始经历和目标岗位生成候选 bullet points。真实性检查模块会标记缺少证据的表述。通过检查后的内容会匹配内部模板，先渲染为 HTML，再生成 PDF。

简化数据流：

```text
raw user input
  -> structured profile
  -> resume type
  -> enhanced resume content
  -> truthfulness report
  -> internal template
  -> HTML resume
  -> PDF resume
  -> reminder panel
```

## 计划模块

- `config`：项目配置和支持格式。
- `schemas`：后续用于定义用户画像和简历内容结构。
- `classifier`：后续用于简历类型分类。
- `enhancer`：后续用于内容增强。
- `truthfulness`：后续用于检查 unsupported claims。
- `templates`：后续用于内部模板管理。
- `renderer`：后续用于 HTML 和 PDF 渲染。
- `pipeline`：串联各阶段工作流。

## 为什么 LLM 只应生成结构化内容，而不直接控制布局

LLM 适合整理文本、抽取字段、改写 bullet points 和发现潜在问题，但不适合直接控制最终版式。简历 PDF 需要稳定的页边距、字体、间距、分页和内容长度控制。如果让 LLM 直接生成布局，结果可能不稳定、不可测试，也难以保证 ATS 友好。

因此，后续设计应让 LLM 输出结构化内容，由确定性的模板和渲染器负责布局。

## 为什么内部模板比联网搜索模板更安全

内部模板更可控：

- 可以保证版权和使用边界清晰。
- 可以统一 ATS 友好规则。
- 可以测试不同内容长度下的布局表现。
- 可以避免引入未知网页内容、恶意模板或低质量模板。

本项目第一版明确不联网搜索或抓取简历模板。

## 为什么 v0 选择 PDF-only 导出

PDF 是简历投递中最常见、版式最稳定的交付格式。v0 选择 PDF-only 可以降低实现范围，优先保证核心简历内容、模板匹配和渲染质量。

Word、JPG 和 PNG 导出会引入额外格式兼容、分页、图片清晰度和样式一致性问题。当前版本只提醒用户如需这些格式，可使用外部 AI 工具或 PDF 转换工具。

## 当前 M0 状态

当前代码只提供 package、配置、异常、占位 pipeline 和基础测试。它不会调用 LLM，不会匹配模板，也不会生成 HTML 或 PDF。
