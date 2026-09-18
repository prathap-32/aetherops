# services/finops_optimizer/app/finops_engine.py
from typing import List
from app.schemas import FinOpsOptimizationRequest, FinOpsOptimizationResponse, SavingsOpportunity, TCOForecast

def calculate_finops_optimizations(req: FinOpsOptimizationRequest) -> FinOpsOptimizationResponse:
    """
    Computes rigorous FinOps cost arbitrage, Reserved Instance & Savings Plans calculations,
    and 1-to-3 year TCO models.
    """
    baseline_spend = req.monthly_on_demand_compute + req.monthly_on_demand_rds + req.monthly_storage_and_network
    opportunities: List[SavingsOpportunity] = []
    total_savings = 0.0

    # 1. 1-Year or 3-Year Compute Savings Plans (34% savings on EC2 baseline)
    if req.monthly_on_demand_compute > 20.0:
        sp_savings = round(req.monthly_on_demand_compute * 0.34, 2)
        total_savings += sp_savings
        opportunities.append(SavingsOpportunity(
            name="1-Year No-Upfront Compute Savings Plan",
            category="Commitment Optimization",
            monthly_savings=sp_savings,
            savings_percentage="34% Savings",
            implementation_complexity="LOW",
            description="Commit to hourly compute rate baseline without instance family lock-in."
        ))

    # 2. Graviton Migration (20% savings)
    if req.current_instance_family in ["t3", "m5", "c5", "r5"]:
        graviton_savings = round(req.monthly_on_demand_compute * 0.20, 2)
        total_savings += graviton_savings
        opportunities.append(SavingsOpportunity(
            name="ARM64 Graviton Migration",
            category="Architectural Modernization",
            monthly_savings=graviton_savings,
            savings_percentage="20% Savings",
            implementation_complexity="MEDIUM",
            description=f"Transition from {req.current_instance_family} x86 to Graviton t4g/m7g/c7g equivalents."
        ))

    # 3. Off-Hours Automation for Non-Prod (65% compute + db savings)
    if req.is_development:
        off_hours_savings = round((req.monthly_on_demand_compute + req.monthly_on_demand_rds) * 0.65, 2)
        total_savings += off_hours_savings
        opportunities.append(SavingsOpportunity(
            name="Automated Non-Prod Night/Weekend Shutdown",
            category="Resource Lifecycle Governance",
            monthly_savings=off_hours_savings,
            savings_percentage="65% Non-Prod Savings",
            implementation_complexity="LOW",
            description="Turn off development instances outside 09:00 - 18:00 M-F using AWS Instance Scheduler."
        ))

    # 4. S3 Intelligent-Tiering and GP3 Volume Transition
    storage_savings = round(req.monthly_storage_and_network * 0.15, 2)
    if storage_savings > 1.0:
        total_savings += storage_savings
        opportunities.append(SavingsOpportunity(
            name="Storage Class Optimization (S3 Intelligent-Tiering)",
            category="Storage Optimization",
            monthly_savings=storage_savings,
            savings_percentage="15% Storage Savings",
            implementation_complexity="LOW",
            description="Eliminate manual archive scripting by letting AWS automatically tier cold blobs."
        ))

    optimized_spend = max(5.0, round(baseline_spend - total_savings, 2))
    net_monthly_savings = round(baseline_spend - optimized_spend, 2)

    tco = TCOForecast(
        on_demand_1_year=round(baseline_spend * 12, 2),
        optimized_1_year=round(optimized_spend * 12, 2),
        net_1_year_savings=round(net_monthly_savings * 12, 2),
        on_demand_3_year=round(baseline_spend * 36, 2),
        optimized_3_year=round(optimized_spend * 36, 2),
        net_3_year_savings=round(net_monthly_savings * 36, 2)
    )

    return FinOpsOptimizationResponse(
        status="SUCCESS",
        project_name=req.project_name,
        baseline_monthly_spend=round(baseline_spend, 2),
        optimized_monthly_spend=optimized_spend,
        total_monthly_savings=net_monthly_savings,
        savings_opportunities=opportunities,
        tco_projection=tco
    )
