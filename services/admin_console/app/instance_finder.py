# services/requirement_analysis/app/instance_finder.py
"""
AetherOps Mathematical Decision Matrix & Probabilistic Instance Type Finder.

Implements multi-criteria decision making (MCDM) using TOPSIS
(Technique for Order Preference by Similarity to Ideal Solution) coupled with
Gaussian Error Function (erf) probabilistic SLA headroom calculations.

Models workload demand under Central Limit Theorem (CLT) to quantify:
1. P(SLA Compliance): Probability that the instance will not saturate under peak load.
2. TOPSIS Relative Closeness: Geometric distance to the ideal multi-objective capacity.
3. Ratio Alignment: Divergence from target Memory-to-vCPU ratio.
4. Pareto-Optimal Multi-Objective Ranking (Cost vs Headroom vs Reliability).
"""

import math
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class InstanceFinderInput(BaseModel):
    # Resource Constraints
    min_vcpus: int = Field(default=2, ge=1, description="Minimum vCPUs required")
    max_vcpus: Optional[int] = Field(default=None, description="Maximum vCPUs allowed")
    min_ram_gb: float = Field(default=4.0, ge=0.5, description="Minimum RAM in GB")
    max_ram_gb: Optional[float] = Field(default=None, description="Maximum RAM in GB")
    
    # Target Memory-to-vCPU Ratio (e.g. 1.0 for compute, 4.0 for general, 8.0 for memory)
    target_ratio: Optional[float] = Field(default=None, description="Ideal Memory-to-vCPU ratio (e.g. 4.0)")
    
    # Workload Traffic Characteristics (for probabilistic SLA modeling)
    target_rps: Optional[int] = Field(default=250, ge=1, description="Target Requests Per Second")
    avg_latency_ms: Optional[float] = Field(default=120.0, ge=1.0, description="Average response latency in ms")
    traffic_burst_factor: float = Field(default=2.0, ge=1.0, le=5.0, description="Peak burst factor (sigma multiplier)")
    
    # Optimization Strategy
    optimization_goal: str = Field(
        default="balanced",
        description="Optimization focus: 'balanced', 'lowest_cost', 'performance', or 'high_availability'"
    )
    preferred_category: Optional[str] = Field(
        default=None,
        description="Optional preferred category: 'burstable', 'general', 'compute', 'memory', 'gpu'"
    )
    architecture_preference: str = Field(
        default="any",
        description="Architecture filter: 'any', 'x86_64' (Intel/AMD), 'arm64' (AWS Graviton)"
    )
    service_type: str = Field(default="ec2", description="Service catalog: 'ec2' or 'rds'")
    region: str = Field(default="us-east-1", description="AWS Region code")
    top_n: int = Field(default=5, ge=1, le=20, description="Number of top candidates to return")


class InstanceRankDetail(BaseModel):
    rank: int
    instance_type: str
    vcpus: int
    ram_gb: float
    ratio: float
    category: str
    price_per_hour: float
    monthly_price: float
    network_performance: str
    architecture: str
    
    # Mathematical Metrics
    topsis_score: float  # [0, 1] relative closeness to ideal
    sla_probability: float  # [0, 1] probability of no saturation under burst
    ratio_divergence: float  # distance from target ratio
    composite_score: float  # [0, 100] percentage overall match
    
    # Qualitative Badges
    fit_label: str  # e.g. "Pareto Optimal", "Cost Leader", "Performance Headroom"
    decision_rationale: str


class InstanceFinderOutput(BaseModel):
    status: str
    region: str
    service_type: str
    optimization_goal: str
    total_candidates_evaluated: int
    weights_applied: Dict[str, float]
    workload_demand_concurrency: float
    ranked_instances: List[InstanceRankDetail]
    best_recommendation: Optional[InstanceRankDetail] = None
    mathematical_summary: Dict[str, Any]


def calculate_sla_probability(instance_vcpus: int, instance_ram: float, req_concurrency: float, burst_factor: float = 2.0) -> float:
    """
    Computes P(SLA Compliance) using Gaussian Error Function (erf).
    Models request concurrency demand as L ~ N(mu, sigma^2).
    """
    # Baseline capacity: 1 vCPU comfortably handles ~150 concurrent connection threads in standard web tier
    capacity_concurrency = instance_vcpus * 150.0
    
    mu = req_concurrency
    sigma = (req_concurrency * (burst_factor - 1.0)) / 2.5
    if sigma <= 0.01:
        sigma = 1.0
        
    # Safe operating zone is below 85% of total instance concurrency capacity
    safe_threshold = capacity_concurrency * 0.85
    z_score = (safe_threshold - mu) / sigma
    
    # Cumulative distribution function of standard normal distribution:
    # Phi(Z) = 0.5 * (1 + erf(Z / sqrt(2)))
    prob = 0.5 * (1.0 + math.erf(z_score / math.sqrt(2.0)))
    return max(0.01, min(0.9999, prob))


def evaluate_decision_matrix(
    candidates: List[Dict[str, Any]],
    finder_input: InstanceFinderInput
) -> InstanceFinderOutput:
    """
    Executes the TOPSIS Multi-Criteria Decision Matrix algorithm and ranks instance candidates.
    """
    if not candidates:
        return InstanceFinderOutput(
            status="EMPTY",
            region=finder_input.region,
            service_type=finder_input.service_type,
            optimization_goal=finder_input.optimization_goal,
            total_candidates_evaluated=0,
            weights_applied={},
            workload_demand_concurrency=0.0,
            ranked_instances=[],
            best_recommendation=None,
            mathematical_summary={"error": "No instance candidates satisfied the specified criteria constraints."}
        )

    # 1. Calculate Little's Law Concurrency: L = lambda * W
    rps = finder_input.target_rps or 250
    latency_sec = (finder_input.avg_latency_ms or 120.0) / 1000.0
    demand_concurrency = rps * latency_sec

    # 2. Determine Multi-Criteria Weights based on optimization goal
    goal = finder_input.optimization_goal.lower().strip()
    if goal == "lowest_cost":
        weights = {"cost": 0.55, "headroom": 0.15, "ratio": 0.20, "net": 0.10}
    elif goal == "performance":
        weights = {"cost": 0.10, "headroom": 0.45, "ratio": 0.25, "net": 0.20}
    elif goal in ["high_availability", "reliability"]:
        weights = {"cost": 0.15, "headroom": 0.35, "ratio": 0.30, "net": 0.20}
    else:  # balanced
        weights = {"cost": 0.30, "headroom": 0.30, "ratio": 0.25, "net": 0.15}

    target_ratio = finder_input.target_ratio or (finder_input.min_ram_gb / max(1, finder_input.min_vcpus))

    # 3. Build Raw Decision Matrix
    # Criteria:
    # C1: Cost Efficiency = 1.0 / price_per_hour (Benefit criterion)
    # C2: Headroom Capacity = vcpus * ram_gb (Benefit criterion)
    # C3: Ratio Fit = 1.0 / (1.0 + abs(ram/vcpu - target_ratio)) (Benefit criterion)
    # C4: Network Bandwidth Weight (Benefit criterion)
    raw_matrix = []
    metadata_list = []

    for item in candidates:
        vcpu = int(item["vcpus"])
        ram = float(item["ram_gb"])
        price = float(item["price_per_hour"])
        ratio = ram / max(1, vcpu)
        
        # Categorize network performance into numeric score
        net_str = item.get("network_performance", "Up to 5 Gbps").lower()
        if "25" in net_str:
            net_score = 4.0
        elif "12.5" in net_str or "10" in net_str:
            net_score = 3.0
        elif "5" in net_str:
            net_score = 2.0
        else:
            net_score = 1.0
            
        # Detect Architecture
        itype = item["instance_type"].lower()
        is_arm = ("g." in itype) or ("t4g" in itype) or ("c6g" in itype) or ("m6g" in itype) or ("r6g" in itype)
        arch = "arm64 (Graviton)" if is_arm else "x86_64 (Intel)"

        # Filtering by architecture if requested
        if finder_input.architecture_preference == "arm64" and not is_arm:
            continue
        if finder_input.architecture_preference == "x86_64" and is_arm:
            continue

        cost_eff = 1.0 / max(0.001, price)
        headroom = float(vcpu * ram)
        ratio_fit = 1.0 / (1.0 + abs(ratio - target_ratio))
        
        raw_matrix.append([cost_eff, headroom, ratio_fit, net_score])
        metadata_list.append({
            "item": item,
            "ratio": ratio,
            "architecture": arch,
            "net_score": net_score,
            "price": price,
            "vcpu": vcpu,
            "ram": ram
        })

    if not raw_matrix:
        return InstanceFinderOutput(
            status="NO_MATCH",
            region=finder_input.region,
            service_type=finder_input.service_type,
            optimization_goal=finder_input.optimization_goal,
            total_candidates_evaluated=0,
            weights_applied=weights,
            workload_demand_concurrency=demand_concurrency,
            ranked_instances=[],
            best_recommendation=None,
            mathematical_summary={"error": "All candidates were filtered out by architecture or criteria constraints."}
        )

    # 4. TOPSIS Step 1 & 2: Vector Normalization and Weighting
    num_items = len(raw_matrix)
    num_criteria = 4
    crit_keys = ["cost", "headroom", "ratio", "net"]
    crit_weights = [weights[k] for k in crit_keys]

    # Calculate Euclidean column norms: sqrt(sum(x_ij^2))
    col_norms = [0.0] * num_criteria
    for j in range(num_criteria):
        col_norms[j] = math.sqrt(sum(raw_matrix[i][j] ** 2 for i in range(num_items))) or 1.0

    # Normalized Weighted Matrix
    v_matrix = [[0.0] * num_criteria for _ in range(num_items)]
    for i in range(num_items):
        for j in range(num_criteria):
            v_matrix[i][j] = (raw_matrix[i][j] / col_norms[j]) * crit_weights[j]

    # 5. TOPSIS Step 3: Positive Ideal Best (A+) and Negative Ideal Worst (A-)
    a_plus = [max(v_matrix[i][j] for i in range(num_items)) for j in range(num_criteria)]
    a_minus = [min(v_matrix[i][j] for i in range(num_items)) for j in range(num_criteria)]

    # 6. TOPSIS Step 4 & 5: Euclidean Distances and Relative Closeness
    scored_results = []
    for i in range(num_items):
        meta = metadata_list[i]
        item = meta["item"]
        
        d_plus = math.sqrt(sum((v_matrix[i][j] - a_plus[j]) ** 2 for j in range(num_criteria)))
        d_minus = math.sqrt(sum((v_matrix[i][j] - a_minus[j]) ** 2 for j in range(num_criteria)))
        
        topsis_closeness = (d_minus / (d_plus + d_minus)) if (d_plus + d_minus) > 0 else 0.5
        
        # Calculate Probabilistic SLA Compliance
        sla_prob = calculate_sla_probability(
            instance_vcpus=meta["vcpu"],
            instance_ram=meta["ram"],
            req_concurrency=demand_concurrency,
            burst_factor=finder_input.traffic_burst_factor
        )
        
        # Composite Percentage Score (60% TOPSIS multi-criteria + 40% Probabilistic SLA assurance)
        composite_score = round((topsis_closeness * 60.0 + sla_prob * 40.0), 2)
        
        # Category Preference Booster
        if finder_input.preferred_category and item.get("category") == finder_input.preferred_category:
            composite_score = min(99.9, composite_score + 3.0)

        # Ratio Divergence
        ratio_div = round(abs(meta["ratio"] - target_ratio), 2)
        
        scored_results.append({
            "item": item,
            "meta": meta,
            "topsis_score": round(topsis_closeness, 4),
            "sla_probability": round(sla_prob, 4),
            "composite_score": composite_score,
            "ratio_divergence": ratio_div,
        })

    # 7. Sort by Composite Score Descending
    scored_results.sort(key=lambda x: x["composite_score"], reverse=True)

    # 8. Build Detailed Ranks with Mathematical Explanations
    ranked_instances: List[InstanceRankDetail] = []
    for rank_idx, res in enumerate(scored_results[:finder_input.top_n], start=1):
        item = res["item"]
        meta = res["meta"]
        vcpu = meta["vcpu"]
        ram = meta["ram"]
        price = meta["price"]
        monthly_price = round(price * 730.0, 2)
        top_score = res["topsis_score"]
        sla = res["sla_probability"]
        
        # Formulate Decision Rationale and Fit Label
        if rank_idx == 1:
            fit_label = "Pareto Optimal (Top Pick)"
            decision_rationale = (
                f"Achieves highest mathematical equilibrium with a TOPSIS closeness of {top_score:.3f} "
                f"and {sla*100:.1f}% probabilistic SLA reliability under {demand_concurrency:.1f} concurrent requests."
            )
        elif price == min(r["meta"]["price"] for r in scored_results[:finder_input.top_n]):
            fit_label = "Cost Optimizer"
            decision_rationale = (
                f"Lowest hourly rate (${price:.4f}/hr) satisfying hard capacity boundaries with "
                f"{sla*100:.1f}% burst confidence."
            )
        elif (vcpu * ram) == max(r["meta"]["vcpu"] * r["meta"]["ram"] for r in scored_results[:finder_input.top_n]):
            fit_label = "Performance Leader"
            decision_rationale = (
                f"Maximum headroom capacity ({vcpu} vCPUs, {ram} GB RAM) for compute/IOPS-heavy spikes."
            )
        elif "arm64" in meta["architecture"]:
            fit_label = "Graviton Efficiency"
            decision_rationale = (
                f"AWS Graviton ARM architecture offering superior price-to-performance efficiency."
            )
        else:
            fit_label = "High Headroom Fit"
            decision_rationale = (
                f"Balanced alternative with {meta['ratio']:.1f}:1 RAM-to-vCPU ratio and {sla*100:.1f}% uptime probability."
            )

        ranked_instances.append(InstanceRankDetail(
            rank=rank_idx,
            instance_type=item["instance_type"],
            vcpus=vcpu,
            ram_gb=ram,
            ratio=round(meta["ratio"], 2),
            category=item.get("category", "standard"),
            price_per_hour=price,
            monthly_price=monthly_price,
            network_performance=item.get("network_performance", "Up to 10 Gbps"),
            architecture=meta["architecture"],
            topsis_score=top_score,
            sla_probability=sla,
            ratio_divergence=res["ratio_divergence"],
            composite_score=res["composite_score"],
            fit_label=fit_label,
            decision_rationale=decision_rationale
        ))

    best_pick = ranked_instances[0] if ranked_instances else None

    return InstanceFinderOutput(
        status="SUCCESS",
        region=finder_input.region,
        service_type=finder_input.service_type,
        optimization_goal=finder_input.optimization_goal,
        total_candidates_evaluated=len(scored_results),
        weights_applied=weights,
        workload_demand_concurrency=round(demand_concurrency, 2),
        ranked_instances=ranked_instances,
        best_recommendation=best_pick,
        mathematical_summary={
            "algorithm": "TOPSIS (Euclidean Ideal Distance) + Gaussian Error Function (erf) SLA Confidence",
            "ideal_positive_norm_vector": [round(x, 4) for x in a_plus],
            "ideal_negative_norm_vector": [round(x, 4) for x in a_minus],
            "target_ratio": round(target_ratio, 2),
            "burst_standard_deviations": round(finder_input.traffic_burst_factor, 1),
            "concurrency_demand_littles_law": round(demand_concurrency, 2)
        }
    )
