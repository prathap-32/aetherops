# services/iac_generator/app/models.py
import datetime
from sqlalchemy import Column, String, Text, Float, DateTime
from app.database import Base

class GeneratedIacModel(Base):
    __tablename__ = "generated_iac_bundles"

    terraform_version_id    = Column(String(100), primary_key=True, index=True)
    architecture_version_id = Column(String(100), index=True, nullable=False)
    project_name            = Column(String(100), index=True, default="aether-workload")
    aws_region              = Column(String(50), default="us-east-1")
    iac_tool                = Column(String(50), default="terraform")
    checksum                = Column(String(128), nullable=False)
    files_json              = Column(Text, nullable=False) # JSON serialized list of files
    tenant_id               = Column(String(50), index=True, default="ten_default")
    user_id                 = Column(String(100), index=True, default="usr_default")
    created_at              = Column(DateTime, default=datetime.datetime.utcnow)
