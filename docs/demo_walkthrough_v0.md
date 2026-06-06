# 演示导览 (Demo Walkthrough v0)

> 中文优先 | Chinese-first

本文档说明如何在本地完整运行 `resume_pdf_agent` 的各种演示模式。

## 环境要求

- Python 3.11+
- Windows（`py` launcher）或 macOS/Linux（`python3`）
- 无需 GPU、无需 LLM API key、无需网络

## 安装

```bash
git clone https://github.com/louielau0610/Resume-PDF-Agent.git
cd Resume-PDF-Agent
pip install -e ".[dev]"
```

## 验证环境

```bash
py -m compileall src tests scripts
py -m pytest -q
```

## 演示模式

### 1. 基线工作流

```bash
py -m resume_pdf_agent run-sample --output-dir outputs/demo_run --pdf-backend mock --write-frontend-page
```

产物：`resume.html`, `resume.pdf`, `index.html`, `confirmation_packet.json`

### 2. JD 增强模式

```bash
py -m resume_pdf_agent run-sample --output-dir outputs/demo_jd --pdf-backend mock --jd-file data/sample_inputs/sample_data_science_jd.txt --use-user-provided-jd --write-frontend-page
```

额外产物：`parsed_jd.json`, `jd_criteria_profile.json`

### 3. Mock LLM 改写模式

```bash
py -m resume_pdf_agent run-sample --output-dir outputs/demo_llm --pdf-backend mock --enable-llm-rewriting --llm-provider mock --write-frontend-page
```

额外产物：`llm_rewrite_result.json`

### 4. 确认门控模式

```bash
py -m resume_pdf_agent run-sample --output-dir outputs/demo_gate --pdf-backend mock --require-confirmation-before-pdf --write-frontend-page
```

### 5. 视觉回归检查

```bash
py scripts/run_visual_regression_checks.py --output-dir outputs/visual_regression_check
```

### 6. PDF Backend 诊断

```bash
py -m resume_pdf_agent check-pdf-backend
```

### 7. API 烟雾测试（无需 FastAPI）

```bash
py -c "from resume_pdf_agent.api import APIWorkflowRequest, APIWorkflowMode, run_workflow_from_api_request; req=APIWorkflowRequest(mode=APIWorkflowMode.SAMPLE, output_dir='outputs/api_demo', pdf_backend='mock', write_frontend_page=True); res=run_workflow_from_api_request(req); print(res.status)"
```

## Mock PDF Backend

演示默认使用 `--pdf-backend mock`，生成最小有效 PDF，无需 WeasyPrint。

## v0 限制

- 无真实外部 LLM 集成（仅 mock）
- 无生产 Web 应用
- 无浏览器端确认/JD上传/改写审阅 UI
- 无 Word/JPG/PNG 导出
- 无认证/数据库

详见 `limitations_and_roadmap_v0.md` 和 `commercial_product_roadmap_v0.md`。
