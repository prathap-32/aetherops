# services/requirement_analysis/app/models.py
from sqlalchemy import Column, Integer, String, Float, UniqueConstraint, DateTime
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

