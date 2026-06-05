# 用户提供的 JD 解析器 (User-provided JD Parser v0)

> 中文优先 | Chinese-first

本文档说明 M15 新增的用户提供 JD 解析器功能。

## 概述

M15 允许用户提供本地岗位描述（JD）文本文件，系统将其解析为结构化数据并转换为可用的 RoleCriteriaProfile，替代静态 M2 criteria knowledge base 进行后续分析。

## 为什么只接受本地文本

- **合规安全**：系统不抓取网页、不访问 URL、不绕过登录墙
- **用户控制**：用户自己提供并审核 JD 内容
- **隐私保护**：不上传数据到任何服务器

## 合规检查

在解析 JD 之前，系统会进行确定性合规检查：

### 阻止的内容（blocked）

包含以下标记的文本将被拒绝：
- `confidential` / `internal use only` / `do not distribute`
- `proprietary hiring rubric` / `resume screening algorithm`
- `interview scorecard` / `candidate evaluation form`
- `scoring rubric` / `not for public release` / `restricted access`

### 警告的内容（allowed_with_warnings）

包含以下标记的文本将被允许但产生警告：
- `recruiter screen` / `hiring manager notes`
- `assessment criteria` / `interview feedback`
- `evaluation criteria`

### 合规状态

| 状态 | 说明 |
|------|------|
| `allowed` | 通过检查，可以解析 |
| `allowed_with_warnings` | 有需注意的问题，但仍可解析 |
| `blocked` | 被阻止，不会解析为 criteria |

## 解析的 JD 字段

| 字段 | 说明 |
|------|------|
| `role_title` | 岗位名称 |
| `company_name` | 公司名称（如果提供） |
| `location` | 工作地点（如果提供） |
| `employment_type` | 雇佣类型 |
| `seniority_level` | 资历级别（intern/entry/junior/mid/senior/unknown） |
| `responsibilities` | 岗位职责 |
| `required_qualifications` | 必备资格 |
| `preferred_qualifications` | 优先资格 |
| `skills` | 技能关键词 |
| `education_requirements` | 学历要求 |

## JD 转 Criteria

解析后的 JD 会被转换为 `RoleCriteriaProfile`：

- 必备资格 → importance 5
- 岗位职责 → importance 4
- 技能关键词 → importance 4
- 优先资格 → importance 3
- 学历要求 → importance 3
- ATS 可读性 → importance 4
- 影响量化 → importance 4
- 真实性风险 → importance 5

所有 criteria 的 `source_type` 标记为 `user_provided_jd`，confidence 设为 0.75。

## CLI 使用

```bash
# 使用示例 JD 文件运行
py -m resume_pdf_agent run-sample --output-dir outputs/sample_jd --pdf-backend mock --jd-file data/sample_inputs/sample_data_science_jd.txt --use-user-provided-jd --write-frontend-page

# 严格门控 + JD 模式（如果 M14 已实现）
py -m resume_pdf_agent run-sample --output-dir outputs/sample_jd_gate --pdf-backend mock --jd-file data/sample_inputs/sample_data_science_jd.txt --use-user-provided-jd --require-confirmation-before-pdf --write-frontend-page
```

## 输出产物

| 产物 | 说明 |
|------|------|
| `parsed_jd.json` | 解析后的结构化 JD |
| `jd_criteria_profile.json` | 从 JD 生成的 RoleCriteriaProfile |

## 已知限制

- 确定性解析器，无 NLP/LLM 辅助
- 无网页抓取或 URL 获取
- 不保证完美提取所有字段
- 技能提取基于静态关键词词典
- 不支持多语言 JD（目前主要支持英文）
- 无浏览器端 JD 上传 UI
- 不合规检查在线验证（仅本地文本匹配）

## 未来改进

- 可选 LLM 辅助 JD 解析（在合规检查之后）
- 官方 JD 来源元数据
- 更丰富的多语言解析
- 浏览器端 JD 上传 UI (M21)
- JD 解析结果用户确认

---

*详见 `docs/demo_walkthrough_v0.md` 了解完整演示步骤。*
