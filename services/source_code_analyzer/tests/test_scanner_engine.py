from __future__ import annotations

import builtins

from app import scanner_engine


def test_missing_optional_pipeline_returns_explicit_partial_result(tmp_path, monkeypatch):
    real_import = builtins.__import__

    def import_without_optional_pipeline(name, *args, **kwargs):
        if name == "repo_analyzer.pipeline":
            raise ImportError("optional pipeline is not installed")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", import_without_optional_pipeline)
    monkeypatch.setattr(
        "app.universal_scanner.run_universal_scan",
        lambda root: {
            "repo_name": root.name,
            "languages": ["Python"],
            "frameworks": ["FastAPI"],
            "databases": [],
            "ports": [],
            "is_monorepo": False,
            "inspected_manifests": ["pyproject.toml"],
        },
    )

    result = scanner_engine.scan_repository(tmp_path, include_findings=True)

    assert result["status"] == "PARTIAL"
    assert result["languages_detected"] == ["Python"]
    assert result["ports_detected"] == []
    assert result["coverage"]["status"] == "NOT_MEASURED"
    assert "findings" in result
    assert result["findings"] == []
    assert "accuracy_score" not in result
