"""
scanner_engine.py — Module 3 core scanning logic.

Wraps repo_analyzer.pipeline.analyze() and surfaces a clean, serialisable
result dict that the FastAPI layer can return directly.
"""
from __future__ import annotations

import logging
from pathlib import Path

logger = logging.getLogger("repo-analyzer-service.engine")


def scan_repository(repo_path: str | Path, *, include_findings: bool = False) -> dict:
    """
    Run repo_analyzer on *repo_path* and return a serialisable result dict.

    Parameters
    ----------
    repo_path:
        Must be an existing directory.
    include_findings:
        When True, the raw Finding list is included in the response (verbose).

    Returns
    -------
    dict with keys matching :class:`app.schemas.ScanResponse`.
    """
    try:
        from repo_analyzer.pipeline import analyze  # type: ignore[import-not-found]
    except ImportError as exc:
        raise ImportError(
            "repo_analyzer is not installed. Ensure 'repo-analyzer' is listed "
            "in pyproject.toml dependencies."
        ) from exc

    root = Path(repo_path).resolve()
    if not root.is_dir():
        raise NotADirectoryError(f"Not a directory: {root}")

    logger.info("Scanning repository: %s", root)
    profile = analyze(root)
    logger.info(
        "Scan complete: %d component(s), monorepo=%s, %d findings, %d unknowns",
        len(profile.components), profile.is_monorepo,
        len(profile.findings), len(profile.unknowns),
    )

    # Aggregate top-level language / framework / db / port lists
    languages:  list[str] = list(dict.fromkeys(
        f.value.lower() for f in profile.findings if f.type == "language"))
    frameworks: list[str] = list(dict.fromkeys(
        f.value.lower() for f in profile.findings if f.type == "framework"))
    databases:  list[str] = list(dict.fromkeys(
        f.value.lower() for f in profile.findings if f.type in ("database", "cache", "queue")))
    ports: list[int] = sorted({
        int(f.value) for f in profile.findings if f.type == "port"
        and f.value.isdigit()
    })

    components_out = []
    for c in profile.components:
        components_out.append({
            "path":              c.path,
            "kind":              c.kind,
            "languages":         c.languages,
            "frameworks":        c.frameworks,
            "package_managers":  c.package_managers,
            "ports":             c.ports,
            "start_commands":    c.start_commands,
            "build_commands":    c.build_commands,
            "databases":         c.databases,
            "has_container_config": c.has_container_config,
        })

    coverage_out = {
        "files_scanned":  profile.coverage.files_scanned,
        "files_skipped":  profile.coverage.files_skipped,
        "bytes_read_kb":  round(profile.coverage.bytes_read / 1024, 1),
        "detectors_run":  profile.coverage.detectors_run,
        "detectors_failed": profile.coverage.detectors_failed,
        "limits_hit":     profile.coverage.limits_hit,
        "languages_without_framework_rules": profile.coverage.languages_without_framework_rules,
    }

    result: dict = {
        "status":             "SUCCESS",
        "repo_name":          profile.repo or root.name,
        "repo_path":          str(root),
        "commit_sha":         profile.commit_sha,
        "is_monorepo":        profile.is_monorepo,
        "components":         components_out,
        "languages_detected": languages,
        "frameworks_detected": frameworks,
        "databases_detected": databases,
        "ports_detected":     ports,
        "unknowns":           profile.unknowns,
        "conflicts":          profile.conflicts,
        "errors":             profile.errors,
        "coverage":           coverage_out,
        "findings_count":     len(profile.findings),
    }

    if include_findings:
        findings_out = []
        for f in profile.findings:
            findings_out.append({
                "id":         f.id,
                "type":       f.type,
                "value":      f.value,
                "status":     f.status,
                "component":  f.component,
                "limitations": f.limitations,
                "evidence":   [
                    {"file": e.file, "line": e.line, "detector": e.detector, "note": e.note}
                    for e in f.evidence
                ],
            })
        result["findings"] = findings_out

    return result
