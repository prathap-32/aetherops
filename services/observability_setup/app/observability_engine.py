# services/observability_setup/app/observability_engine.py
from typing import List
from app.schemas import ObservabilitySetupRequest, ObservabilitySetupResponse, TelemetryArtifact

def generate_observability_suite(req: ObservabilitySetupRequest) -> ObservabilitySetupResponse:
    """
    Synthesizes CloudWatch alarm definitions, OpenTelemetry collector YAML, and Grafana dashboard JSON.
    """
    artifacts: List[TelemetryArtifact] = []
    telemetry_stack = ["Amazon CloudWatch Metrics & Logs"]

    # 1. CloudWatch Terraform Alarms Module
    cw_terraform = f"""# CloudWatch Alarms for {req.project_name} ({req.environment})
resource "aws_sns_topic" "alerts" {{
  name = "{req.project_name}-{req.environment}-alerts"
}}

resource "aws_cloudwatch_metric_alarm" "high_cpu" {{
  alarm_name          = "{req.project_name}-ec2-high-cpu"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = 2
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = 300
  statistic           = "Average"
  threshold           = {req.target_cpu_alarm_threshold}
  alarm_description   = "Triggered when instance average CPU breaches {req.target_cpu_alarm_threshold}% for 10 minutes"
  alarm_actions       = [aws_sns_topic.alerts.arn]
}}

resource "aws_cloudwatch_metric_alarm" "alb_5xx_errors" {{
  alarm_name          = "{req.project_name}-alb-high-5xx"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "HTTPCode_Target_5XX_Count"
  namespace           = "AWS/ApplicationELB"
  period              = 60
  statistic           = "Sum"
  threshold           = {req.target_error_rate_threshold}
  alarm_description   = "Triggers when downstream backend nodes return 5xx errors"
  alarm_actions       = [aws_sns_topic.alerts.arn]
}}

resource "aws_cloudwatch_metric_alarm" "rds_low_storage" {{
  alarm_name          = "{req.project_name}-rds-storage-low"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = 1
  metric_name         = "FreeStorageSpace"
  namespace           = "AWS/RDS"
  period              = 300
  statistic           = "Average"
  threshold           = 5368709120  # 5 GB in bytes
  alarm_description   = "Free database storage capacity fell below 5 GB"
  alarm_actions       = [aws_sns_topic.alerts.arn]
}}
"""
    artifacts.append(TelemetryArtifact(
        filename="cloudwatch-alarms.tf",
        artifact_type="CLOUDWATCH",
        content=cw_terraform
    ))

    # 2. OpenTelemetry Collector Configuration
    if req.enable_otel:
        telemetry_stack.append("OpenTelemetry (OTel) Distributed Tracing")
        otel_yaml = f"""# OpenTelemetry Collector Configuration for {req.project_name}
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317
      http:
        endpoint: 0.0.0.0:4318

processors:
  batch:
    timeout: 1s
    send_batch_size: 1024
  memory_limiter:
    check_interval: 2s
    limit_percentage: 75
    spike_limit_percentage: 15

exporters:
  awsxray:
    region: us-east-1
  awsemf:
    region: us-east-1
    log_group_name: "/aws/ecs/{req.project_name}"
    log_stream_name: "otel-metrics"

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [memory_limiter, batch]
      exporters: [awsxray]
    metrics:
      receivers: [otlp]
      processors: [memory_limiter, batch]
      exporters: [awsemf]
"""
        artifacts.append(TelemetryArtifact(
            filename="otel-collector-config.yaml",
            artifact_type="OTEL",
            content=otel_yaml
        ))

    # 3. Grafana Dashboard JSON
    grafana_json = f"""{{
  "annotations": {{ "list": [] }},
  "editable": true,
  "fiscalYearStartMonth": 0,
  "graphTooltip": 0,
  "id": null,
  "title": "{req.project_name} - Cloud Telemetry & SLO Overview",
  "panels": [
    {{
      "title": "CPU Saturation (%)",
      "type": "timeseries",
      "targets": [
        {{
          "namespace": "AWS/EC2",
          "metricName": "CPUUtilization",
          "dimensions": {{ "Project": "{req.project_name}" }}
        }}
      ]
    }},
    {{
      "title": "ALB Target Response Latency (p95 ms)",
      "type": "timeseries",
      "targets": [
        {{
          "namespace": "AWS/ApplicationELB",
          "metricName": "TargetResponseTime",
          "dimensions": {{ "Project": "{req.project_name}" }}
        }}
      ]
    }}
  ]
}}"""
    artifacts.append(TelemetryArtifact(
        filename="grafana-dashboard.json",
        artifact_type="GRAFANA",
        content=grafana_json
    ))
    telemetry_stack.append("Grafana Unified Telemetry Visualizer")

    return ObservabilitySetupResponse(
        status="SUCCESS",
        project_name=req.project_name,
        telemetry_stack=telemetry_stack,
        artifacts=artifacts,
        monitored_metrics=["CPUUtilization", "FreeStorageSpace", "HTTPCode_Target_5XX_Count", "TargetResponseTime", "Distributed OTel Traces"]
    )
