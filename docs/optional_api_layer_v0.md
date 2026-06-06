# 可选 API 层 (Optional API Layer v0)

> 中文优先 | Chinese-first

## 概述

M19 添加了**可选的 API 适配层**，将现有确定性工作流包装为 API 风格的请求/响应模型。

**CLI 仍然是主要的稳定接口。API 层是可选扩展。**

## 为什么是可选

- CLI 是经过充分测试的稳定基线
- FastAPI 是可选的（未安装在核心依赖中）
- 无生产 Web 应用部署要求
- 保持项目依赖最小化

## API 模型

### APIWorkflowRequest

```python
req = APIWorkflowRequest(
    mode="sample",           # "sample" or "custom"
    output_dir="outputs/run",
    pdf_backend="mock",
    write_frontend_page=True,
)
```

### APIWorkflowResponse

包含工作流状态的完整结构，包括输出路径、产物列表、警告和错误。

### APIHealthResponse

报告可用功能和可选依赖状态。

## 安装可选 API 依赖

```bash
pip install resume-pdf-agent[api]
# 或手动
pip install fastapi uvicorn
```

## 服务层使用（无需 FastAPI）

```python
from resume_pdf_agent.api import (
    APIWorkflowRequest,
    APIWorkflowMode,
    run_workflow_from_api_request,
)

req = APIWorkflowRequest(
    mode=APIWorkflowMode.SAMPLE,
    output_dir="outputs/my_run",
    pdf_backend="mock",
    write_frontend_page=True,
)
response = run_workflow_from_api_request(req)
print(response.status, response.html_output_path)
```

## 本地开发服务器（需要 FastAPI）

```bash
py scripts/run_api_dev_server.py --host 127.0.0.1 --port 8000
```

端点：
- `GET /` — 服务元数据
- `GET /health` — 健康检查
- `POST /workflow/run` — 运行工作流
- `GET /artifacts?output_dir=...` — 列出产物

## 已知限制

- 无生产 Web 应用部署
- 无前端 UI
- 无文件上传 UI
- 无用户认证
- 无数据库
- 无 Word/JPG/PNG 导出
- 无浏览器端工作流执行
- FastAPI 为可选依赖

## 未来改进

- 浏览器端确认 UI (M20)
- 浏览器端 JD 上传 UI (M21)
- 浏览器端 LLM 改写审阅 UI (M22)
- 认证/数据库（仅当产品化后）
