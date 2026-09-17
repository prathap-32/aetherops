# AetherOps AI - Cloud Infrastructure Microservices

This repository contains the microservice implementations for **Module 1 (Requirement Analysis Service)** and **Module 2 (Cloud Architecture Generator)** of the AetherOps AI (formerly *CloudMentor AI*) platform.

## Microservices Architecture

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

---

## Getting Started

### 1. Installation
This repository uses the `uv` package manager. Install the packages and create virtual environments in the services:
```bash
# Set up workspace packages
uv sync
```

### 2. Run Both Services Concurrently
You can launch both services together using the unified coordinator at the root:
```bash
uv run python main.py
```
* **Module 1** (Requirement Analysis) will run at `http://localhost:8001`
* **Module 2** (Architecture Generator) will run at `http://localhost:8002`

Alternatively, you can run them independently:
```bash
# Run Module 1 only
cd services/requirement_analysis
uv run python main.py

# Run Module 2 only
cd services/architecture_generator
uv run python main.py
```

---

## API & Testing

### Running Tests
To run the test suites for both services:
```bash
# Test Requirement Analysis (Module 1)
PYTHONPATH=services/requirement_analysis uv run pytest services/requirement_analysis/

# Test Architecture Generator (Module 2)
PYTHONPATH=services/architecture_generator uv run pytest services/architecture_generator/
```

### API Endpoints

#### Module 1: Requirement Analysis (`http://localhost:8001`)
* `GET /health` - Service status health check.
* `POST /api/v1/analyze` - Receives scale/SLA targets, outputs computed AWS architecture specifications (`RequirementProfileOutput`).

#### Module 2: Architecture Generator (`http://localhost:8002`)
* `GET /health` - Service status health check.
* `POST /api/v1/generate-graph` - Receives `RequirementProfileOutput`, outputs React Flow coordinates and elements (`ReactFlowGraphJSON`).