# services/source_and_cloud_connection/app/models.py
import datetime
from sqlalchemy import Column, String, DateTime, Text, Boolean, UniqueConstraint
from app.database import Base


class GitConnection(Base):
    """
    Stores a GitHub/Git repository connection for a specific project environment.

    One environment has at most one active GitConnection.
    The PAT token is stored as a reference label only — never echoed back to the UI.
    """
    __tablename__ = "sc_git_connections"

    id              = Column(String(36),  primary_key=True, index=True)   # UUID v4
    project_id      = Column(String(36),  nullable=False, index=True)     # from Module 1
    environment_id  = Column(String(36),  nullable=False, index=True)     # from Module 1
    tenant_id       = Column(String(36),  nullable=True,  index=True)     # Tenant isolation
    created_by_user_id = Column(String(36), nullable=True, index=True)    # User UUID
    owner           = Column(String(100), nullable=False, index=True)     # user who connected

    # Repository details (filled by user)
    repo_url        = Column(String(500), nullable=False)                  # https://github.com/org/repo
    repo_name       = Column(String(200), nullable=False)                  # org/repo-name
    branch          = Column(String(200), nullable=False, default="main")
    pat_label       = Column(String(100), nullable=True)                   # e.g. "my-github-pat" — no token stored
    pat_token_hash  = Column(String(255), nullable=True)                   # bcrypt hash for validation only
    encrypted_pat   = Column(Text,        nullable=True)                   # AES-256-GCM encrypted PAT
    pat_nonce       = Column(String(64),  nullable=True)                   # Base64 96-bit nonce
    pat_tag         = Column(String(64),  nullable=True)                   # Base64 128-bit GCM tag

    auth_type       = Column(String(30),  nullable=True, default="PAT")    # OAUTH | PAT | MANUAL
    github_user     = Column(String(100), nullable=True)                   # GitHub username if connected via OAuth/PAT

    # System-populated after connection validation
    default_branch  = Column(String(200), nullable=True)
    last_commit_sha = Column(String(40),  nullable=True)
    last_commit_msg = Column(String(500), nullable=True)
    last_commit_author = Column(String(200), nullable=True)
    last_commit_at  = Column(DateTime,    nullable=True)
    is_private      = Column(Boolean,     default=False)
    stars           = Column(String(20),  nullable=True)
    language        = Column(String(50),  nullable=True)                   # primary detected language

    status          = Column(String(30),  nullable=False, default="PENDING")
    # PENDING → CONNECTED → FAILED | DISCONNECTED

    created_at      = Column(DateTime,    nullable=False, default=datetime.datetime.utcnow)
    updated_at      = Column(DateTime,    nullable=False, default=datetime.datetime.utcnow,
                             onupdate=datetime.datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("project_id", "environment_id", name="_sc_proj_env_uc"),
    )

    def to_dict(self):
        return {
            "id":               self.id,
            "project_id":       self.project_id,
            "environment_id":   self.environment_id,
            "tenant_id":        self.tenant_id,
            "created_by_user_id": self.created_by_user_id,
            "owner":            self.owner,
            "repo_url":         self.repo_url,
            "repo_name":        self.repo_name,
            "branch":           self.branch,
            "pat_label":        self.pat_label,
            "auth_type":        self.auth_type or "PAT",
            "github_user":      self.github_user,
            "default_branch":   self.default_branch,
            "last_commit_sha":  self.last_commit_sha,
            "last_commit_msg":  self.last_commit_msg,
            "last_commit_author": self.last_commit_author,
            "last_commit_at":   self.last_commit_at.isoformat() if self.last_commit_at else None,
            "is_private":       bool(self.is_private),
            "stars":            self.stars,
            "language":         self.language,
            "status":           self.status,
            "created_at":       self.created_at.isoformat() if self.created_at else None,
            "updated_at":       self.updated_at.isoformat() if self.updated_at else None,
        }


class CloudConnection(Base):
    """
    Stores an AWS Cloud connection (Access Keys or IAM Role ARN) for a project environment.

    One environment has at most one active CloudConnection.
    Sensitive credentials (Secret Key) are masked or hashed and never echoed back in plain text.
    """
    __tablename__ = "sc_cloud_connections"

    id                 = Column(String(36),  primary_key=True, index=True)   # UUID v4
    project_id         = Column(String(36),  nullable=False, index=True)
    environment_id     = Column(String(36),  nullable=False, index=True)
    tenant_id          = Column(String(36),  nullable=True,  index=True)
    created_by_user_id = Column(String(36),  nullable=True,  index=True)
    owner              = Column(String(100), nullable=False, index=True)

    provider           = Column(String(30),  nullable=False, default="AWS")  # AWS | GCP | AZURE
    auth_type          = Column(String(30),  nullable=False, default="ACCESS_KEYS")  # ACCESS_KEYS | IAM_ROLE_ARN
    aws_region         = Column(String(50),  nullable=False, default="us-east-1")

    # Access Keys mode (masked for display)
    access_key_masked  = Column(String(30),  nullable=True)                  # e.g. "AKIA••••••••1234"
    access_key_id      = Column(String(128), nullable=True)                  # stored for deployment runner
    secret_key_hash    = Column(String(255), nullable=True)                  # legacy verification hash
    encrypted_secret   = Column(Text,        nullable=True)                  # AES-256-GCM encrypted secret key
    encryption_nonce   = Column(String(64),  nullable=True)                  # Base64 96-bit nonce
    encryption_tag     = Column(String(64),  nullable=True)                  # Base64 128-bit GCM auth tag
    encryption_key_id  = Column(String(64),  nullable=True)                  # Key provider ID (e.g. root-v1)

    # IAM Role ARN mode
    role_arn           = Column(String(300), nullable=True)                  # arn:aws:iam::123456789012:role/...
    external_id        = Column(String(100), nullable=True)

    # AWS Identity populated via STS GetCallerIdentity
    account_id         = Column(String(30),  nullable=True)                  # 12-digit AWS Account ID
    caller_arn         = Column(String(300), nullable=True)                  # validated caller/role ARN
    caller_user_id     = Column(String(100), nullable=True)                  # STS UserId

    status             = Column(String(30),  nullable=False, default="PENDING")
    # PENDING → CONNECTED → FAILED | DISCONNECTED

    last_validated_at  = Column(DateTime,    nullable=True)
    created_at         = Column(DateTime,    nullable=False, default=datetime.datetime.utcnow)
    updated_at         = Column(DateTime,    nullable=False, default=datetime.datetime.utcnow,
                                onupdate=datetime.datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("project_id", "environment_id", name="_sc_cloud_proj_env_uc"),
    )

    def to_dict(self):
        return {
            "id":                self.id,
            "project_id":        self.project_id,
            "environment_id":    self.environment_id,
            "tenant_id":          self.tenant_id,
            "created_by_user_id": self.created_by_user_id,
            "owner":             self.owner,
            "provider":          self.provider,
            "auth_type":         self.auth_type,
            "aws_region":        self.aws_region,
            "access_key_masked": self.access_key_masked,
            "role_arn":          self.role_arn,
            "external_id":       self.external_id,
            "account_id":        self.account_id,
            "caller_arn":        self.caller_arn,
            "caller_user_id":    self.caller_user_id,
            "status":            self.status,
            "last_validated_at": self.last_validated_at.isoformat() if self.last_validated_at else None,
            "created_at":        self.created_at.isoformat() if self.created_at else None,
            "updated_at":        self.updated_at.isoformat() if self.updated_at else None,
        }


class SourceSnapshot(Base):
    """
    A point-in-time snapshot of the repository's file tree and metadata
    captured when a connection is made or refreshed.

    Passed forward to Module 3 (Source Code Analyzer).
    """
    __tablename__ = "sc_source_snapshots"

    id              = Column(String(36),  primary_key=True, index=True)
    connection_id   = Column(String(36),  nullable=False, index=True)   # FK → GitConnection.id
    project_id      = Column(String(36),  nullable=False, index=True)
    environment_id  = Column(String(36),  nullable=False, index=True)

    commit_sha      = Column(String(40),  nullable=False)
    branch          = Column(String(200), nullable=False)

    # JSON blobs
    file_tree       = Column(Text, nullable=True)   # JSON: [{path, type, size}]
    detected_files  = Column(Text, nullable=True)   # JSON: {dockerfile, package_json, requirements_txt, ...}
    language_hints  = Column(Text, nullable=True)   # JSON: {primary: "Python", others: ["JS"]}
    total_files     = Column(String(20), nullable=True)
    total_size_kb   = Column(String(20), nullable=True)

    created_at      = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)

    def to_dict(self):
        import json
        def _j(v):
            if not v:
                return {}
            try:
                return json.loads(v)
            except Exception:
                return {}
        def _jl(v):
            if not v:
                return []
            try:
                return json.loads(v)
            except Exception:
                return []
        return {
            "id":             self.id,
            "connection_id":  self.connection_id,
            "project_id":     self.project_id,
            "environment_id": self.environment_id,
            "commit_sha":     self.commit_sha,
            "branch":         self.branch,
            "file_tree":      _jl(self.file_tree),
            "detected_files": _j(self.detected_files),
            "language_hints": _j(self.language_hints),
            "total_files":    self.total_files,
            "total_size_kb":  self.total_size_kb,
            "created_at":     self.created_at.isoformat() if self.created_at else None,
        }
