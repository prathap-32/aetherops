"""
repo_bridge.py — Module 1 bridge to the repo_analyzer library.

Wraps ``repo_analyzer.pipeline.analyze()`` and translates the resulting
``ApplicationProfile`` into a fully-typed ``RequirementInput`` that the
Module 1 sizing engine can process without modification.

Mapping strategy
----------------
 language / framework hints  →  TechnologyStack (frontend / backend / database)
 detected ports              →  traffic hints
 docker / k8s / ci_cd        →  OperationsPreference
 database findings           →  database field
 monorepo flag               →  stream hint (complex = web_application)
 security findings           →  security_need heuristic
 coverage                    →  educational notes surfaced in the response

The bridge is intentionally deterministic — no LLM calls, no guessing.
Every decision is traceable back to a concrete Finding in the profile.
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

from app.schemas import (
    RequirementInput,
    TechnologyStack,
    OperationsPreference,
    MonitoringPreference,
    TrafficScale,
    ReliabilityLevel,
    SecurityNeed,
    CloudStream,
)

logger = logging.getLogger("repo-bridge")


# ---------------------------------------------------------------------------
# Internal mapping tables
# ---------------------------------------------------------------------------

# repo_analyzer language values → our TechnologyStack.backend bucket
_BACKEND_LANGUAGES: dict[str, str] = {
    "python":      "python_fastapi_django",
    "typescript":  "nodejs_express",
    "javascript":  "nodejs_express",
    "java":        "java_spring",
    "kotlin":      "java_spring",
    "scala":       "java_spring",
    "go":          "python_fastapi_django",   # closest proxy — no go literal in schema
    "rust":        "python_fastapi_django",
    "ruby":        "nodejs_express",
    "php":         "nodejs_express",
    "c#":          "java_spring",
    "c++":         "java_spring",
}

# repo_analyzer framework values → backend bucket (highest-priority override)
_BACKEND_FRAMEWORKS: dict[str, str] = {
    "fastapi":      "python_fastapi_django",
    "django":       "python_fastapi_django",
    "flask":        "python_fastapi_django",
    "express":      "nodejs_express",
    "nestjs":       "nodejs_express",
    "koa":          "nodejs_express",
    "hapi":         "nodejs_express",
    "spring":       "java_spring",
    "spring-boot":  "java_spring",
    "quarkus":      "java_spring",
    "micronaut":    "java_spring",
    "gin":          "python_fastapi_django",
    "fiber":        "python_fastapi_django",
    "rails":        "nodejs_express",
    "laravel":      "nodejs_express",
}

_FRONTEND_FRAMEWORKS: dict[str, str] = {
    "react":    "react_vue_angular",
    "vue":      "react_vue_angular",
    "angular":  "react_vue_angular",
    "next":     "react_vue_angular",
    "nuxt":     "react_vue_angular",
    "svelte":   "react_vue_angular",
    "remix":    "react_vue_angular",
    "gatsby":   "react_vue_angular",
    "html":     "simple_html_css",
    "css":      "simple_html_css",
}

_DATABASE_MAP: dict[str, str] = {
    "postgresql": "postgresql",
    "postgres":   "postgresql",
    "pg":         "postgresql",
    "mysql":      "mysql",
    "mariadb":    "mysql",
    "sqlite":     "mysql",          # closest proxy
    "mongodb":    "mysql",
    "dynamodb":   "mysql",
    "redis":      "mysql",          # used as primary db in some stacks
    "cassandra":  "postgresql",
    "cockroachdb": "postgresql",
}

_ORCHESTRATION_MAP: dict[str, str] = {
    "kubernetes": "kubernetes",
    "k8s":        "kubernetes",
    "helm":       "kubernetes",
    "ecs":        "ecs_fargate",
    "fargate":    "ecs_fargate",
    "docker":     "docker_compose",
    "compose":    "docker_compose",
    "docker-compose": "docker_compose",
}

_CICD_MAP: dict[str, str] = {
    "github_actions": "github_actions",
    "github-actions": "github_actions",
    "github actions": "github_actions",
    "jenkins":        "jenkins",
    "gitlab-ci":      "none",
    "circleci":       "none",
    "travis":         "none",
    "azuredevops":    "none",
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

class RepoBridgeResult:
    """Carries the derived RequirementInput together with rich diagnostic notes."""

    def __init__(
        self,
        requirement_input: RequirementInput,
        repo_name: str,
        is_monorepo: bool,
        languages_detected: list[str],
        frameworks_detected: list[str],
        databases_detected: list[str],
        ports_detected: list[int],
        unknowns: list[str],
        conflicts: list[str],
        errors: list[str],
        coverage_notes: dict,
    ) -> None:
        self.requirement_input = requirement_input
        self.repo_name = repo_name
        self.is_monorepo = is_monorepo
        self.languages_detected = languages_detected
        self.frameworks_detected = frameworks_detected
        self.databases_detected = databases_detected
        self.ports_detected = ports_detected
        self.unknowns = unknowns
        self.conflicts = conflicts
        self.errors = errors
        self.coverage_notes = coverage_notes

    def to_dict(self) -> dict:
        return {
            "repo_name": self.repo_name,
            "is_monorepo": self.is_monorepo,
            "languages_detected": self.languages_detected,
            "frameworks_detected": self.frameworks_detected,
            "databases_detected": self.databases_detected,
            "ports_detected": self.ports_detected,
            "unknowns": self.unknowns,
            "conflicts": self.conflicts,
            "errors": self.errors,
            "coverage_notes": self.coverage_notes,
            "mapped_requirement_input": self.requirement_input.model_dump(),
        }


def analyze_repository(
    repo_path: str | Path,
    *,
    project_name_override: Optional[str] = None,
    monthly_budget: Optional[float] = None,
    traffic_scale_override: Optional[str] = None,
    reliability_override: Optional[str] = None,
) -> RepoBridgeResult:
    """
    Main entry point.  Runs repo_analyzer on *repo_path* and returns a
    :class:`RepoBridgeResult` containing a ready-to-use :class:`RequirementInput`.

    Parameters
    ----------
    repo_path:
        Absolute or relative path to the repository root directory.
    project_name_override:
        If provided, overrides the repo folder name as the project name.
    monthly_budget:
        Optional monthly cost cap forwarded directly to the sizing engine.
    traffic_scale_override:
        ``"hobby_dev"`` / ``"growth"`` / ``"production"`` — caller can
        force a scale instead of inferring from port hints.
    reliability_override:
        ``"dev_testing"`` / ``"production_safe"`` / ``"mission_critical"``
    """
    # -- 1. Run repo_analyzer (static, zero-network, zero-LLM) ----------------
    try:
        from repo_analyzer.pipeline import analyze as _analyze  # type: ignore[import-not-found]
    except ImportError as exc:
        raise ImportError(
            "repo_analyzer is not installed. "
            "Add 'repo-analyzer' to the service's pyproject.toml dependencies."
        ) from exc

    repo_path = Path(repo_path).resolve()
    logger.info("repo_bridge: scanning repository at '%s'", repo_path)
    profile = _analyze(repo_path)
    logger.info(
        "repo_bridge: scan complete — %d component(s), monorepo=%s, "
        "%d findings, %d unknowns",
        len(profile.components),
        profile.is_monorepo,
        len(profile.findings),
        len(profile.unknowns),
    )

    # -- 2. Aggregate finding values across all components --------------------
    all_languages:   list[str] = []
    all_frameworks:  list[str] = []
    all_databases:   list[str] = []
    all_ports:       list[int] = []
    has_docker:      bool = False
    has_k8s:         bool = False
    has_ci_cd:       bool = False
    ci_cd_tool:      str = "none"
    iac_tool:        str = "none"
    has_container:   bool = False
    has_monitoring:  bool = False

    for finding in profile.findings:
        v = finding.value.lower().strip()
        t = finding.type

        if t == "language":
            all_languages.append(v)
        elif t == "framework":
            all_frameworks.append(v)
        elif t in ("database", "cache", "queue"):
            all_databases.append(v)
        elif t == "port":
            try:
                all_ports.append(int(finding.value))
            except (ValueError, TypeError):
                pass
        elif t == "container":
            has_docker = True
            has_container = True
        elif t == "orchestration":
            if "kubernetes" in v or "helm" in v or "k8s" in v:
                has_k8s = True
            elif "ecs" in v or "fargate" in v:
                ci_cd_tool = "ecs_fargate"
            has_container = True
        elif t == "ci_cd":
            has_ci_cd = True
            for key, val in _CICD_MAP.items():
                if key in v:
                    ci_cd_tool = val
                    break
        elif t == "iac":
            if "terraform" in v:
                iac_tool = "terraform"
        elif t == "devops_tool":
            if any(kw in v for kw in ("prometheus", "grafana", "datadog", "newrelic", "cloudwatch")):
                has_monitoring = True

    # deduplicate preserving order
    all_languages  = list(dict.fromkeys(all_languages))
    all_frameworks = list(dict.fromkeys(all_frameworks))
    all_databases  = list(dict.fromkeys(all_databases))
    all_ports      = sorted(set(all_ports))

    # -- 3. Derive TechnologyStack --------------------------------------------
    backend  = _detect_backend(all_languages, all_frameworks)
    frontend = _detect_frontend(all_frameworks, all_languages)
    database = _detect_database(all_databases)

    technology = TechnologyStack(
        frontend=frontend,
        backend=backend,
        database=database,
    )

    # -- 4. Derive OperationsPreference ---------------------------------------
    orchestration = "none"
    if has_k8s:
        orchestration = "kubernetes"
    elif "ecs_fargate" in (ci_cd_tool,):
        orchestration = "ecs_fargate"
    elif has_docker:
        orchestration = "docker_compose"

    operations = OperationsPreference(
        container_orchestration=orchestration,
        infrastructure_as_code=iac_tool,
        configuration_management="none",
        ci_cd_pipeline=ci_cd_tool if ci_cd_tool not in ("none", "ecs_fargate") else "github_actions" if has_ci_cd else "none",
    )

    # -- 5. Derive MonitoringPreference --------------------------------------
    monitoring_level = "advanced" if has_monitoring else ("basic" if has_ci_cd else "none")
    monitoring = MonitoringPreference(
        level=monitoring_level,
        alerting_channel="slack_webhook" if monitoring_level == "advanced" else "email" if monitoring_level == "basic" else "none",
    )

    # -- 6. Derive TrafficScale -----------------------------------------------
    if traffic_scale_override and traffic_scale_override in TrafficScale._value2member_map_:
        traffic_scale = TrafficScale(traffic_scale_override)
    else:
        # Heuristic: presence of high-port (>1000), k8s, or multi-component → growth/production
        if has_k8s or profile.is_monorepo or len(profile.components) >= 3:
            traffic_scale = TrafficScale.growth
        elif backend != "none" and database != "none" and has_container:
            traffic_scale = TrafficScale.growth
        else:
            traffic_scale = TrafficScale.hobby_dev

    # -- 7. Derive ReliabilityLevel -------------------------------------------
    if reliability_override and reliability_override in ReliabilityLevel._value2member_map_:
        reliability = ReliabilityLevel(reliability_override)
    else:
        if has_k8s:
            reliability = ReliabilityLevel.production_safe
        elif has_docker and has_ci_cd:
            reliability = ReliabilityLevel.production_safe
        else:
            reliability = ReliabilityLevel.dev_testing

    # -- 8. Derive SecurityNeed -----------------------------------------------
    security_need = SecurityNeed.standard
    for finding in profile.findings:
        v = finding.value.lower()
        if any(kw in v for kw in ("hipaa", "health", "ehr", "phi")):
            security_need = SecurityNeed.healthcare
            break
        if any(kw in v for kw in ("pci", "payment", "stripe", "braintree", "fintech", "bank")):
            security_need = SecurityNeed.payment_processing
            break

    # -- 9. Derive CloudStream -----------------------------------------------
    stream = _detect_stream(all_frameworks, all_languages, all_databases, profile)

    # -- 10. Project name & storage estimate ----------------------------------
    repo_name = profile.repo or repo_path.name
    project_name = project_name_override or _slugify(repo_name)

    # Rough storage estimate: 5 GB per component, min 5
    data_storage_gb = max(5.0, float(len(profile.components) * 5))

    # -- 11. Assemble RequirementInput ----------------------------------------
    req_input = RequirementInput(
        project_name=project_name,
        stream=stream,
        technology=technology,
        operations=operations,
        monitoring=monitoring,
        traffic_scale=traffic_scale,
        reliability=reliability,
        data_storage_gb=data_storage_gb,
        security_need=security_need,
        monthly_budget=monthly_budget,
        raw_prompt=f"Auto-mapped from repository scan of '{repo_name}'",
    )

    # -- 12. Build coverage notes for the caller ------------------------------
    coverage_notes = {
        "files_scanned": profile.coverage.files_scanned,
        "files_skipped": profile.coverage.files_skipped,
        "bytes_read_kb": round(profile.coverage.bytes_read / 1024, 1),
        "detectors_run": profile.coverage.detectors_run,
        "detectors_failed": profile.coverage.detectors_failed,
        "limits_hit": profile.coverage.limits_hit,
        "languages_without_framework_rules": profile.coverage.languages_without_framework_rules,
    }

    logger.info(
        "repo_bridge: mapped to RequirementInput — backend=%s frontend=%s database=%s "
        "stream=%s traffic=%s reliability=%s",
        backend, frontend, database, stream, traffic_scale.value, reliability.value,
    )

    return RepoBridgeResult(
        requirement_input=req_input,
        repo_name=repo_name,
        is_monorepo=profile.is_monorepo,
        languages_detected=all_languages,
        frameworks_detected=all_frameworks,
        databases_detected=all_databases,
        ports_detected=all_ports,
        unknowns=profile.unknowns,
        conflicts=profile.conflicts,
        errors=profile.errors,
        coverage_notes=coverage_notes,
    )


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _detect_backend(languages: list[str], frameworks: list[str]) -> str:
    # Framework takes precedence over raw language
    for fw in frameworks:
        mapped = _BACKEND_FRAMEWORKS.get(fw)
        if mapped:
            return mapped
    for lang in languages:
        mapped = _BACKEND_LANGUAGES.get(lang)
        if mapped:
            return mapped
    return "none"


def _detect_frontend(frameworks: list[str], languages: list[str]) -> str:
    for fw in frameworks:
        mapped = _FRONTEND_FRAMEWORKS.get(fw)
        if mapped:
            return mapped
    # TypeScript without a backend framework is likely a frontend
    if "typescript" in languages and not any(
        fw in _BACKEND_FRAMEWORKS for fw in frameworks
    ):
        return "react_vue_angular"
    return "none"


def _detect_database(databases: list[str]) -> str:
    # First pass: prefer proper relational databases over cache/queue substitutes
    priority_order = ["postgresql", "postgres", "pg", "cockroachdb", "mysql", "mariadb", "sqlite"]
    for db in priority_order:
        if db in databases:
            return _DATABASE_MAP[db]
    # Second pass: accept anything else in order
    for db in databases:
        mapped = _DATABASE_MAP.get(db.lower())
        if mapped:
            return mapped
    return "none"


def _detect_stream(
    frameworks: list[str],
    languages: list[str],
    databases: list[str],
    profile,
) -> CloudStream:
    fw_set = set(frameworks)
    db_set = set(databases)
    lang_set = set(languages)

    # AI/ML signals
    if any(kw in fw_set | lang_set for kw in ("torch", "tensorflow", "keras", "sklearn", "transformers", "onnx")):
        return CloudStream.ai_ml

    # IoT signals
    if any(kw in db_set for kw in ("mqtt", "influxdb", "timescaledb", "kinesis")):
        return CloudStream.iot

    # DevOps tooling signals
    if any(kw in fw_set | lang_set for kw in ("ansible", "terraform", "puppet", "chef")):
        return CloudStream.devops_tooling

    # Default: web_application for anything with a detectable backend or frontend
    return CloudStream.web_application


def _slugify(name: str) -> str:
    import re
    slug = re.sub(r"[^a-zA-Z0-9\-_]", "-", name).strip("-")
    return slug[:64] or "repo-project"
