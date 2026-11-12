# AetherOps Module 3 Database Models (`source_analysis` schema)

```python
from sqlalchemy import Column, String, Integer, Float, Boolean, JSON, DateTime, Text, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
import datetime
import uuid

Base = declarative_base()

class AnalysisRun(Base):
    __tablename__ = "analysis_runs"
    __table_args__ = {"schema": "source_analysis"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(String(36), index=True, nullable=False)
    environment_id = Column(String(36), index=True, nullable=True)
    repository_url = Column(String(500), nullable=False)
    branch = Column(String(100), default="main")
    commit_sha = Column(String(64), index=True, nullable=False)
    status = Column(String(50), default="COMPLETED")
    analyzer_version = Column(String(50), default="2.0.0")
    detected_languages = Column(JSON, default=list)
    frameworks = Column(JSON, default=list)
    databases = Column(JSON, default=list)
    ports = Column(JSON, default=list)
    coverage = Column(JSON, default=dict)
    findings = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class ApplicationProfileRecord(Base):
    __tablename__ = "application_profiles"
    __table_args__ = {"schema": "source_analysis"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    analysis_run_id = Column(UUID(as_uuid=True), ForeignKey("source_analysis.analysis_runs.id"), nullable=False)
    profile_data = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
```
