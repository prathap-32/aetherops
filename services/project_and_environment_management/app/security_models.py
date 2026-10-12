# services/project_and_environment_management/app/security_models.py
import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from app.database import Base


class AdminUser(Base):
    __tablename__ = "pm_admin_users"

    id             = Column(Integer, primary_key=True, index=True)
    username       = Column(String(64),  unique=True, index=True, nullable=False)
    email          = Column(String(120), unique=True, index=True, nullable=False)
    password_hash  = Column(String(255), nullable=False)
    role           = Column(String(32),  default="SUPER_ADMIN", nullable=False)
    is_active      = Column(Boolean,     default=True, nullable=False)
    failed_attempts= Column(Integer,     default=0, nullable=False)
    locked_until   = Column(DateTime,    nullable=True)
    last_login_at  = Column(DateTime,    nullable=True)
    created_at     = Column(DateTime,    default=datetime.datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            "id":            self.id,
            "username":      self.username,
            "email":         self.email,
            "role":          self.role,
            "is_active":     self.is_active,
            "last_login_at": self.last_login_at.isoformat() if self.last_login_at else None,
            "created_at":    self.created_at.isoformat() if self.created_at else None,
        }


class AdminAuditLog(Base):
    __tablename__ = "pm_admin_audit_logs"

    id              = Column(Integer, primary_key=True, index=True)
    username        = Column(String(64),  index=True, nullable=False)
    action          = Column(String(64),  nullable=False)
    target_resource = Column(String(120), nullable=True)
    status          = Column(String(32),  default="SUCCESS", nullable=False)
    ip_address      = Column(String(64),  nullable=True)
    details         = Column(String(500), nullable=True)
    created_at      = Column(DateTime,    default=datetime.datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            "id":              self.id,
            "username":        self.username,
            "action":          self.action,
            "target_resource": self.target_resource,
            "status":          self.status,
            "ip_address":      self.ip_address,
            "details":         self.details,
            "created_at":      self.created_at.isoformat() if self.created_at else None,
        }
