# 发布检查清单 (Release Checklist v0)

> 中文优先 | Chinese-first

本文档列出 `resume_pdf_agent` v0 发布前的自检项。在每次提交或发布前逐项确认。

## 环境 (Environment)

- [ ] Python 3.11+ 已安装
- [ ] 项目依赖已安装：`pip install -e ".[dev]"`
- [ ] 无需 LLM API key（系统不调用 LLM）
- [ ] 无需网络连接（系统不联网）
- [ ] 无需外部系统依赖（mock PDF backend 可用）

## 安装 (Installation)

- [ ] `pip install -e ".[dev]"` 无报错
- [ ] `py -m compileall src tests scripts` 编译通过
- [ ] 无需额外手动配置即可运行

## 测试 (Tests)

- [ ] `py -m pytest -q` 全部通过（305+ tests）
- [ ] 无 skipped tests（除非有明确文档说明）
- [ ] 无 xfail tests（除非有对应 issue 追踪）
- [ ] 现有 M0-M12 测试无退化
- [ ] M13 新增测试通过

## CLI 演示 (CLI Demo)

- [ ] `py -m resume_pdf_agent run-sample --output-dir outputs/demo_run --pdf-backend mock --write-frontend-page` 成功运行
- [ ] `py -m resume_pdf_agent list-criteria` 输出正确的 profile ID 列表
- [ ] `py -m resume_pdf_agent list-templates` 输出正确的 template ID 列表
- [ ] `py -m resume_pdf_agent run --input data/sample_inputs/sample_data_science_user.json --output-dir outputs/test_run --pdf-backend mock` 成功运行

## 输出产物 (Output Artifacts)

- [ ] `outputs/demo_run/index.html` 已生成（前端仪表板）
- [ ] `outputs/demo_run/resume.html` 已生成（HTML 简历）
- [ ] `outputs/demo_run/resume.pdf` 已生成（PDF 简历，mock backend）
- [ ] `outputs/demo_run/criteria_profile.json` 已生成
- [ ] `outputs/demo_run/classification.json` 已生成
- [ ] `outputs/demo_run/gap_analysis.json` 已生成
- [ ] `outputs/demo_run/truthfulness.json` 已生成
- [ ] `outputs/demo_run/enhancement.json` 已生成
- [ ] `outputs/demo_run/template_selection.json` 已生成
- [ ] `outputs/demo_run/workflow_result.json` 已生成

## 文档 (Documentation)

- [ ] `README.md`（中文）存在且内容完整
- [ ] `README.en.md`（英文）存在且内容完整
- [ ] `PROJECT_STATUS.md` 更新到 M13
- [ ] `TODO.md` 更新路线图
- [ ] `docs/demo_walkthrough_v0.md` 存在
- [ ] `docs/architecture_diagram_v0.md` 存在且包含 Mermaid 图表
- [ ] `docs/github_project_overview_v0.md` 存在
- [ ] `docs/release_checklist_v0.md` 存在（即本文档）
- [ ] `docs/limitations_and_roadmap_v0.md` 存在
- [ ] `examples/README.md` 存在
- [ ] `examples/sample_data_science_demo.md` 存在

## 安全声明检查 (Safety Claims)

- [ ] README 不声称知道内部筛选标准
- [ ] README 不声称预测录用概率
- [ ] README 不声称预测面试概率
- [ ] README 不声称预测 offer 概率
- [ ] README 不声称 Word/JPG/PNG 导出已实现
- [ ] README 记录了 v0 仅支持 PDF 的限制
- [ ] 所有文档不包含虚假公司特定标准
- [ ] 所有样本数据明确标注为测试用途

## 已知限制 (Known Limitations)

- [ ] README 记录了无 LLM 调用
- [ ] README 记录了无真实 JD 解析
- [ ] README 记录了 mock PDF backend
- [ ] README 记录了仅 PDF 导出
- [ ] README 记录了无 Web 应用
- [ ] 限制文档 `limitations_and_roadmap_v0.md` 内容完整

## GitHub 就绪 (GitHub Readiness)

- [ ] `.gitignore` 忽略 `outputs/`、`__pycache__/`、`.pytest_cache/`
- [ ] 无大型生成输出文件被提交
- [ ] 仓库描述准确
- [ ] 提交历史清晰
- [ ] Commit message 有意义
- [ ] `git status` 干净（无不必要的未跟踪文件）

## 可选未来发布项 (Optional Future Release Items)

- [ ] WeasyPrint 生产环境安装指南 (M17)
- [ ] 用户确认工作流 (M14)
- [ ] 真实 JD 解析器 (M15)
- [ ] 可选 LLM 辅助改写 (M16)
- [ ] 视觉回归测试 (M18)
- [ ] 可选 Web 应用层 (M19)

---

*以上 M14-M19 为路线图想法，尚未实现。*
