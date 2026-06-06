"""Optional local dev server script for M19 API layer.

Usage:
    py scripts/run_api_dev_server.py
    py scripts/run_api_dev_server.py --host 127.0.0.1 --port 8000

Requires: fastapi, uvicorn (pip install resume-pdf-agent[api])
"""

from __future__ import annotations

import argparse
import sys
from importlib.util import find_spec


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Resume PDF Agent API dev server.")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to.")
    parser.add_argument("--port", type=int, default=8000, help="Port to listen on.")
    args = parser.parse_args()

    # Check optional dependencies
    missing = []
    if find_spec("fastapi") is None:
        missing.append("fastapi")
    if find_spec("uvicorn") is None:
        missing.append("uvicorn")

    if missing:
        print(
            f"Optional API dependencies are not installed: {', '.join(missing)}"
        )
        print("Install with: pip install resume-pdf-agent[api]")
        print("Or manually: pip install fastapi uvicorn")
        return 1

    import uvicorn
    from resume_pdf_agent.api import create_api_app

    app = create_api_app()
    print(f"Starting dev server at http://{args.host}:{args.port}")
    print("API docs: http://{args.host}:{args.port}/docs")
    uvicorn.run(app, host=args.host, port=args.port)
    return 0


if __name__ == "__main__":
    sys.exit(main())
