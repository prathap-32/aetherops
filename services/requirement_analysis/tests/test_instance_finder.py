# services/requirement_analysis/tests/test_instance_finder.py
import pytest
import math
from app.instance_finder import (
    InstanceFinderInput,
    InstanceFinderOutput,
    calculate_sla_probability,
    evaluate_decision_matrix
)
from app.catalog import EC2_CATALOG, RDS_CATALOG


def test_calculate_sla_probability():
    """
    Validates Gaussian Error Function erf probabilistic SLA calculation.
    """
    # 2 vCPUs gives 300 concurrency capacity (safe operating point: 255)
    # Low demand (10 concurrency) should yield near 100% SLA compliance
    prob_low = calculate_sla_probability(instance_vcpus=2, instance_ram=4.0, req_concurrency=10.0, burst_factor=2.0)
    assert prob_low > 0.99, f"Expected >99% confidence for light load, got {prob_low}"

    # Moderate demand (150 concurrency) under 2x burst
    prob_med = calculate_sla_probability(instance_vcpus=2, instance_ram=4.0, req_concurrency=150.0, burst_factor=2.0)
    assert 0.80 <= prob_med <= 0.99, f"Expected 80-99% confidence, got {prob_med}"

    # Extreme demand (400 concurrency) exceeding capacity (300)
    prob_high = calculate_sla_probability(instance_vcpus=2, instance_ram=4.0, req_concurrency=400.0, burst_factor=2.0)
    assert prob_high < 0.20, f"Expected low confidence for overloaded instance, got {prob_high}"


def test_topsis_decision_matrix_ec2_balanced():
    """
    Tests TOPSIS multi-criteria decision matrix on standard EC2 catalog with balanced goal.
    """
    candidates = [spec.model_dump() for spec in EC2_CATALOG if spec.vcpus >= 2 and spec.ram_gb >= 4.0]
    assert len(candidates) > 0

    inp = InstanceFinderInput(
        min_vcpus=2,
        min_ram_gb=4.0,
        target_ratio=4.0,
        optimization_goal="balanced",
        target_rps=200,
        avg_latency_ms=100.0,
        traffic_burst_factor=2.0,
        architecture_preference="any",
        service_type="ec2",
        top_n=5
    )

    output = evaluate_decision_matrix(candidates, inp)

    assert output.status == "SUCCESS"
    assert output.total_candidates_evaluated > 0
    assert len(output.ranked_instances) <= 5
    assert output.best_recommendation is not None
    assert output.best_recommendation.rank == 1

    # Check that TOPSIS score and SLA probability are bounded in [0, 1]
    for r in output.ranked_instances:
        assert 0.0 <= r.topsis_score <= 1.0
        assert 0.0 <= r.sla_probability <= 1.0
        assert 0.0 <= r.composite_score <= 100.0

    # Ensure ranked descending by composite score
    scores = [r.composite_score for r in output.ranked_instances]
    assert scores == sorted(scores, reverse=True)


def test_topsis_optimization_goals():
    """
    Verifies that changing the optimization goal shifts the weights and preference:
    - 'lowest_cost' prioritizes cheaper instances (high cost weight).
    - 'performance' prioritizes larger instances with higher headroom.
    """
    candidates = [spec.model_dump() for spec in EC2_CATALOG if spec.vcpus >= 2 and spec.ram_gb >= 4.0]

    # Lowest Cost
    inp_cost = InstanceFinderInput(
        min_vcpus=2,
        min_ram_gb=4.0,
        optimization_goal="lowest_cost",
        top_n=3
    )
    out_cost = evaluate_decision_matrix(candidates, inp_cost)
    assert out_cost.weights_applied["cost"] > out_cost.weights_applied["headroom"]
    top_cost_pick = out_cost.best_recommendation
    assert top_cost_pick is not None

    # Performance
    inp_perf = InstanceFinderInput(
        min_vcpus=2,
        min_ram_gb=4.0,
        optimization_goal="performance",
        top_n=3
    )
    out_perf = evaluate_decision_matrix(candidates, inp_perf)
    assert out_perf.weights_applied["headroom"] > out_perf.weights_applied["cost"]
    top_perf_pick = out_perf.best_recommendation
    assert top_perf_pick is not None

    # Performance pick should have equal or greater compute/headroom than lowest cost pick
    cost_capacity = top_cost_pick.vcpus * top_cost_pick.ram_gb
    perf_capacity = top_perf_pick.vcpus * top_perf_pick.ram_gb
    assert perf_capacity >= cost_capacity


def test_architecture_filtering():
    """
    Verifies Graviton (arm64) vs Intel/AMD (x86_64) hardware filtering.
    """
    candidates = [spec.model_dump() for spec in EC2_CATALOG]

    # arm64 filter
    inp_arm = InstanceFinderInput(
        min_vcpus=2,
        min_ram_gb=4.0,
        architecture_preference="arm64",
        top_n=5
    )
    out_arm = evaluate_decision_matrix(candidates, inp_arm)
    for r in out_arm.ranked_instances:
        assert "arm64" in r.architecture.lower() or "graviton" in r.architecture.lower()

    # x86_64 filter
    inp_x86 = InstanceFinderInput(
        min_vcpus=2,
        min_ram_gb=4.0,
        architecture_preference="x86_64",
        top_n=5
    )
    out_x86 = evaluate_decision_matrix(candidates, inp_x86)
    for r in out_x86.ranked_instances:
        assert "x86_64" in r.architecture.lower() or "intel" in r.architecture.lower()


def test_rds_decision_matrix():
    """
    Verifies instance finder evaluation on RDS database instances.
    """
    candidates = [spec.model_dump() for spec in RDS_CATALOG if spec.vcpus >= 2 and spec.ram_gb >= 4.0]
    inp = InstanceFinderInput(
        min_vcpus=2,
        min_ram_gb=4.0,
        service_type="rds",
        optimization_goal="balanced",
        top_n=4
    )
    out = evaluate_decision_matrix(candidates, inp)
    assert out.status == "SUCCESS"
    assert len(out.ranked_instances) > 0
    assert out.best_recommendation is not None
    assert "db." in out.best_recommendation.instance_type


def test_empty_candidates_handling():
    """
    Verifies graceful handling when no candidates satisfy extreme constraints.
    """
    candidates = []
    inp = InstanceFinderInput(min_vcpus=999, min_ram_gb=9999.0)
    out = evaluate_decision_matrix(candidates, inp)
    assert out.status == "EMPTY"
    assert len(out.ranked_instances) == 0
    assert out.best_recommendation is None


def test_instance_finder_api_endpoint():
    """
    Tests the FastAPI HTTP endpoint POST /api/v1/instance-finder/evaluate.
    """
    from fastapi.testclient import TestClient
    from app.main import app

    client = TestClient(app)
    payload = {
        "min_vcpus": 2,
        "min_ram_gb": 4.0,
        "target_ratio": 4.0,
        "optimization_goal": "balanced",
        "target_rps": 250,
        "avg_latency_ms": 120.0,
        "traffic_burst_factor": 2.0,
        "architecture_preference": "any",
        "service_type": "ec2",
        "region": "us-east-1",
        "top_n": 5
    }
    res = client.post("/api/v1/instance-finder/evaluate", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "SUCCESS"
    assert len(data["ranked_instances"]) > 0
    assert data["best_recommendation"] is not None
    assert "topsis_score" in data["ranked_instances"][0]
    assert "sla_probability" in data["ranked_instances"][0]
    assert "composite_score" in data["ranked_instances"][0]
    assert "mathematical_summary" in data

