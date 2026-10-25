// frontend/src/constants/awsRegions.js
// Complete list of all 39 AWS Regions with descriptive names and geographical grouping

export const AWS_REGIONS_39 = [
  // North America (9)
  { value: 'us-east-1', label: 'us-east-1 (US East - N. Virginia)', group: 'North America' },
  { value: 'us-east-2', label: 'us-east-2 (US East - Ohio)', group: 'North America' },
  { value: 'us-west-1', label: 'us-west-1 (US West - N. California)', group: 'North America' },
  { value: 'us-west-2', label: 'us-west-2 (US West - Oregon)', group: 'North America' },
  { value: 'ca-central-1', label: 'ca-central-1 (Canada - Central)', group: 'North America' },
  { value: 'ca-west-1', label: 'ca-west-1 (Canada West - Calgary)', group: 'North America' },
  { value: 'mx-central-1', label: 'mx-central-1 (Mexico - Central)', group: 'North America' },
  { value: 'us-gov-east-1', label: 'us-gov-east-1 (AWS GovCloud US-East)', group: 'North America' },
  { value: 'us-gov-west-1', label: 'us-gov-west-1 (AWS GovCloud US-West)', group: 'North America' },

  // South America (1)
  { value: 'sa-east-1', label: 'sa-east-1 (South America - São Paulo)', group: 'South America' },

  // Europe (8)
  { value: 'eu-west-1', label: 'eu-west-1 (Europe - Ireland)', group: 'Europe' },
  { value: 'eu-west-2', label: 'eu-west-2 (Europe - London)', group: 'Europe' },
  { value: 'eu-west-3', label: 'eu-west-3 (Europe - Paris)', group: 'Europe' },
  { value: 'eu-central-1', label: 'eu-central-1 (Europe - Frankfurt)', group: 'Europe' },
  { value: 'eu-central-2', label: 'eu-central-2 (Europe - Zurich)', group: 'Europe' },
  { value: 'eu-north-1', label: 'eu-north-1 (Europe - Stockholm)', group: 'Europe' },
  { value: 'eu-south-1', label: 'eu-south-1 (Europe - Milan)', group: 'Europe' },
  { value: 'eu-south-2', label: 'eu-south-2 (Europe - Spain)', group: 'Europe' },

  // Asia Pacific (13)
  { value: 'ap-south-1', label: 'ap-south-1 (Asia Pacific - Mumbai)', group: 'Asia Pacific' },
  { value: 'ap-south-2', label: 'ap-south-2 (Asia Pacific - Hyderabad)', group: 'Asia Pacific' },
  { value: 'ap-southeast-1', label: 'ap-southeast-1 (Asia Pacific - Singapore)', group: 'Asia Pacific' },
  { value: 'ap-southeast-2', label: 'ap-southeast-2 (Asia Pacific - Sydney)', group: 'Asia Pacific' },
  { value: 'ap-southeast-3', label: 'ap-southeast-3 (Asia Pacific - Jakarta)', group: 'Asia Pacific' },
  { value: 'ap-southeast-4', label: 'ap-southeast-4 (Asia Pacific - Melbourne)', group: 'Asia Pacific' },
  { value: 'ap-southeast-5', label: 'ap-southeast-5 (Asia Pacific - Malaysia)', group: 'Asia Pacific' },
  { value: 'ap-southeast-6', label: 'ap-southeast-6 (Asia Pacific - New Zealand)', group: 'Asia Pacific' },
  { value: 'ap-southeast-7', label: 'ap-southeast-7 (Asia Pacific - Thailand)', group: 'Asia Pacific' },
  { value: 'ap-east-1', label: 'ap-east-1 (Asia Pacific - Hong Kong)', group: 'Asia Pacific' },
  { value: 'ap-east-2', label: 'ap-east-2 (Asia Pacific - Taipei)', group: 'Asia Pacific' },
  { value: 'ap-northeast-1', label: 'ap-northeast-1 (Asia Pacific - Tokyo)', group: 'Asia Pacific' },
  { value: 'ap-northeast-2', label: 'ap-northeast-2 (Asia Pacific - Seoul)', group: 'Asia Pacific' },
  { value: 'ap-northeast-3', label: 'ap-northeast-3 (Asia Pacific - Osaka)', group: 'Asia Pacific' },

  // Middle East & Africa (6)
  { value: 'me-south-1', label: 'me-south-1 (Middle East - Bahrain)', group: 'Middle East & Africa' },
  { value: 'me-central-1', label: 'me-central-1 (Middle East - UAE)', group: 'Middle East & Africa' },
  { value: 'me-central-2', label: 'me-central-2 (Middle East - Saudi Arabia)', group: 'Middle East & Africa' },
  { value: 'il-central-1', label: 'il-central-1 (Israel - Tel Aviv)', group: 'Middle East & Africa' },
  { value: 'af-south-1', label: 'af-south-1 (Africa - Cape Town)', group: 'Middle East & Africa' },

  // China (2)
  { value: 'cn-north-1', label: 'cn-north-1 (China - Beijing)', group: 'China' },
  { value: 'cn-northwest-1', label: 'cn-northwest-1 (China - Ningxia)', group: 'China' },
];

export const PROJECT_TYPES_LIST = [
  { value: 'web_application', label: 'Web Application', desc: 'Full-stack or SPA with REST/GraphQL backend', icon: '🌐' },
  { value: 'api_service', label: 'API Service', desc: 'High-throughput microservice or backend API', icon: '⚡' },
  { value: 'microservices', label: 'Microservices Mesh', desc: 'Distributed service fleet with API Gateway', icon: '🧩' },
  { value: 'data_pipeline', label: 'Data Pipeline', desc: 'ETL/ELT batch and streaming data pipeline', icon: '📊' },
  { value: 'serverless_backend', label: 'Serverless Backend', desc: 'Event-driven AWS Lambda + DynamoDB backend', icon: '☁️' },
  { value: 'event_driven_pipeline', label: 'Event-Driven Pipeline', desc: 'SQS/SNS/EventBridge asynchronous streaming', icon: '📨' },
  { value: 'data_lakehouse', label: 'Data Lakehouse', desc: 'S3 + Athena + Glue Analytics Lakehouse', icon: '🗄️' },
  { value: 'ml_workload', label: 'ML Training Workload', desc: 'SageMaker & GPU cluster model training', icon: '🧠' },
  { value: 'ml_inference_pipeline', label: 'ML Inference Engine', desc: 'Low-latency real-time model serving API', icon: '🤖' },
  { value: 'iot_ingestion', label: 'IoT Ingestion Fleet', desc: 'AWS IoT Core & real-time telemetry processing', icon: '📡' },
  { value: 'mobile_backend', label: 'Mobile Backend', desc: 'Cognito + AppSync + DynamoDB Mobile API', icon: '📱' },
  { value: 'containerized_workload', label: 'Containerized (ECS/EKS)', desc: 'Docker workloads orchestrated on ECS/EKS', icon: '🐳' },
  { value: 'static_site', label: 'Static Site / Jamstack', desc: 'CloudFront + S3 static SPA hosting', icon: '📄' },
  { value: 'fintech_ledger', label: 'FinTech Core Ledger', desc: 'ACID-compliant double-entry ledger & KMS', icon: '💳' },
  { value: 'edge_computing', label: 'Edge Computing', desc: 'Lambda@Edge & CloudFront Functions', icon: '🌍' },
  { value: 'internal_tool', label: 'Internal Operations Tool', desc: 'Secure back-office admin application', icon: '🛠️' },
];

export const TIER_TYPES_LIST = [
  { value: 'development', label: 'DEV (Development)', badgeColor: 'bg-blue-50 text-blue-700 border-blue-200' },
  { value: 'staging', label: 'STAGING (Staging & Pre-prod)', badgeColor: 'bg-amber-50 text-amber-700 border-amber-200' },
  { value: 'production', label: 'PROD (Production)', badgeColor: 'bg-rose-50 text-rose-700 border-rose-200' },
  { value: 'testing', label: 'TEST (Integration / Automated Testing)', badgeColor: 'bg-purple-50 text-purple-700 border-purple-200' },
  { value: 'qa', label: 'QA (Quality Assurance)', badgeColor: 'bg-indigo-50 text-indigo-700 border-indigo-200' },
  { value: 'disaster_recovery', label: 'DR (Disaster Recovery & Hot Standby)', badgeColor: 'bg-orange-50 text-orange-700 border-orange-200' },
  { value: 'sandbox', label: 'SANDBOX (Developer Sandbox)', badgeColor: 'bg-emerald-50 text-emerald-700 border-emerald-200' },
];
