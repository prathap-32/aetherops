# shared/aetherops_common/__init__.py
"""
AetherOps Common Shared Utilities.
Centralized Application Secrets Management & Runtime Configuration.
"""

from .secrets import (
    load_application_secrets,
    get_application_setting,
    get_application_secrets_status,
    SecretsManagerError,
)

__all__ = [
    "load_application_secrets",
    "get_application_setting",
    "get_application_secrets_status",
    "SecretsManagerError",
]
