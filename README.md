# AetherOps AI - Cloud Infrastructure Microservices

This repository contains the microservice implementations for the AetherOps microservices.

## UV-based Workspace (preferred)

This repository uses the `uv` workspace manager. Each service is a separate Python package with its own `pyproject.toml` and `uv` creates isolated virtual environments for each package and syncs dependencies from the manifests.

Quick start (recommended):

1. Install `uv` (if not already installed). Example:

```bash
pip install uv
```

2. Sync the workspace and create per-service virtual environments:

```bash
uv sync
```

3. Run the unified coordinator (dev entrypoint):

```bash
uv run python main.py
```

4. Run a single service (from repo root or inside the service directory):

```bash
# from repo root
uv run -C services/requirement_analysis python main.py

# or inside the service directory
cd services/requirement_analysis
uv run python main.py
```

Notes:
- Each service already contains a `pyproject.toml` with its dependencies. `uv sync` reads these and prepares per-service environments.
- Tests can be executed with `uv run pytest services/<service_name>/` as shown in the original README.

---

## Legacy (deprecated)

A `requirements.txt` file previously existed for a consolidated pip-style install, but this repository now uses `uv` and the per-service `pyproject.toml` files as the authoritative source of dependencies. Prefer `uv sync` and `uv run` over pip installs at the repo root.

---

## Microservices Architecture (unchanged)

```text
aether-cloud/
├── services/
│   ├── requirement_analysis/      # Module 1 microservice (Port 8001)
│   │   ├── app/
│   │   │   ├── catalog.py         # Resource specs and pricing structures
│   │   │   ├── schemas.py         # Pydantic v2 input/output data models
│   │   │   ├── engine.py          # Deterministic rules profiling engine
│   │   │   └── main.py            # FastAPI service exposing endpoints
│   │   ├── tests/
│   │   │   └── test_engine.py     # Independent test suite for Module 1
│   │   ├── pyproject.toml         # Module 1 dependencies
│   │   └── main.py                # Port 8001 entrypoint
│   │
│   └── architecture_generator/    # Module 2 microservice (Port 8002)
│       ├── app/
│       │   ├── schemas.py         # React Flow structures & layout types
│       │   ├── generator.py       # DAG coordinate generation logic
│       │   └── main.py            # FastAPI service exposing endpoints
│       │   tests/
│       │   └── test_generator.py  # Independent test suite for Module 2
│       │   pyproject.toml         # Module 2 dependencies
│       └── main.py                # Port 8002 entrypoint
│
└── main.py                        # Unified Microservices Coordinator (dev entrypoint)
```
