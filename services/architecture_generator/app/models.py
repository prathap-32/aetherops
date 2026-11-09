# services/architecture_generator/app/models.py
import datetime
from sqlalchemy import Column, String, Text, Boolean, Float, DateTime
from app.database import Base

class ArchitectureVersionModel(Base):
    __tablename__ = "architecture_versions"

    version_id       = Column(String(100), primary_key=True, index=True)
    project_id       = Column(String(100), index=True, default="default")
    environment_id   = Column(String(100), index=True, default="env")
    environment_tier = Column(String(50), default="development")
    target_region    = Column(String(50), default="us-east-1")
    nodes            = Column(Text, nullable=True) # JSON string
    edges            = Column(Text, nullable=True) # JSON string
    status           = Column(String(50), default="DRAFT")
    is_approved      = Column(Boolean, default=False)
    approval_id      = Column(String(100), nullable=True)
    approved_by      = Column(String(100), nullable=True)
    approved_at      = Column(Float, nullable=True)
    tenant_id        = Column(String(50), index=True, default="ten_default")
    user_id          = Column(String(100), index=True, default="usr_default")
    created_at       = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at       = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

class StudioSessionModel(Base):
    __tablename__ = "studio_sessions"

    session_id       = Column(String(100), primary_key=True, index=True)
    tenant_id        = Column(String(50), index=True, default="ten_default")
    user_id          = Column(String(100), index=True, default="usr_default")
    project_id       = Column(String(100), default="default")
    version_id       = Column(String(100), nullable=True)
    state_data       = Column(Text, nullable=True) # JSON string
    created_at       = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at       = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
