# services/observability_setup/app/schemas.py
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class ObservabilitySetupRequest(BaseModel):
    project_name: str = Field(default="workload-telemetry")
    environment: str = Field(default="production")
    alert_channel: str = Field(default="slack_webhook", description="email, slack_webhook, pagerduty")
    slack_webhook_url: Optional[str] = Field(default="https://hooks.slack.com/services/mock")
    enable_otel: bool = Field(default=True)
    enable_cloudwatch_alarms: bool = Field(default=True)
    target_cpu_alarm_threshold: int = Field(default=80, ge=50, le=95)
    target_error_rate_threshold: float = Field(default=1.0, ge=0.1, le=10.0)

class TelemetryArtifact(BaseModel):
    filename: str
    artifact_type: str  # CLOUDWATCH, OTEL, PROMETHEUS, GRAFANA
    content: str

class ObservabilitySetupResponse(BaseModel):
    status: str
    project_name: str
    telemetry_stack: List[str]
    artifacts: List[TelemetryArtifact]
    monitored_metrics: List[str]
