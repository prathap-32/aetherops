# services/requirement_analysis/app/models.py
from sqlalchemy import Column, Integer, String, Float, UniqueConstraint
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

