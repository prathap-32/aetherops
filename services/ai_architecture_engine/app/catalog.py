from typing import List, Dict, Any
from pydantic import BaseModel

class EC2InstanceSpec(BaseModel):
    instance_type: str
    vcpus: int
    ram_gb: float
    price_per_hour: float
    network_performance: str
    category: str

class RDSInstanceSpec(BaseModel):
    instance_type: str
    vcpus: int
    ram_gb: float
    price_per_hour: float
    category: str

EC2_CATALOG: List[EC2InstanceSpec] = [
    EC2InstanceSpec(instance_type="t3.nano", vcpus=2, ram_gb=0.5, price_per_hour=0.0052, network_performance="Up to 5 Gbps", category="burstable"),
    EC2InstanceSpec(instance_type="t3.micro", vcpus=2, ram_gb=1.0, price_per_hour=0.0104, network_performance="Up to 5 Gbps", category="burstable"),
    EC2InstanceSpec(instance_type="t3.small", vcpus=2, ram_gb=2.0, price_per_hour=0.0208, network_performance="Up to 5 Gbps", category="burstable"),
    EC2InstanceSpec(instance_type="t3.medium", vcpus=2, ram_gb=4.0, price_per_hour=0.0416, network_performance="Up to 5 Gbps", category="burstable"),
    EC2InstanceSpec(instance_type="t3.large", vcpus=2, ram_gb=8.0, price_per_hour=0.0832, network_performance="Up to 5 Gbps", category="burstable"),
    EC2InstanceSpec(instance_type="t3.xlarge", vcpus=4, ram_gb=16.0, price_per_hour=0.1664, network_performance="Up to 5 Gbps", category="burstable"),
    EC2InstanceSpec(instance_type="t4g.micro", vcpus=2, ram_gb=1.0, price_per_hour=0.0084, network_performance="Up to 5 Gbps", category="burstable"),
    EC2InstanceSpec(instance_type="t4g.small", vcpus=2, ram_gb=2.0, price_per_hour=0.0168, network_performance="Up to 5 Gbps", category="burstable"),
    EC2InstanceSpec(instance_type="t4g.medium", vcpus=2, ram_gb=4.0, price_per_hour=0.0336, network_performance="Up to 5 Gbps", category="burstable"),
    EC2InstanceSpec(instance_type="m6i.large", vcpus=2, ram_gb=8.0, price_per_hour=0.096, network_performance="Up to 12.5 Gbps", category="general"),
    EC2InstanceSpec(instance_type="c6i.large", vcpus=2, ram_gb=4.0, price_per_hour=0.085, network_performance="Up to 12.5 Gbps", category="compute"),
]

RDS_CATALOG: List[RDSInstanceSpec] = [
    RDSInstanceSpec(instance_type="db.t3.micro", vcpus=2, ram_gb=1.0, price_per_hour=0.017, category="burstable"),
    RDSInstanceSpec(instance_type="db.t3.small", vcpus=2, ram_gb=2.0, price_per_hour=0.034, category="burstable"),
    RDSInstanceSpec(instance_type="db.t3.medium", vcpus=2, ram_gb=4.0, price_per_hour=0.068, category="burstable"),
    RDSInstanceSpec(instance_type="db.t4g.micro", vcpus=2, ram_gb=1.0, price_per_hour=0.014, category="burstable"),
    RDSInstanceSpec(instance_type="db.t4g.small", vcpus=2, ram_gb=2.0, price_per_hour=0.028, category="burstable"),
    RDSInstanceSpec(instance_type="db.m6i.large", vcpus=2, ram_gb=8.0, price_per_hour=0.176, category="standard"),
]
