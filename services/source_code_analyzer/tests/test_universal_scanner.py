from app.universal_scanner import run_universal_scan


def test_empty_repository_does_not_receive_fabricated_ports(tmp_path):
    report = run_universal_scan(tmp_path)
    assert report["ports"] == []
    assert report["workload_type"] == "UNKNOWN / INSUFFICIENT_EVIDENCE"
