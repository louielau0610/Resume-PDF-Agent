# 用户确认工作流 (User Confirmation Workflow v0)

> 中文优先 | Chinese-first

本文档说明 M14 新增的用户确认工作流功能。

## 概述

M14 在确定性工作流中增加了**用户确认层**。在 PDF 生成之前，系统会从已有的分析模块中收集需要用户关注的项，打包成确认包（ConfirmationPacket），生成可审查的文档，并可选择性地在用户确认前阻止最终 PDF 生成。

## 为什么需要确认

在 v0 确定性管线中，truthfulness checker、bullet enhancement 和 gap analysis 模块会检测到：

- **无证据支撑的声明**（unsupported claims）
- **无来源的量化指标**（unsupported metrics）
- **无法验证的量化声明**（unverifiable quantified claims）
- **领导力夸大风险**（leadership exaggeration risk）
- **需要用户确认的增强 bullet**
- **差距分析警告**

这些项不应在用户审核前直接进入最终 PDF。M14 收集这些项并提供审核机制。

## 需要确认的项目类型

| 类型 | 说明 | 优先级 |
|------|------|--------|
| `unsupported_claim` | 无证据支撑的声明 | BLOCKING |
| `unsupported_metric` | 无来源的量化指标 | BLOCKING |
| `unverifiable_quantified_claim` | 无法验证的量化声明 | HIGH |
| `leadership_exaggeration_risk` | 领导力夸大风险 | HIGH |
| `risky_enhanced_bullet` | 有风险标记的增强 bullet | HIGH |
| `needs_confirmation_bullet` | 需要用户确认的 bullet | HIGH |
| `gap_analysis_warning` | 差距分析警告 | MEDIUM |
| `missing_evidence` | 缺失证据 | MEDIUM |

## 生成的文件

运行工作流后，输出目录中会包含以下确认相关文件：

| 文件 | 说明 |
|------|------|
| `confirmation_packet.json` | 结构化的确认项集合（JSON） |
| `confirmation_review.md` | 中文审核文档（Markdown），包含完整的确认项表格和审核指南 |
| `confirmation_review_result.json` | （可选）应用用户决策后的审核结果 |

## 工作模式

### 默认模式（advisory）

默认情况下，确认包作为建议性产物生成，不影响 PDF 输出：

```bash
# Windows
py -m resume_pdf_agent run-sample --output-dir outputs/sample_confirm --pdf-backend mock --write-frontend-page

# macOS / Linux
python -m resume_pdf_agent run-sample --output-dir outputs/sample_confirm --pdf-backend mock --write-frontend-page
```

此模式下：
- ✅ 确认包文件正常生成
- ✅ PDF 正常生成（向后兼容）
- ✅ 用户可自行查看确认包

### 严格门控模式（strict gate）

启用 `--require-confirmation-before-pdf` 后，如果存在阻塞项，系统将跳过 PDF 生成：

```bash
# Windows
py -m resume_pdf_agent run-sample --output-dir outputs/sample_confirm_gate --pdf-backend mock --require-confirmation-before-pdf --write-frontend-page

# macOS / Linux
python -m resume_pdf_agent run-sample --output-dir outputs/sample_confirm_gate --pdf-backend mock --require-confirmation-before-pdf --write-frontend-page
```

此模式下：
- ✅ 确认包文件正常生成
- ❌ 如果有阻塞项，PDF 被跳过
- 📝 CLI 输出说明需要确认后才能生成 PDF

## 如何提供审核决策

用户可以通过创建决策 JSON 文件来审核确认项：

1. 运行工作流生成 `confirmation_packet.json`
2. 查看 `confirmation_review.md` 了解每个确认项的详情
3. 创建决策 JSON 文件（参考 `data/sample_inputs/sample_confirmation_decisions.json`）
4. 使用 `--confirmation-decisions` 加载决策文件：

```bash
py -m resume_pdf_agent run-sample --output-dir outputs/my_run --pdf-backend mock --confirmation-decisions path/to/my_decisions.json --write-frontend-page
```

### 决策类型

| 决策 | 说明 |
|------|------|
| `approve` | 批准声明（您可验证其真实性） |
| `reject` | 拒绝声明（应删除） |
| `needs_editing` | 需要修改（请提供修改文本） |
| `provide_evidence` | 提供证据（请附上支持材料） |
| `ignore_for_now` | 暂不处理（仅限非阻塞项） |

## 安全声明

- 本系统**不独立验证真实世界事实**。确认工作流的目的是让用户审核，而非自动验证。
- 本系统**不预测录用概率、面试概率或 offer 概率**。
- 本系统**不声称知道任何公司的内部筛选标准**。
- 本系统**不调用 LLM API 进行审核**。
- 最终审核责任在用户。请仅批准您能亲自验证的声明。

## 这不是浏览器 UI

M14 提供的是**确定性文件生成**，不是交互式浏览器界面。确认包以 JSON 和 Markdown 文件形式输出，用户通过编辑决策 JSON 文件来提供反馈。未来的 M20 可能考虑浏览器端确认 UI。

## 已知限制

- 确认项基于确定性规则生成，可能存在误报
- 无浏览器端交互式审核界面
- 决策应用后不会自动重写简历内容
- 不进行网络验证或第三方事实核查
- 确认包不包含敏感个人信息过滤（用户应自行审核）

## 未来改进

- M20: 浏览器端确认 UI
- 更丰富的证据溯源
- 可选的 LLM 辅助解释（在 safeguards 之后）
- 与用户编辑集成（确认后重新渲染）

---

*详见 `docs/demo_walkthrough_v0.md` 了解完整演示步骤。*
