from app.universal_scanner import run_universal_scan


def test_empty_repository_does_not_receive_fabricated_ports(tmp_path):
    report = run_universal_scan(tmp_path)
    assert report["ports"] == []
    assert report["workload_type"] == "UNKNOWN / INSUFFICIENT_EVIDENCE"

def test_local_monorepo_dependency_inventory_is_bounded_and_scoped(tmp_path):
    from app.universal_scanner import run_universal_scan

    api = tmp_path / "apps" / "api"
    web = tmp_path / "apps" / "web"
    api.mkdir(parents=True)
    web.mkdir(parents=True)
    (api / "pyproject.toml").write_text(
        '[project]\ndependencies = ["fastapi==0.115.0"]\n',
        encoding="utf-8",
    )
    (web / "package.json").write_text(
        '{"dependencies":{"react":"18.2.0"}}',
        encoding="utf-8",
    )

    report = run_universal_scan(tmp_path)
    assert report["is_monorepo"] is True
    assert set(report["application_roots"]) == {"apps/api", "apps/web"}
    assert {item["package_name"] for item in report["dependencies_detected"]} == {
        "fastapi", "react"
    }
    assert report["dependency_count"] == 2
