# services/requirement_analysis/app/catalog.py
from typing import Dict, List, Optional
from pydantic import BaseModel

class EC2InstanceSpec(BaseModel):
    instance_type: str
    vcpus: int
    ram_gb: float
    price_per_hour: float
    network_performance: str  # e.g. "Up to 5 Gbps", "10 Gbps"
    category: str  # "burstable", "compute", "memory", "general"

class RDSInstanceSpec(BaseModel):
    instance_type: str
    vcpus: int
    ram_gb: float
    price_per_hour: float
    category: str  # "burstable", "standard", "memory"

# Real AWS EC2 catalog details (US East N. Virginia - us-east-1 Linux On-Demand)
EC2_CATALOG: List[EC2InstanceSpec] = [
    # General Purpose - Burstable (t3)
    EC2InstanceSpec(instance_type="t3.nano", vcpus=2, ram_gb=0.5, price_per_hour=0.0052, network_performance="Up to 5 Gbps", category="burstable"),
    EC2InstanceSpec(instance_type="t3.micro", vcpus=2, ram_gb=1.0, price_per_hour=0.0104, network_performance="Up to 5 Gbps", category="burstable"),
    EC2InstanceSpec(instance_type="t3.small", vcpus=2, ram_gb=2.0, price_per_hour=0.0208, network_performance="Up to 5 Gbps", category="burstable"),
    EC2InstanceSpec(instance_type="t3.medium", vcpus=2, ram_gb=4.0, price_per_hour=0.0416, network_performance="Up to 5 Gbps", category="burstable"),
    EC2InstanceSpec(instance_type="t3.large", vcpus=2, ram_gb=8.0, price_per_hour=0.0832, network_performance="Up to 5 Gbps", category="burstable"),
    EC2InstanceSpec(instance_type="t3.xlarge", vcpus=4, ram_gb=16.0, price_per_hour=0.1664, network_performance="Up to 5 Gbps", category="burstable"),
    EC2InstanceSpec(instance_type="t3.2xlarge", vcpus=8, ram_gb=32.0, price_per_hour=0.3328, network_performance="Up to 5 Gbps", category="burstable"),

    # General Purpose - Graviton Burstable (t4g)
    EC2InstanceSpec(instance_type="t4g.nano", vcpus=2, ram_gb=0.5, price_per_hour=0.0042, network_performance="Up to 5 Gbps", category="burstable"),
    EC2InstanceSpec(instance_type="t4g.micro", vcpus=2, ram_gb=1.0, price_per_hour=0.0084, network_performance="Up to 5 Gbps", category="burstable"),
    EC2InstanceSpec(instance_type="t4g.small", vcpus=2, ram_gb=2.0, price_per_hour=0.0168, network_performance="Up to 5 Gbps", category="burstable"),
    EC2InstanceSpec(instance_type="t4g.medium", vcpus=2, ram_gb=4.0, price_per_hour=0.0336, network_performance="Up to 5 Gbps", category="burstable"),
    EC2InstanceSpec(instance_type="t4g.large", vcpus=2, ram_gb=8.0, price_per_hour=0.0672, network_performance="Up to 5 Gbps", category="burstable"),
    EC2InstanceSpec(instance_type="t4g.xlarge", vcpus=4, ram_gb=16.0, price_per_hour=0.1344, network_performance="Up to 5 Gbps", category="burstable"),
    EC2InstanceSpec(instance_type="t4g.2xlarge", vcpus=8, ram_gb=32.0, price_per_hour=0.2688, network_performance="Up to 5 Gbps", category="burstable"),

    # General Purpose - Intel (m6i)
    EC2InstanceSpec(instance_type="m6i.large", vcpus=2, ram_gb=8.0, price_per_hour=0.096, network_performance="Up to 12.5 Gbps", category="general"),
    EC2InstanceSpec(instance_type="m6i.xlarge", vcpus=4, ram_gb=16.0, price_per_hour=0.192, network_performance="Up to 12.5 Gbps", category="general"),
    EC2InstanceSpec(instance_type="m6i.2xlarge", vcpus=8, ram_gb=32.0, price_per_hour=0.384, network_performance="Up to 12.5 Gbps", category="general"),
    EC2InstanceSpec(instance_type="m6i.4xlarge", vcpus=16, ram_gb=64.0, price_per_hour=0.768, network_performance="Up to 12.5 Gbps", category="general"),

    # General Purpose - Graviton (m6g)
    EC2InstanceSpec(instance_type="m6g.medium", vcpus=1, ram_gb=4.0, price_per_hour=0.0385, network_performance="Up to 10 Gbps", category="general"),
    EC2InstanceSpec(instance_type="m6g.large", vcpus=2, ram_gb=8.0, price_per_hour=0.077, network_performance="Up to 10 Gbps", category="general"),
    EC2InstanceSpec(instance_type="m6g.xlarge", vcpus=4, ram_gb=16.0, price_per_hour=0.154, network_performance="Up to 10 Gbps", category="general"),
    EC2InstanceSpec(instance_type="m6g.2xlarge", vcpus=8, ram_gb=32.0, price_per_hour=0.308, network_performance="Up to 10 Gbps", category="general"),
    EC2InstanceSpec(instance_type="m6g.4xlarge", vcpus=16, ram_gb=64.0, price_per_hour=0.616, network_performance="Up to 10 Gbps", category="general"),

    # Compute Optimized - Intel (c6i)
    EC2InstanceSpec(instance_type="c6i.large", vcpus=2, ram_gb=4.0, price_per_hour=0.085, network_performance="Up to 12.5 Gbps", category="compute"),
    EC2InstanceSpec(instance_type="c6i.xlarge", vcpus=4, ram_gb=8.0, price_per_hour=0.170, network_performance="Up to 12.5 Gbps", category="compute"),
    EC2InstanceSpec(instance_type="c6i.2xlarge", vcpus=8, ram_gb=16.0, price_per_hour=0.340, network_performance="Up to 12.5 Gbps", category="compute"),
    EC2InstanceSpec(instance_type="c6i.4xlarge", vcpus=16, ram_gb=32.0, price_per_hour=0.680, network_performance="Up to 12.5 Gbps", category="compute"),

    # Compute Optimized - Graviton (c6g)
    EC2InstanceSpec(instance_type="c6g.medium", vcpus=1, ram_gb=2.0, price_per_hour=0.034, network_performance="Up to 10 Gbps", category="compute"),
    EC2InstanceSpec(instance_type="c6g.large", vcpus=2, ram_gb=4.0, price_per_hour=0.068, network_performance="Up to 10 Gbps", category="compute"),
    EC2InstanceSpec(instance_type="c6g.xlarge", vcpus=4, ram_gb=8.0, price_per_hour=0.136, network_performance="Up to 10 Gbps", category="compute"),
    EC2InstanceSpec(instance_type="c6g.2xlarge", vcpus=8, ram_gb=16.0, price_per_hour=0.272, network_performance="Up to 10 Gbps", category="compute"),

    # Memory Optimized - Intel (r6i)
    EC2InstanceSpec(instance_type="r6i.large", vcpus=2, ram_gb=16.0, price_per_hour=0.126, network_performance="Up to 12.5 Gbps", category="memory"),
    EC2InstanceSpec(instance_type="r6i.xlarge", vcpus=4, ram_gb=32.0, price_per_hour=0.252, network_performance="Up to 12.5 Gbps", category="memory"),
    EC2InstanceSpec(instance_type="r6i.2xlarge", vcpus=8, ram_gb=64.0, price_per_hour=0.504, network_performance="Up to 12.5 Gbps", category="memory"),
    EC2InstanceSpec(instance_type="r6i.4xlarge", vcpus=16, ram_gb=128.0, price_per_hour=1.008, network_performance="Up to 12.5 Gbps", category="memory"),

    # Memory Optimized - Graviton (r6g)
    EC2InstanceSpec(instance_type="r6g.medium", vcpus=1, ram_gb=8.0, price_per_hour=0.0504, network_performance="Up to 10 Gbps", category="memory"),
    EC2InstanceSpec(instance_type="r6g.large", vcpus=2, ram_gb=16.0, price_per_hour=0.1008, network_performance="Up to 10 Gbps", category="memory"),
    EC2InstanceSpec(instance_type="r6g.xlarge", vcpus=4, ram_gb=32.0, price_per_hour=0.2016, network_performance="Up to 10 Gbps", category="memory"),
    EC2InstanceSpec(instance_type="r6g.2xlarge", vcpus=8, ram_gb=64.0, price_per_hour=0.4032, network_performance="Up to 10 Gbps", category="memory"),

    # Accelerated Computing / GPU
    EC2InstanceSpec(instance_type="g4dn.xlarge", vcpus=4, ram_gb=16.0, price_per_hour=0.526, network_performance="Up to 25 Gbps", category="gpu"),
    EC2InstanceSpec(instance_type="g4dn.2xlarge", vcpus=8, ram_gb=32.0, price_per_hour=0.752, network_performance="Up to 25 Gbps", category="gpu"),
]


# Real AWS RDS (PostgreSQL/MySQL Single-AZ On-Demand)
RDS_CATALOG: List[RDSInstanceSpec] = [
    # Burstable Graviton (db.t4g)
    RDSInstanceSpec(instance_type="db.t4g.micro", vcpus=2, ram_gb=1.0, price_per_hour=0.016, category="burstable"),
    RDSInstanceSpec(instance_type="db.t4g.small", vcpus=2, ram_gb=2.0, price_per_hour=0.032, category="burstable"),
    RDSInstanceSpec(instance_type="db.t4g.medium", vcpus=2, ram_gb=4.0, price_per_hour=0.064, category="burstable"),
    RDSInstanceSpec(instance_type="db.t4g.large", vcpus=2, ram_gb=8.0, price_per_hour=0.128, category="burstable"),
    RDSInstanceSpec(instance_type="db.t4g.xlarge", vcpus=4, ram_gb=16.0, price_per_hour=0.256, category="burstable"),

    # Burstable Intel (db.t3)
    RDSInstanceSpec(instance_type="db.t3.micro", vcpus=2, ram_gb=1.0, price_per_hour=0.017, category="burstable"),
    RDSInstanceSpec(instance_type="db.t3.small", vcpus=2, ram_gb=2.0, price_per_hour=0.034, category="burstable"),
    RDSInstanceSpec(instance_type="db.t3.medium", vcpus=2, ram_gb=4.0, price_per_hour=0.068, category="burstable"),
    RDSInstanceSpec(instance_type="db.t3.large", vcpus=2, ram_gb=8.0, price_per_hour=0.136, category="burstable"),
    RDSInstanceSpec(instance_type="db.t3.xlarge", vcpus=4, ram_gb=16.0, price_per_hour=0.272, category="burstable"),

    # Standard Graviton (db.m6g)
    RDSInstanceSpec(instance_type="db.m6g.large", vcpus=2, ram_gb=8.0, price_per_hour=0.182, category="standard"),
    RDSInstanceSpec(instance_type="db.m6g.xlarge", vcpus=4, ram_gb=16.0, price_per_hour=0.364, category="standard"),
    RDSInstanceSpec(instance_type="db.m6g.2xlarge", vcpus=8, ram_gb=32.0, price_per_hour=0.728, category="standard"),
    RDSInstanceSpec(instance_type="db.m6g.4xlarge", vcpus=16, ram_gb=64.0, price_per_hour=1.456, category="standard"),

    # Standard Intel (db.m6i)
    RDSInstanceSpec(instance_type="db.m6i.large", vcpus=2, ram_gb=8.0, price_per_hour=0.200, category="standard"),
    RDSInstanceSpec(instance_type="db.m6i.xlarge", vcpus=4, ram_gb=16.0, price_per_hour=0.400, category="standard"),
    RDSInstanceSpec(instance_type="db.m6i.2xlarge", vcpus=8, ram_gb=32.0, price_per_hour=0.800, category="standard"),

    # Memory Graviton (db.r6g)
    RDSInstanceSpec(instance_type="db.r6g.large", vcpus=2, ram_gb=16.0, price_per_hour=0.240, category="memory"),
    RDSInstanceSpec(instance_type="db.r6g.xlarge", vcpus=4, ram_gb=32.0, price_per_hour=0.480, category="memory"),
    RDSInstanceSpec(instance_type="db.r6g.2xlarge", vcpus=8, ram_gb=64.0, price_per_hour=0.960, category="memory"),
    RDSInstanceSpec(instance_type="db.r6g.4xlarge", vcpus=16, ram_gb=128.0, price_per_hour=1.920, category="memory"),

    # Memory Intel (db.r6i)
    RDSInstanceSpec(instance_type="db.r6i.large", vcpus=2, ram_gb=16.0, price_per_hour=0.264, category="memory"),
    RDSInstanceSpec(instance_type="db.r6i.xlarge", vcpus=4, ram_gb=32.0, price_per_hour=0.528, category="memory"),
    RDSInstanceSpec(instance_type="db.r6i.2xlarge", vcpus=8, ram_gb=64.0, price_per_hour=1.056, category="memory"),
]

# Pricing for storage per GB per month (US East N. Virginia)
STORAGE_PRICING: Dict[str, float] = {
    "ebs_gp3_gb_per_month": 0.08,
    "rds_gp3_gb_per_month": 0.115,
    "s3_standard_gb_per_month": 0.023,
    "s3_glacier_gb_per_month": 0.0036,
}

# General static monthly cost allocations (base charges)
NETWORK_PRICING: Dict[str, float] = {
    "alb_per_hour": 0.0225,          # ~$16.20/month flat base
    "nat_gateway_per_hour": 0.045,   # ~$32.40/month flat base per NAT GW
    "vpn_connection_per_hour": 0.05, # ~$36.00/month flat base
    "data_transfer_out_per_gb": 0.09,
    "cloudfront_out_per_gb": 0.085,
}

def get_cheapest_ec2_matching(min_vcpus: int, min_ram_gb: float, category_preference: Optional[str] = None) -> Optional[EC2InstanceSpec]:
    """
    Finds the cheapest EC2 instance satisfying minimum vCPU and RAM constraints.
    """
    candidates = [
        spec for spec in EC2_CATALOG 
        if spec.vcpus >= min_vcpus and spec.ram_gb >= min_ram_gb
    ]
    if not candidates:
        return None
    
    if category_preference:
        pref_candidates = [spec for spec in candidates if spec.category == category_preference]
        if pref_candidates:
            return min(pref_candidates, key=lambda x: x.price_per_hour)
            
    return min(candidates, key=lambda x: x.price_per_hour)

def get_cheapest_rds_matching(min_vcpus: int, min_ram_gb: float, category_preference: Optional[str] = None) -> Optional[RDSInstanceSpec]:
    """
    Finds the cheapest RDS instance satisfying minimum vCPU and RAM constraints.
    """
    candidates = [
        spec for spec in RDS_CATALOG
        if spec.vcpus >= min_vcpus and spec.ram_gb >= min_ram_gb
    ]
    if not candidates:
        return None
    
    if category_preference:
        pref_candidates = [spec for spec in candidates if spec.category == category_preference]
        if pref_candidates:
            return min(pref_candidates, key=lambda x: x.price_per_hour)
            
    return min(candidates, key=lambda x: x.price_per_hour)
