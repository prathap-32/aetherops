# services/requirement_analysis/app/models.py
import json
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, UniqueConstraint, DateTime, Text, Boolean
from app.database import Base

class EC2Catalog(Base):
    __tablename__ = "ec2_catalog"

    id = Column(Integer, primary_key=True, index=True)
    instance_type = Column(String(50), unique=True, index=True, nullable=False)
    vcpus = Column(Integer, nullable=False)
    ram_gb = Column(Float, nullable=False)
    price_per_hour = Column(Float, nullable=False)
    network_performance = Column(String(100), nullable=False)
    category = Column(String(50), nullable=False)

    def to_dict(self):
        return {
            "instance_type": self.instance_type,
            "vcpus": self.vcpus,
            "ram_gb": self.ram_gb,
            "price_per_hour": self.price_per_hour,
            "network_performance": self.network_performance,
            "category": self.category
        }

class RDSCatalog(Base):
    __tablename__ = "rds_catalog"

    id = Column(Integer, primary_key=True, index=True)
    instance_type = Column(String(50), unique=True, index=True, nullable=False)
    vcpus = Column(Integer, nullable=False)
    ram_gb = Column(Float, nullable=False)
    price_per_hour = Column(Float, nullable=False)
    category = Column(String(50), nullable=False)

    def to_dict(self):
        return {
            "instance_type": self.instance_type,
            "vcpus": self.vcpus,
            "ram_gb": self.ram_gb,
            "price_per_hour": self.price_per_hour,
            "category": self.category
        }

class GenericServiceCatalog(Base):
    __tablename__ = "generic_service_catalog"

    id = Column(Integer, primary_key=True, index=True)
    service = Column(String(50), index=True, nullable=False)
    instance_type = Column(String(100), index=True, nullable=False)
    vcpus = Column(Integer, nullable=True, default=0)
    ram_gb = Column(Float, nullable=True, default=0.0)
    price_per_hour = Column(Float, nullable=False)
    unit = Column(String(50), nullable=True, default="Hrs")
    category = Column(String(50), nullable=False)
    region = Column(String(50), nullable=True, default="us-east-1")
    details = Column(String(500), nullable=True)

    __table_args__ = (
        UniqueConstraint('service', 'instance_type', name='_service_instance_uc'),
    )

    def to_dict(self):
        return {
            "instance_type": self.instance_type,
            "vcpus": self.vcpus,
            "ram_gb": self.ram_gb,
            "price_per_hour": self.price_per_hour,
            "category": self.category,
            "service": self.service,
            "unit": self.unit,
            "region": self.region,
            "details": self.details
        }

class SyncMetadata(Base):
    __tablename__ = "sync_metadata"

    id = Column(Integer, primary_key=True, index=True)
    region_code = Column(String(50), unique=True, index=True, nullable=False)
    last_sync_timestamp = Column(DateTime, nullable=False)
    status = Column(String(20), nullable=False)  # SUCCESS, FAILED, IN_PROGRESS
    records_synced = Column(Integer, nullable=False, default=0)
    ec2_count = Column(Integer, nullable=False, default=0)
    rds_count = Column(Integer, nullable=False, default=0)
    generic_count = Column(Integer, nullable=False, default=0)
    duration_ms = Column(Integer, nullable=False, default=0)
    error_message = Column(String(500), nullable=True)

    def to_dict(self):
        return {
            "region_code": self.region_code,
            "last_sync_timestamp": self.last_sync_timestamp.isoformat() if self.last_sync_timestamp else None,
            "status": self.status,
            "records_synced": self.records_synced,
            "ec2_count": self.ec2_count,
            "rds_count": self.rds_count,
            "generic_count": self.generic_count,
            "duration_ms": self.duration_ms,
            "error_message": self.error_message
        }


class RequirementProject(Base):
    """
    Dedicated Module 1 Domain Entity:
    Stores project requirements, architecture sizing specifications, service selection rationales ("Why That Service"),
    FinOps cost optimization strategies, and Module 2 dispatch state in local SQLite.
    """
    __tablename__ = "requirement_projects"

    id = Column(String(36), primary_key=True, index=True)
    project_name = Column(String(100), index=True, nullable=False)
    description = Column(String(500), nullable=True)
    stream = Column(String(50), nullable=False, default="web_application")
    target_region = Column(String(50), nullable=False, default="us-east-1")
    traffic_scale = Column(String(50), nullable=False, default="hobby_dev")
    reliability = Column(String(50), nullable=False, default="dev_testing")
    security_need = Column(String(50), nullable=False, default="standard")
    data_storage_gb = Column(Float, nullable=False, default=10.0)
    monthly_budget = Column(Float, nullable=True)

    # Input Preferences (JSON stringified)
    tech_stack = Column(Text, nullable=True)
    operations = Column(Text, nullable=True)
    monitoring = Column(Text, nullable=True)

    # Architecture Analysis Results
    architecture_tier = Column(String(50), nullable=False, default="Developer")
    estimated_monthly_cost = Column(Float, nullable=False, default=0.0)
    cost_breakdown = Column(Text, nullable=True)       # JSON: {"compute": ..., "database": ..., ...}
    service_rationales = Column(Text, nullable=True)   # JSON: {"compute": {"service": ..., "why": ...}, ...}
    cost_optimizations = Column(Text, nullable=True)   # JSON: [{"title": ..., "savings": ..., "detail": ...}]
    profile_output = Column(Text, nullable=True)       # JSON: Full RequirementProfileOutput

    status = Column(String(30), nullable=False, default="ANALYZED") # DRAFT, ANALYZED, DISPATCHED_TO_M2
    dispatched_to_m2 = Column(Boolean, default=False)
    m2_graph_summary = Column(Text, nullable=True)     # JSON: {"nodes": ..., "edges": ...}

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        def _parse(field):
            if not field:
                return {}
            try:
                return json.loads(field) if isinstance(field, str) else field
            except Exception:
                return {}

        def _parse_list(field):
            if not field:
                return []
            try:
                return json.loads(field) if isinstance(field, str) else field
            except Exception:
                return []

        return {
            "id": self.id,
            "project_name": self.project_name,
            "description": self.description,
            "stream": self.stream,
            "target_region": self.target_region,
            "traffic_scale": self.traffic_scale,
            "reliability": self.reliability,
            "security_need": self.security_need,
            "data_storage_gb": self.data_storage_gb,
            "monthly_budget": self.monthly_budget,
            "tech_stack": _parse(self.tech_stack),
            "operations": _parse(self.operations),
            "monitoring": _parse(self.monitoring),
            "architecture_tier": self.architecture_tier,
            "estimated_monthly_cost": self.estimated_monthly_cost,
            "cost_breakdown": _parse(self.cost_breakdown),
            "service_rationales": _parse(self.service_rationales),
            "cost_optimizations": _parse_list(self.cost_optimizations),
            "profile_output": _parse(self.profile_output),
            "status": self.status,
            "dispatched_to_m2": bool(self.dispatched_to_m2),
            "m2_graph_summary": _parse(self.m2_graph_summary),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


