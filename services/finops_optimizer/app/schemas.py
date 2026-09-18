# services/finops_optimizer/app/schemas.py
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class FinOpsOptimizationRequest(BaseModel):
    project_name: str = Field(default="workload-finops")
    monthly_on_demand_compute: float = Field(..., ge=0.0)
    monthly_on_demand_rds: float = Field(..., ge=0.0)
    monthly_storage_and_network: float = Field(default=0.0, ge=0.0)
    current_instance_family: str = Field(default="t3")
    is_development: bool = Field(default=False)

class SavingsOpportunity(BaseModel):
    name: str
    category: str
    monthly_savings: float
    savings_percentage: str
    implementation_complexity: str  # LOW, MEDIUM, HIGH
    description: str

class TCOForecast(BaseModel):
    on_demand_1_year: float
    optimized_1_year: float
    net_1_year_savings: float
    on_demand_3_year: float
    optimized_3_year: float
    net_3_year_savings: float

class FinOpsOptimizationResponse(BaseModel):
    status: str
    project_name: str
    baseline_monthly_spend: float
    optimized_monthly_spend: float
    total_monthly_savings: float
    savings_opportunities: List[SavingsOpportunity]
    tco_projection: TCOForecast
