# 数据科学示例说明 (Sample Data Science Demo)

> 中文优先 | Chinese-first

本文档描述 `resume_pdf_agent` 内置的数据科学实习生示例。

## 示例简介

内置示例模拟了一位统计学与计算机科学双专业本科生申请数据科学实习岗位的场景。所有数据均为通用示例，不代表真实个人。

## 示例用户画像摘要

| 字段 | 值 |
|------|-----|
| 姓名 | Alex Chen（示例名） |
| 学历 | 统计学与计算机科学 本科在读 |
| GPA | 3.7/4.0 |
| 目标岗位 | Data Science Intern |
| 技能 | Python、SQL、R、pandas、NumPy、scikit-learn、Matplotlib、Tableau |
| 语言 | 英语（专业工作水平）、中文（母语） |
| 获奖 | 大学数据挑战赛决赛入围 |

## 目标角色

**Data Science Intern**（数据科学实习生）

对应的 criteria profile ID：`data_science_intern`

## 预期 Criteria Profile

匹配到 `data_science_intern` profile，该 profile 包含以下类别 criteria：

- **role_fit**：数据科学相关背景、统计建模能力
- **skill_coverage**：Python、SQL、ML 库、数据可视化
- **evidence_strength**：项目经历、课程项目可验证性
- **impact_quantification**：量化结果的能力
- **action_result_clarity**：行为-结果表述清晰度
- **education_relevance**：统计学/计算机科学专业对口
- **ats_readability**：ATS 系统可读性
- **truthfulness_risk**：声明真实性风险评估

## 预期简历类型

分类器预期输出：

- **Primary type**：`data_science_resume`
- **Confidence**：medium-high
- **Signals**：Python + ML 工具链、统计课程、数据分析项目

## 预期模板方向

模板选择器预期推荐：

- **首选**：`data_science_technical`（数据科学技术类模板）
- **备选**：`ats_student_basic`（ATS 基础学生模板）

## 预期产物

| 产物 | 说明 |
|------|------|
| `criteria_profile.json` | data_science_intern 的完整 criteria 内容 |
| `classification.json` | 简历类型分类为 data_science_resume |
| `gap_analysis.json` | 与 data science intern criteria 的差距分析 |
| `truthfulness.json` | 各声明的证据等级评估 |
| `enhancement.json` | 按 criteria 增强的 bullet 候选项 |
| `template_selection.json` | 模板选择为 data_science_technical |
| `workflow_result.json` | 完整工作流结果 |
| `resume.html` | 使用 data_science_technical 模板渲染 |
| `resume.pdf` | 从 HTML 生成的 PDF |
| `index.html` | 工作流仪表板页面 |

## 安全说明

- 示例数据中的人物为虚构，不代表真实申请人
- 所有经历、技能、获奖均为通用示例
- 不包含虚假夸大的成就
- 不包含真实公司信息或个人身份信息
- 示例中的 `evidence_notes` 明确标注为基于示例 profile 描述

## Mock Backend 说明

本示例默认使用 `--pdf-backend mock`。Mock backend 生成最小有效 PDF 文件，用于验证管线完整性，不依赖 WeasyPrint 或 Playwright 的系统级依赖。

如需真实 PDF 渲染，安装 WeasyPrint 后使用 `--pdf-backend weasyprint`。

## 运行命令

```bash
# Windows
py -m resume_pdf_agent run-sample --output-dir outputs/demo_run --pdf-backend mock --write-frontend-page

# macOS / Linux
python -m resume_pdf_agent run-sample --output-dir outputs/demo_run --pdf-backend mock --write-frontend-page
```

---

*详见 `docs/demo_walkthrough_v0.md` 了解完整演示步骤。*
