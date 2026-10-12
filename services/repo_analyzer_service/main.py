"""
Module 3 — Repository Analyzer Service entrypoint.
Runs on port 8003 by default.

Usage
-----
    cd services/repo_analyzer_service
    uv run python main.py

    # or from the aether-cloud root:
    uv run python services/repo_analyzer_service/main.py
"""
import os
import sys

# Ensure the service's own package directory is importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8011)),
        reload=bool(os.getenv("DEV_MODE", "")),
        log_config=None,          # We use our own RichHandler
        access_log=True,
    )

