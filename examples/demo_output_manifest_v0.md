# 演示输出产物清单 (Demo Output Manifest v0)

> 中文优先 | Chinese-first

运行 `resume_pdf_agent` 演示工作流后，输出目录包含以下产物。

---

## 核心产物（始终生成）

| 文件名 | 类型 | 说明 |
|--------|------|------|
| `criteria_profile.json` | JSON | 匹配的岗位 criteria profile |
| `classification.json` | JSON | 简历类型分类结果 |
| `gap_analysis.json` | JSON | Criteria 差距分析结果 |
| `truthfulness.json` | JSON | 真实性检查结果 |
| `enhancement.json` | JSON | Bullet 增强候选项 |
| `template_selection.json` | JSON | 内部模板匹配结果 |
| `resume.html` | HTML | ATS 友好的结构化简历 |
| `resume.pdf` | PDF | 从 HTML 生成的 PDF（mock 后端为最小有效 PDF） |
| `workflow_result.json` | JSON | 完整工作流结果汇总 |

---

## 确认工作流产物的（M14）

| 文件名 | 类型 | 说明 |
|--------|------|------|
| `confirmation_packet.json` | JSON | 需要用户审核的确认项集合 |
| `confirmation_review.md` | Markdown | 中文确认审核文档 |

---

## JD 模式产物（M15）

| 文件名 | 类型 | 说明 |
|--------|------|------|
| `parsed_jd.json` | JSON | 解析后的结构化 JD |
| `jd_criteria_profile.json` | JSON | 从 JD 生成的 criteria profile |

---

## LLM 改写产物（M16，可选）

| 文件名 | 类型 | 说明 |
|--------|------|------|
| `llm_rewrite_result.json` | JSON | LLM 改写候选结果（mock 后端） |

---

## 前端仪表板（M11/M12）

| 文件名 | 类型 | 说明 |
|--------|------|------|
| `index.html` | HTML | Cinematic dark 静态工作流仪表板 |

---

## 安全说明

- 所有 JSON 产物均为结构化数据，不包含原始简历全文
- HTML/PDF 产物基于用户提供的证据生成
- 不包含虚假成就、虚构指标或内部筛选标准
- Mock PDF 后端生成最小有效 PDF（用于测试/演示）

---

*不同工作流模式（基线/JD/LLM/确认门控）生成的产物集合可能略有不同。*
