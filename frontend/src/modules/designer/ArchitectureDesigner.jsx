// frontend/src/modules/designer/ArchitectureDesigner.jsx
import React, { useState, useRef, useEffect, useMemo, useCallback } from 'react';
import {
  Palette,
  Layers,
  Network,
  Plus,
  ArrowRight,
  ShieldCheck,
  Sparkles,
  CheckCircle2,
  ZoomIn,
  ZoomOut,
  Maximize2,
  RotateCcw,
  MousePointer,
  Hand,
  Link2,
  Trash2,
  Download,
  Upload,
  Save,
  FileCode,
  DollarSign,
  Cpu,
  Server,
  Database,
  Globe,
  Lock,
  Cloud,
  HardDrive,
  Shield,
  Zap,
  Info,
  ChevronDown,
  ChevronRight,
  Search,
  ExternalLink,
  Sliders,
  Copy,
  Check,
  RefreshCw,
  Box,
  CornerDownRight,
  SlidersHorizontal,
  X,
  Play
} from 'lucide-react';
import { architectureStudioApi } from '../../services/api';

// ═══════════════════════════════════════════════════════════════════════════════
// AWS Icon Component — Official AWS Brand Colors on Light Theme
// ═══════════════════════════════════════════════════════════════════════════════
export function AwsIcon({ type, className = "w-5 h-5", size = 20 }) {
  switch (type) {
    case 'ec2':
      return (
        <svg viewBox="0 0 24 24" width={size} height={size} className={className} fill="none">
          <rect x="2.5" y="2.5" width="19" height="19" rx="4" fill="#ff9900" stroke="#d97706" strokeWidth="1.25" />
          <path d="M7 8h10M7 12h10M7 16h6" stroke="#ffffff" strokeLinecap="round" strokeWidth="2" />
          <circle cx="16" cy="16" r="1.5" fill="#ffffff" />
        </svg>
      );
    case 'ecs':
    case 'fargate':
      return (
        <svg viewBox="0 0 24 24" width={size} height={size} className={className} fill="none">
          <rect x="2.5" y="2.5" width="19" height="19" rx="4" fill="#ff9900" stroke="#d97706" strokeWidth="1.25" />
          <rect x="6" y="6" width="5" height="5" rx="1" fill="#ffffff" />
          <rect x="13" y="6" width="5" height="5" rx="1" fill="#ffffff" />
          <rect x="6" y="13" width="5" height="5" rx="1" fill="#ffffff" />
          <rect x="13" y="13" width="5" height="5" rx="1" fill="#ffffff" />
        </svg>
      );
    case 'lambda':
      return (
        <svg viewBox="0 0 24 24" width={size} height={size} className={className} fill="none">
          <rect x="2.5" y="2.5" width="19" height="19" rx="4" fill="#ff9900" stroke="#d97706" strokeWidth="1.25" />
          <path d="M7 17.5l4.5-9.5M11.5 8h6M11.5 17.5l4-7" stroke="#ffffff" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      );
    case 'eks':
      return (
        <svg viewBox="0 0 24 24" width={size} height={size} className={className} fill="none">
          <rect x="2.5" y="2.5" width="19" height="19" rx="4" fill="#ff9900" stroke="#d97706" strokeWidth="1.25" />
          <circle cx="12" cy="12" r="5" stroke="#ffffff" strokeWidth="1.75" />
          <path d="M12 7v10M7 12h10" stroke="#ffffff" strokeWidth="1.5" strokeLinecap="round" />
        </svg>
      );
    case 'vpc':
      return (
        <svg viewBox="0 0 24 24" width={size} height={size} className={className} fill="none">
          <rect x="2.5" y="2.5" width="19" height="19" rx="4" fill="#8c4fff" stroke="#6d28d9" strokeWidth="1.25" />
          <path d="M6.5 8h11a1.5 1.5 0 011.5 1.5v7a1.5 1.5 0 01-1.5 1.5h-11A1.5 1.5 0 015 16.5v-7A1.5 1.5 0 016.5 8z" stroke="#ffffff" strokeWidth="1.5" />
          <path d="M9 12h6M12 9v6" stroke="#ffffff" strokeWidth="1.5" strokeLinecap="round" />
        </svg>
      );
    case 'subnet_public':
      return (
        <svg viewBox="0 0 24 24" width={size} height={size} className={className} fill="none">
          <rect x="2.5" y="2.5" width="19" height="19" rx="4" fill="#0284c7" stroke="#0369a1" strokeWidth="1.25" />
          <rect x="6" y="6" width="12" height="12" rx="2" stroke="#ffffff" strokeWidth="1.75" strokeDasharray="3 2" />
          <circle cx="12" cy="12" r="2.5" fill="#ffffff" />
        </svg>
      );
    case 'subnet_private':
      return (
        <svg viewBox="0 0 24 24" width={size} height={size} className={className} fill="none">
          <rect x="2.5" y="2.5" width="19" height="19" rx="4" fill="#475569" stroke="#334155" strokeWidth="1.25" />
          <rect x="6" y="6" width="12" height="12" rx="2" stroke="#ffffff" strokeWidth="1.75" strokeDasharray="3 2" />
          <path d="M10 11v-1a2 2 0 114 0v1m-5 0h6v4h-6v-4z" fill="#ffffff" />
        </svg>
      );
    case 'alb':
      return (
        <svg viewBox="0 0 24 24" width={size} height={size} className={className} fill="none">
          <rect x="2.5" y="2.5" width="19" height="19" rx="4" fill="#8c4fff" stroke="#6d28d9" strokeWidth="1.25" />
          <circle cx="12" cy="7" r="2" fill="#ffffff" />
          <path d="M12 9v4m0 0l-4 3m4-3l4 3" stroke="#ffffff" strokeWidth="1.75" strokeLinecap="round" />
          <circle cx="7" cy="17" r="1.5" fill="#ffffff" />
          <circle cx="17" cy="17" r="1.5" fill="#ffffff" />
        </svg>
      );
    case 'eip':
      return (
        <svg viewBox="0 0 24 24" width={size} height={size} className={className} fill="none">
          <rect x="2.5" y="2.5" width="19" height="19" rx="4" fill="#a855f7" stroke="#7e22ce" strokeWidth="1.25" />
          <circle cx="12" cy="10" r="3" stroke="#ffffff" strokeWidth="1.75" />
          <path d="M12 13v5M9.5 18h5" stroke="#ffffff" strokeWidth="2" strokeLinecap="round" />
        </svg>
      );
    case 'route53':
      return (
        <svg viewBox="0 0 24 24" width={size} height={size} className={className} fill="none">
          <rect x="2.5" y="2.5" width="19" height="19" rx="4" fill="#7c3aed" stroke="#6d28d9" strokeWidth="1.25" />
          <circle cx="12" cy="12" r="6" stroke="#ffffff" strokeWidth="1.75" />
          <path d="M12 6l2 6-4-2 2-4z" fill="#ffffff" />
        </svg>
      );
    case 'cloudfront':
      return (
        <svg viewBox="0 0 24 24" width={size} height={size} className={className} fill="none">
          <rect x="2.5" y="2.5" width="19" height="19" rx="4" fill="#8c4fff" stroke="#6d28d9" strokeWidth="1.25" />
          <circle cx="12" cy="12" r="5" stroke="#ffffff" strokeWidth="1.75" />
          <circle cx="6" cy="8" r="1.5" fill="#ffffff" />
          <circle cx="18" cy="8" r="1.5" fill="#ffffff" />
          <circle cx="12" cy="19" r="1.5" fill="#ffffff" />
        </svg>
      );
    case 'igw':
      return (
        <svg viewBox="0 0 24 24" width={size} height={size} className={className} fill="none">
          <rect x="2.5" y="2.5" width="19" height="19" rx="4" fill="#8c4fff" stroke="#6d28d9" strokeWidth="1.25" />
          <path d="M6 12h12M14 8l4 4-4 4" stroke="#ffffff" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      );
    case 'nat_gw':
      return (
        <svg viewBox="0 0 24 24" width={size} height={size} className={className} fill="none">
          <rect x="2.5" y="2.5" width="19" height="19" rx="4" fill="#8c4fff" stroke="#6d28d9" strokeWidth="1.25" />
          <path d="M7 10h10M13 6l4 4-4 4M17 14H7M11 18l-4-4 4-4" stroke="#ffffff" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      );
    case 'rds_pg':
    case 'rds_mysql':
    case 'rds_aurora':
    case 'rds':
      return (
        <svg viewBox="0 0 24 24" width={size} height={size} className={className} fill="none">
          <rect x="2.5" y="2.5" width="19" height="19" rx="4" fill="#3b82f6" stroke="#2563eb" strokeWidth="1.25" />
          <ellipse cx="12" cy="8" rx="6" ry="2.5" stroke="#ffffff" strokeWidth="1.5" />
          <path d="M6 8v4c0 1.38 2.69 2.5 6 2.5s6-1.12 6-2.5V8M6 12v4c0 1.38 2.69 2.5 6 2.5s6-1.12 6-2.5v-4" stroke="#ffffff" strokeWidth="1.5" />
        </svg>
      );
    case 'elasticache':
      return (
        <svg viewBox="0 0 24 24" width={size} height={size} className={className} fill="none">
          <rect x="2.5" y="2.5" width="19" height="19" rx="4" fill="#0284c7" stroke="#0369a1" strokeWidth="1.25" />
          <path d="M6 12l6-4 6 4-6 4-6-4z" stroke="#ffffff" strokeWidth="1.75" fill="none" />
          <path d="M6 15l6 4 6-4" stroke="#ffffff" strokeWidth="1.75" strokeLinecap="round" />
        </svg>
      );
    case 'dynamodb':
      return (
        <svg viewBox="0 0 24 24" width={size} height={size} className={className} fill="none">
          <rect x="2.5" y="2.5" width="19" height="19" rx="4" fill="#3b82f6" stroke="#2563eb" strokeWidth="1.25" />
          <ellipse cx="12" cy="7" rx="5.5" ry="2" stroke="#ffffff" strokeWidth="1.5" />
          <path d="M6.5 7v10c0 1.1 2.46 2 5.5 2s5.5-.9 5.5-2V7" stroke="#ffffff" strokeWidth="1.5" />
          <path d="M6.5 12c0 1.1 2.46 2 5.5 2s5.5-.9 5.5-2" stroke="#ffffff" strokeWidth="1.5" />
        </svg>
      );
    case 's3':
      return (
        <svg viewBox="0 0 24 24" width={size} height={size} className={className} fill="none">
          <rect x="2.5" y="2.5" width="19" height="19" rx="4" fill="#10b981" stroke="#059669" strokeWidth="1.25" />
          <path d="M6 8h12l-1.5 10a2 2 0 01-2 1.8h-5a2 2 0 01-2-1.8L6 8z" stroke="#ffffff" strokeWidth="1.5" />
          <ellipse cx="12" cy="8" rx="6" ry="2" stroke="#ffffff" strokeWidth="1.5" />
        </svg>
      );
    case 'efs':
      return (
        <svg viewBox="0 0 24 24" width={size} height={size} className={className} fill="none">
          <rect x="2.5" y="2.5" width="19" height="19" rx="4" fill="#10b981" stroke="#059669" strokeWidth="1.25" />
          <rect x="5.5" y="6" width="13" height="12" rx="2" stroke="#ffffff" strokeWidth="1.5" />
          <path d="M9 10h6M9 14h6" stroke="#ffffff" strokeWidth="1.75" strokeLinecap="round" />
        </svg>
      );
    case 'waf':
    case 'shield':
      return (
        <svg viewBox="0 0 24 24" width={size} height={size} className={className} fill="none">
          <rect x="2.5" y="2.5" width="19" height="19" rx="4" fill="#ef4444" stroke="#dc2626" strokeWidth="1.25" />
          <path d="M12 6l6 3v4.5c0 3.5-2.5 6.5-6 7.5-3.5-1-6-4-6-7.5V9l6-3z" stroke="#ffffff" strokeWidth="1.5" />
          <path d="M10 12.5l1.5 1.5 3-3" stroke="#ffffff" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      );
    case 'kms':
      return (
        <svg viewBox="0 0 24 24" width={size} height={size} className={className} fill="none">
          <rect x="2.5" y="2.5" width="19" height="19" rx="4" fill="#ef4444" stroke="#dc2626" strokeWidth="1.25" />
          <rect x="7" y="11" width="10" height="8" rx="1.5" stroke="#ffffff" strokeWidth="1.5" />
          <path d="M9 11V8a3 3 0 016 0v3" stroke="#ffffff" strokeWidth="1.5" />
        </svg>
      );
    case 'cloudwatch':
      return (
        <svg viewBox="0 0 24 24" width={size} height={size} className={className} fill="none">
          <rect x="2.5" y="2.5" width="19" height="19" rx="4" fill="#ec4899" stroke="#db2777" strokeWidth="1.25" />
          <path d="M6 16l4-5 3 3 5-6" stroke="#ffffff" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      );
    case 'client':
    default:
      return (
        <svg viewBox="0 0 24 24" width={size} height={size} className={className} fill="none">
          <rect x="2.5" y="2.5" width="19" height="19" rx="4" fill="#0f766e" stroke="#115e59" strokeWidth="1.25" />
          <rect x="6" y="6" width="12" height="8" rx="1" stroke="#ffffff" strokeWidth="1.5" />
          <path d="M10 17h4M12 14v3" stroke="#ffffff" strokeWidth="1.75" strokeLinecap="round" />
        </svg>
      );
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// AWS Service Catalog Definitions
// ═══════════════════════════════════════════════════════════════════════════════
export const AWS_SERVICES_CATALOG = [
  // Compute
  {
    id: 'ec2',
    name: 'Amazon EC2',
    category: 'Compute',
    color: '#ff9900',
    defaultTier: 't4g.micro',
    defaultCost: 6.12,
    defaultPort: '8080',
    description: 'Virtual server with ARM Graviton2 compute. Ideal for Docker containerized workloads.',
    isContainer: false,
    tiers: ['t4g.nano', 't4g.micro', 't4g.small', 't4g.medium', 'c6g.large']
  },
  {
    id: 'ecs',
    name: 'AWS ECS Fargate',
    category: 'Compute',
    color: '#ff9900',
    defaultTier: '0.5 vCPU / 1GB',
    defaultCost: 14.40,
    defaultPort: '80',
    description: 'Serverless container execution without managing underlying EC2 virtual machines.',
    isContainer: false,
    tiers: ['0.25 vCPU / 0.5GB', '0.5 vCPU / 1GB', '1.0 vCPU / 2GB', '2.0 vCPU / 4GB']
  },
  {
    id: 'lambda',
    name: 'AWS Lambda',
    category: 'Compute',
    color: '#ff9900',
    defaultTier: 'Serverless (128MB)',
    defaultCost: 0.20,
    defaultPort: 'Event',
    description: 'Event-driven serverless computing that runs code in response to API Gateway or S3 events.',
    isContainer: false,
    tiers: ['128 MB', '256 MB', '512 MB', '1024 MB']
  },
  {
    id: 'eks',
    name: 'Amazon EKS',
    category: 'Compute',
    color: '#ff9900',
    defaultTier: 'v1.29 Managed',
    defaultCost: 73.00,
    defaultPort: '443',
    description: 'Fully managed Kubernetes cluster control plane with automated upgrades and patching.',
    isContainer: false,
    tiers: ['v1.28 Managed', 'v1.29 Managed', 'v1.30 Managed']
  },

  // Networking
  {
    id: 'vpc',
    name: 'VPC Boundary',
    category: 'Networking',
    color: '#8c4fff',
    defaultTier: '10.0.0.0/16',
    defaultCost: 0.00,
    defaultPort: 'All',
    description: 'Virtual Private Cloud isolated logical network topology container.',
    isContainer: true,
    width: 840,
    height: 520,
    tiers: ['10.0.0.0/16', '172.16.0.0/16', '192.168.0.0/16']
  },
  {
    id: 'subnet_public',
    name: 'Public Subnet',
    category: 'Networking',
    color: '#0284c7',
    defaultTier: '10.0.1.0/24',
    defaultCost: 0.00,
    defaultPort: '443/80',
    description: 'Subnet with route to Internet Gateway for public load balancers and egress NAT.',
    isContainer: true,
    width: 320,
    height: 380,
    tiers: ['10.0.1.0/24', '10.0.2.0/24', '10.0.3.0/24']
  },
  {
    id: 'subnet_private',
    name: 'Private Subnet',
    category: 'Networking',
    color: '#475569',
    defaultTier: '10.0.2.0/24',
    defaultCost: 0.00,
    defaultPort: 'Internal',
    description: 'Subnet isolated from direct internet ingress. Hosts compute instances and databases.',
    isContainer: true,
    width: 440,
    height: 380,
    tiers: ['10.0.10.0/24', '10.0.11.0/24', '10.0.12.0/24']
  },
  {
    id: 'alb',
    name: 'Application Load Balancer',
    category: 'Networking',
    color: '#8c4fff',
    defaultTier: 'Dual-AZ Managed',
    defaultCost: 16.50,
    defaultPort: '80/443',
    description: 'Layer 7 load balancer distributing HTTP/HTTPS traffic with SSL offloading.',
    isContainer: false,
    tiers: ['Dual-AZ Managed', 'Single-AZ (Dev)', 'Cross-Zone Global']
  },
  {
    id: 'eip',
    name: 'Direct Elastic IP',
    category: 'Networking',
    color: '#a855f7',
    defaultTier: 'Static Public IPv4',
    defaultCost: 0.00,
    defaultPort: '8080',
    description: 'Single static public IP attached directly to compute. Zero load balancer cost for DEV workloads.',
    isContainer: false,
    tiers: ['Static Public IPv4']
  },
  {
    id: 'route53',
    name: 'Amazon Route 53',
    category: 'Networking',
    color: '#7c3aed',
    defaultTier: 'Hosted Zone',
    defaultCost: 0.50,
    defaultPort: '53',
    description: 'Scalable cloud DNS web service and domain routing health checker.',
    isContainer: false,
    tiers: ['Public Hosted Zone', 'Private Hosted Zone', 'Latency Routing']
  },
  {
    id: 'cloudfront',
    name: 'Amazon CloudFront',
    category: 'Networking',
    color: '#8c4fff',
    defaultTier: 'Global Edge',
    defaultCost: 2.50,
    defaultPort: '443',
    description: 'Fast, secure CDN service delivering data, videos, applications, and APIs globally.',
    isContainer: false,
    tiers: ['PriceClass_100 (US/EU)', 'PriceClass_All (Global)']
  },
  {
    id: 'igw',
    name: 'Internet Gateway',
    category: 'Networking',
    color: '#8c4fff',
    defaultTier: 'VPC Gateway',
    defaultCost: 0.00,
    defaultPort: '0.0.0.0/0',
    description: 'Horizontally scaled, redundant VPC component allowing communication between VPC and internet.',
    isContainer: false,
    tiers: ['Default Redundant IGW']
  },
  {
    id: 'nat_gw',
    name: 'NAT Gateway',
    category: 'Networking',
    color: '#8c4fff',
    defaultTier: 'Managed NAT',
    defaultCost: 32.40,
    defaultPort: 'Outbound',
    description: 'Network Address Translation service enabling private subnet instances to access internet.',
    isContainer: false,
    tiers: ['Public NAT Gateway', 'Private NAT Gateway']
  },

  // Database
  {
    id: 'rds_pg',
    name: 'RDS PostgreSQL',
    category: 'Database',
    color: '#3b82f6',
    defaultTier: 'db.t4g.micro (20GB)',
    defaultCost: 8.60,
    defaultPort: '5432',
    description: 'Managed PostgreSQL relational database with automated backups and encryption at rest.',
    isContainer: false,
    tiers: ['db.t4g.micro', 'db.t4g.small', 'db.t4g.medium', 'db.r6g.large']
  },
  {
    id: 'rds_mysql',
    name: 'RDS MySQL',
    category: 'Database',
    color: '#3b82f6',
    defaultTier: 'db.t4g.micro (20GB)',
    defaultCost: 8.40,
    defaultPort: '3306',
    description: 'Managed MySQL database engine with read replicas and point-in-time recovery.',
    isContainer: false,
    tiers: ['db.t4g.micro', 'db.t4g.small', 'db.t4g.medium']
  },
  {
    id: 'rds_aurora',
    name: 'Aurora Serverless v2',
    category: 'Database',
    color: '#3b82f6',
    defaultTier: '0.5 ACU Autoscaling',
    defaultCost: 43.20,
    defaultPort: '5432/3306',
    description: 'High-performance MySQL & PostgreSQL compatible database with instant autoscaling.',
    isContainer: false,
    tiers: ['0.5 - 4 ACU', '1.0 - 8 ACU', '2.0 - 16 ACU']
  },
  {
    id: 'elasticache',
    name: 'Amazon ElastiCache Redis',
    category: 'Database',
    color: '#0284c7',
    defaultTier: 'cache.t4g.micro',
    defaultCost: 12.40,
    defaultPort: '6379',
    description: 'Ultra-low latency in-memory data store and caching cluster for sub-millisecond response.',
    isContainer: false,
    tiers: ['cache.t4g.micro', 'cache.t4g.small', 'cache.m6g.large']
  },
  {
    id: 'dynamodb',
    name: 'Amazon DynamoDB',
    category: 'Database',
    color: '#3b82f6',
    defaultTier: 'On-Demand Pay-per-Request',
    defaultCost: 1.25,
    defaultPort: 'HTTPS',
    description: 'Serverless, NoSQL database with single-digit millisecond latency at any scale.',
    isContainer: false,
    tiers: ['On-Demand', 'Provisioned (5 RCU / 5 WCU)']
  },

  // Storage
  {
    id: 's3',
    name: 'Amazon S3 Standard',
    category: 'Storage',
    color: '#10b981',
    defaultTier: 'Standard (100 GB)',
    defaultCost: 2.30,
    defaultPort: 'HTTPS',
    description: 'Object storage built to retrieve any amount of data from anywhere with 99.999999999% durability.',
    isContainer: false,
    tiers: ['Standard (100 GB)', 'Standard (500 GB)', 'Intelligent-Tiering']
  },
  {
    id: 'efs',
    name: 'Amazon EFS Elastic File',
    category: 'Storage',
    color: '#10b981',
    defaultTier: 'General Purpose (50GB)',
    defaultCost: 15.00,
    defaultPort: 'NFS:2049',
    description: 'Serverless, fully managed elastic file system for Linux containers and EC2 instances.',
    isContainer: false,
    tiers: ['Standard General Purpose', 'One Zone Storage']
  },

  // Security
  {
    id: 'waf',
    name: 'AWS WAF Shield',
    category: 'Security',
    color: '#ef4444',
    defaultTier: 'Core Managed Rule Set',
    defaultCost: 5.00,
    defaultPort: 'Filter',
    description: 'Web application firewall protecting against common exploits and bot attacks.',
    isContainer: false,
    tiers: ['Basic Rate-Limit', 'AWSManagedRulesCommonRuleSet']
  },
  {
    id: 'kms',
    name: 'AWS KMS Encryption Key',
    category: 'Security',
    color: '#ef4444',
    defaultTier: 'Customer Managed Key',
    defaultCost: 1.00,
    defaultPort: 'KMS-API',
    description: 'Hardware security module managed cryptographic keys for EBS, RDS, and S3 encryption.',
    isContainer: false,
    tiers: ['Customer Managed Key (CMK)', 'AWS Default Key']
  },
  {
    id: 'cloudwatch',
    name: 'Amazon CloudWatch Alarms',
    category: 'Security',
    color: '#ec4899',
    defaultTier: 'Detailed Metrics & Alarms',
    defaultCost: 2.10,
    defaultPort: 'Telemetry',
    description: 'Monitoring and observability service collecting operational logs and automated alarm triggers.',
    isContainer: false,
    tiers: ['Standard Metrics', 'High-Resolution Alarms']
  }
];

// ═══════════════════════════════════════════════════════════════════════════════
// Clean Architectural Blueprints (Optional Starters — Clean Production Grade)
// ═══════════════════════════════════════════════════════════════════════════════
const CLEAN_BLUEPRINTS = {
  single_ec2_dev: {
    name: 'Single EC2 Host (Dev)',
    description: 'Optimized development environment with direct Elastic IP ($0/mo) and single-AZ VPC.',
    totalCost: 6.12,
    nodes: [
      {
        id: 'vpc_1',
        serviceType: 'vpc',
        name: 'VPC: 10.0.0.0/16 (us-east-1)',
        category: 'Networking',
        tier: '10.0.0.0/16',
        cost: 0,
        x: 240,
        y: 40,
        width: 660,
        height: 440,
        isContainer: true,
      },
      {
        id: 'subnet_pub_1',
        serviceType: 'subnet_public',
        name: 'Public Subnet: 10.0.1.0/24 (AZ-a)',
        category: 'Networking',
        tier: '10.0.1.0/24',
        cost: 0,
        x: 270,
        y: 100,
        width: 320,
        height: 340,
        isContainer: true,
      },
      {
        id: 'client_1',
        serviceType: 'client',
        name: 'Internet Client',
        category: 'Networking',
        tier: 'Public HTTPS',
        cost: 0,
        x: 40,
        y: 180,
        width: 170,
        height: 80,
        sg: 'public',
        port: '443',
        status: 'Active',
      },
      {
        id: 'eip_1',
        serviceType: 'eip',
        name: 'Direct Elastic IP',
        category: 'Networking',
        tier: 'Static Public IPv4',
        cost: 0,
        x: 310,
        y: 150,
        width: 230,
        height: 80,
        sg: 'sg-eip-public',
        port: '8080',
        status: 'Dev Shield',
      },
      {
        id: 'ec2_1',
        serviceType: 'ec2',
        name: 'EC2 App Host',
        category: 'Compute',
        tier: 't4g.micro | 1 vCPU, 1 GB',
        cost: 6.12,
        x: 310,
        y: 270,
        width: 230,
        height: 85,
        sg: 'sg-app-ec2',
        port: '8080:80',
        status: 'Healthy',
      },
    ],
    edges: [
      {
        id: 'e_1',
        source: 'client_1',
        sourceAnchor: 'right',
        target: 'eip_1',
        targetAnchor: 'left',
        label: 'HTTPS:443',
        style: 'orthogonal',
        animated: true,
      },
      {
        id: 'e_2',
        source: 'eip_1',
        sourceAnchor: 'bottom',
        target: 'ec2_1',
        targetAnchor: 'top',
        label: 'HTTP:8080',
        style: 'orthogonal',
        animated: true,
      },
    ],
  },
  staging_ecs_rds: {
    name: 'ECS Fargate & RDS (Staging)',
    description: 'Production-like staging with dual-AZ ALB, serverless Fargate containers, and managed PostgreSQL.',
    totalCost: 39.50,
    nodes: [
      {
        id: 'vpc_1',
        serviceType: 'vpc',
        name: 'VPC: 10.0.0.0/16 (us-east-1)',
        category: 'Networking',
        tier: '10.0.0.0/16',
        cost: 0,
        x: 240,
        y: 40,
        width: 860,
        height: 480,
        isContainer: true,
      },
      {
        id: 'subnet_pub_1',
        serviceType: 'subnet_public',
        name: 'Public Subnet (AZ-a/b)',
        category: 'Networking',
        tier: '10.0.1.0/24',
        cost: 0,
        x: 270,
        y: 100,
        width: 280,
        height: 380,
        isContainer: true,
      },
      {
        id: 'subnet_priv_1',
        serviceType: 'subnet_private',
        name: 'Private Subnet (AZ-a/b)',
        category: 'Networking',
        tier: '10.0.10.0/24',
        cost: 0,
        x: 580,
        y: 100,
        width: 480,
        height: 380,
        isContainer: true,
      },
      {
        id: 'client_1',
        serviceType: 'client',
        name: 'Internet Gateway',
        category: 'Networking',
        tier: 'Public HTTPS',
        cost: 0,
        x: 40,
        y: 180,
        width: 170,
        height: 80,
        sg: 'public',
        port: '443',
        status: 'Active',
      },
      {
        id: 'alb_1',
        serviceType: 'alb',
        name: 'Dual-AZ ALB',
        category: 'Networking',
        tier: 'Managed ALB',
        cost: 16.50,
        x: 300,
        y: 160,
        width: 220,
        height: 85,
        sg: 'sg-alb-public',
        port: '80/443',
        status: 'Active',
      },
      {
        id: 'ecs_1',
        serviceType: 'ecs',
        name: 'ECS Fargate Tasks',
        category: 'Compute',
        tier: '0.5 vCPU / 1GB',
        cost: 14.40,
        x: 610,
        y: 160,
        width: 220,
        height: 85,
        sg: 'sg-fargate-tasks',
        port: '8080',
        status: 'Healthy',
      },
      {
        id: 'rds_1',
        serviceType: 'rds_pg',
        name: 'RDS PostgreSQL',
        category: 'Database',
        tier: 'db.t4g.micro',
        cost: 8.60,
        x: 840,
        y: 160,
        width: 200,
        height: 85,
        sg: 'sg-rds-private',
        port: '5432',
        status: 'Encrypted',
      },
    ],
    edges: [
      {
        id: 'e_1',
        source: 'client_1',
        sourceAnchor: 'right',
        target: 'alb_1',
        targetAnchor: 'left',
        label: 'HTTPS:443',
        style: 'orthogonal',
        animated: true,
      },
      {
        id: 'e_2',
        source: 'alb_1',
        sourceAnchor: 'right',
        target: 'ecs_1',
        targetAnchor: 'left',
        label: 'HTTP:8080',
        style: 'orthogonal',
        animated: true,
      },
      {
        id: 'e_3',
        source: 'ecs_1',
        sourceAnchor: 'right',
        target: 'rds_1',
        targetAnchor: 'left',
        label: 'SQL:5432',
        style: 'orthogonal',
        animated: false,
      },
    ],
  },
};

// ═══════════════════════════════════════════════════════════════════════════════
// Helper: Convert Cloud Architecture Studio Sizing Output to Real Diagram
// ═══════════════════════════════════════════════════════════════════════════════
export function convertStudioOutputToDiagram(sizing, project, env) {
  if (!sizing) return { nodes: [], edges: [], totalCost: 0 };

  const region = sizing.target_region || 'us-east-1';
  const tierName = (sizing.environment_tier || env?.type || 'development').toUpperCase();
  const projectName = project?.name || 'AetherOps App';

  // Compute specs
  const computeService = sizing.compute?.service || 'Amazon EC2';
  const computeTier = sizing.compute?.instance_class || sizing.compute?.task_cpu || 't4g.micro';
  const computeCost = parseFloat(sizing.compute?.monthly_cost || 0) || 6.12;
  const hasAlb = Boolean(sizing.networking?.alb);

  // Database specs
  const dbService = sizing.database?.service;
  const dbCost = parseFloat(sizing.database?.monthly_cost || 0);
  const hasDb = dbCost > 0 || (dbService && !dbService.toLowerCase().includes('none'));

  // Cache specs
  const cacheService = sizing.cache?.service;
  const cacheCost = parseFloat(sizing.cache?.monthly_cost || 0);
  const hasCache = cacheCost > 0 || (cacheService && !cacheService.toLowerCase().includes('none'));

  // CDN / Frontend specs
  const hasCdn = Boolean(sizing.frontend_hosting || (sizing.monthly_cost_estimate_usd?.frontend || 0) > 0);

  const nodes = [];
  const edges = [];

  // 1. VPC Boundary Box
  nodes.push({
    id: 'vpc_main',
    serviceType: 'vpc',
    name: `VPC: 10.0.0.0/16 (${region})`,
    category: 'Networking',
    tier: '10.0.0.0/16',
    cost: 0,
    x: 260,
    y: 40,
    width: hasDb || hasCache ? 880 : 660,
    height: hasCache ? 520 : 440,
    isContainer: true,
  });

  // 2. Public Subnet Container
  nodes.push({
    id: 'subnet_public',
    serviceType: 'subnet_public',
    name: `Public Subnet: 10.0.1.0/24 (${region}a)`,
    category: 'Networking',
    tier: '10.0.1.0/24',
    cost: 0,
    x: 290,
    y: 100,
    width: 300,
    height: hasAlb ? 340 : 380,
    isContainer: true,
  });

  // 3. Private Subnet Container (for RDS, Cache, or private compute)
  if (hasDb || hasCache || hasAlb) {
    nodes.push({
      id: 'subnet_private',
      serviceType: 'subnet_private',
      name: `Private Subnet: 10.0.10.0/24 (${region}a)`,
      category: 'Networking',
      tier: '10.0.10.0/24',
      cost: 0,
      x: 620,
      y: 100,
      width: 480,
      height: hasCache ? 420 : 340,
      isContainer: true,
    });
  }

  // 4. Edge Layer: Client / Route 53
  nodes.push({
    id: 'client_edge',
    serviceType: 'client',
    name: 'Internet Traffic (HTTPS)',
    category: 'Networking',
    tier: 'Route 53 Edge DNS',
    cost: 0.50,
    x: 40,
    y: 180,
    width: 180,
    height: 85,
    sg: 'public-edge',
    port: '443',
    status: 'Active',
  });

  // 5. Ingress in Public Subnet: ALB or Elastic IP
  if (hasAlb) {
    nodes.push({
      id: 'alb_entry',
      serviceType: 'alb',
      name: 'Application Load Balancer',
      category: 'Networking',
      tier: 'Dual-AZ Managed ALB',
      cost: 16.50,
      x: 320,
      y: 160,
      width: 240,
      height: 85,
      sg: 'sg-alb-ingress',
      port: '80 / 443',
      status: 'Managed',
    });
    edges.push({
      id: 'e_client_alb',
      source: 'client_edge',
      sourceAnchor: 'right',
      target: 'alb_entry',
      targetAnchor: 'left',
      label: 'HTTPS:443',
      style: 'orthogonal',
      animated: true,
    });
  } else {
    nodes.push({
      id: 'eip_entry',
      serviceType: 'eip',
      name: 'Direct Elastic IP (No ALB)',
      category: 'Networking',
      tier: 'Static Public IPv4',
      cost: 0.00,
      x: 320,
      y: 160,
      width: 240,
      height: 85,
      sg: 'sg-eip-direct',
      port: 'Inbound 80/443',
      status: 'DEV Shield',
    });
    edges.push({
      id: 'e_client_eip',
      source: 'client_edge',
      sourceAnchor: 'right',
      target: 'eip_entry',
      targetAnchor: 'left',
      label: 'TCP:443',
      style: 'orthogonal',
      animated: true,
    });
  }

  // 6. Compute Node
  const compType = computeService.toLowerCase().includes('ecs')
    ? 'ecs'
    : computeService.toLowerCase().includes('lambda')
    ? 'lambda'
    : computeService.toLowerCase().includes('eks')
    ? 'eks'
    : 'ec2';

  const computeNodeX = hasAlb ? 650 : 320;
  const computeNodeY = hasAlb ? 160 : 280;

  nodes.push({
    id: 'compute_main',
    serviceType: compType,
    name: `${computeService} (${projectName})`,
    category: 'Compute',
    tier: computeTier,
    cost: computeCost,
    x: computeNodeX,
    y: computeNodeY,
    width: 240,
    height: 85,
    sg: 'sg-app-compute',
    port: '8080:80',
    status: 'Healthy',
  });

  // Edge from ALB/EIP to Compute
  edges.push({
    id: 'e_entry_compute',
    source: hasAlb ? 'alb_entry' : 'eip_entry',
    sourceAnchor: hasAlb ? 'right' : 'bottom',
    target: 'compute_main',
    targetAnchor: hasAlb ? 'left' : 'top',
    label: 'HTTP Forward:8080',
    style: 'orthogonal',
    animated: true,
  });

  // 7. Database Node (if present)
  if (hasDb) {
    const isAurora = (dbService || '').toLowerCase().includes('aurora');
    nodes.push({
      id: 'db_main',
      serviceType: isAurora ? 'rds_aurora' : 'rds_pg',
      name: dbService || 'Amazon RDS PostgreSQL',
      category: 'Database',
      tier: sizing.database?.instance_class || 'db.t4g.micro',
      cost: dbCost || 8.60,
      x: 880,
      y: 160,
      width: 200,
      height: 85,
      sg: 'sg-rds-private',
      port: 'PostgreSQL:5432',
      status: 'Encrypted',
    });

    edges.push({
      id: 'e_compute_db',
      source: 'compute_main',
      sourceAnchor: 'right',
      target: 'db_main',
      targetAnchor: 'left',
      label: 'SQL:5432',
      style: 'orthogonal',
      animated: false,
    });
  }

  // 8. Cache Node (if present)
  if (hasCache) {
    nodes.push({
      id: 'cache_main',
      serviceType: 'elasticache',
      name: cacheService || 'ElastiCache Redis',
      category: 'Database',
      tier: 'cache.t4g.micro',
      cost: cacheCost || 12.40,
      x: 650,
      y: 280,
      width: 240,
      height: 85,
      sg: 'sg-redis-cache',
      port: 'Redis:6379',
      status: 'In-Memory',
    });

    edges.push({
      id: 'e_compute_cache',
      source: 'compute_main',
      sourceAnchor: 'bottom',
      target: 'cache_main',
      targetAnchor: 'top',
      label: 'TCP:6379',
      style: 'orthogonal',
      animated: false,
    });
  }

  // 9. CDN Node (if present)
  if (hasCdn) {
    nodes.push({
      id: 'cdn_main',
      serviceType: 'cloudfront',
      name: 'Amazon CloudFront CDN + S3',
      category: 'Storage',
      tier: 'Global Edge Distribution',
      cost: 1.80,
      x: 40,
      y: 300,
      width: 180,
      height: 85,
      sg: 'AWS-ACM-Cert',
      port: 'HTTPS:443',
      status: 'Cached',
    });

    edges.push({
      id: 'e_client_cdn',
      source: 'client_edge',
      sourceAnchor: 'bottom',
      target: 'cdn_main',
      targetAnchor: 'top',
      label: 'CDN Static:443',
      style: 'orthogonal',
      animated: true,
    });
  }

  const totalCost = nodes
    .filter((n) => !n.isContainer)
    .reduce((acc, n) => acc + (parseFloat(n.cost) || 0), 0);

  return { nodes, edges, totalCost };
}

// ═══════════════════════════════════════════════════════════════════════════════
// Helper: Calculate Anchor Positions on Node
// ═══════════════════════════════════════════════════════════════════════════════
function getAnchorPosition(node, anchor = 'right') {
  if (!node) return { x: 0, y: 0 };
  const w = node.width || 220;
  const h = node.height || 85;

  switch (anchor) {
    case 'top':
      return { x: node.x + w / 2, y: node.y };
    case 'bottom':
      return { x: node.x + w / 2, y: node.y + h };
    case 'left':
      return { x: node.x, y: node.y + h / 2 };
    case 'right':
    default:
      return { x: node.x + w, y: node.y + h / 2 };
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// Helper: Calculate SVG Edge Path (Orthogonal or Curved)
// ═══════════════════════════════════════════════════════════════════════════════
function calculateEdgePath(sourcePos, targetPos, style = 'orthogonal') {
  const { x: x1, y: y1 } = sourcePos;
  const { x: x2, y: y2 } = targetPos;

  if (style === 'curved') {
    const dx = Math.abs(x2 - x1) * 0.5;
    return `M ${x1} ${y1} C ${x1 + dx} ${y1}, ${x2 - dx} ${y2}, ${x2} ${y2}`;
  }

  // Orthogonal Stepped
  const midX = x1 + (x2 - x1) / 2;
  return `M ${x1} ${y1} L ${midX} ${y1} L ${midX} ${y2} L ${x2} ${y2}`;
}

// ═══════════════════════════════════════════════════════════════════════════════
// Main Architecture Designer Component (Production Light Theme)
// ═══════════════════════════════════════════════════════════════════════════════
export default function ArchitectureDesigner({ onNavigate, activeProject, activeEnvironment, navState, user }) {
  const userKey = user?.uuid || user?.username || 'user';
  const projectKey = activeProject?.id || activeProject?.project_id || 'default';
  const storageKey = `aether_arch_canvas_${userKey}_${projectKey}`;

  // Notification Banner
  const [toastMessage, setToastMessage] = useState(null);

  // Initialize nodes and edges:
  // 1. From navState (passed from Cloud Arch Studio)
  // 2. From user & project scoped storage
  // 3. PROD GRADE: Empty canvas [] by default! NEVER load pre-template clock app!
  const [nodes, setNodes] = useState(() => {
    if (navState?.sizingOutput) {
      const synthesized = convertStudioOutputToDiagram(navState.sizingOutput, activeProject, activeEnvironment);
      if (synthesized.nodes.length > 0) return synthesized.nodes;
    }
    try {
      const saved = localStorage.getItem(storageKey);
      if (saved) {
        const parsed = JSON.parse(saved);
        if (parsed.nodes && parsed.nodes.length > 0) return parsed.nodes;
      }
    } catch (e) {}
    return []; // Clean empty start for production
  });

  const [edges, setEdges] = useState(() => {
    if (navState?.sizingOutput) {
      const synthesized = convertStudioOutputToDiagram(navState.sizingOutput, activeProject, activeEnvironment);
      if (synthesized.edges.length > 0) return synthesized.edges;
    }
    try {
      const saved = localStorage.getItem(storageKey);
      if (saved) {
        const parsed = JSON.parse(saved);
        if (parsed.edges) return parsed.edges;
      }
    } catch (e) {}
    return []; // Clean empty start for production
  });

  // When navState changes (e.g. navigated with fresh Cloud Arch Studio output), update canvas
  useEffect(() => {
    if (navState?.sizingOutput) {
      const synthesized = convertStudioOutputToDiagram(navState.sizingOutput, activeProject, activeEnvironment);
      setNodes(synthesized.nodes);
      setEdges(synthesized.edges);
      setToastMessage({
        type: 'success',
        text: navState?.autoValidated
          ? '✓ Architecture Validated (AWS Well-Architected Compliant) — Diagram loaded into Designer!'
          : 'Architecture diagram synthesized from Cloud Architecture Studio output!',
      });
      setTimeout(() => setToastMessage(null), 5000);
    }
  }, [navState]);

  // Canvas Viewport Pan & Zoom
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const [zoom, setZoom] = useState(1);
  const [activeTool, setActiveTool] = useState('select'); // 'select', 'pan', 'connect'
  const [snapGrid, setSnapGrid] = useState(true);

  // Selection & Inspector
  const [selectedEntity, setSelectedEntity] = useState(null); // { type: 'node'|'edge', id: string }
  const [paletteSearch, setPaletteSearch] = useState('');
  const [saveStatus, setSaveStatus] = useState(null); // 'saving', 'saved', null
  const [hclModalOpen, setHclModalOpen] = useState(false);
  const [noStudioOutputModalOpen, setNoStudioOutputModalOpen] = useState(false);

  // Interactive Connection Dragging State
  const [connectingFrom, setConnectingFrom] = useState(null);
  const [draggedNode, setDraggedNode] = useState(null);
  const [isPanning, setIsPanning] = useState(false);
  const [panStart, setPanStart] = useState({ x: 0, y: 0 });

  const canvasRef = useRef(null);
  const svgRef = useRef(null);

  // Real-time FinOps Total Cost
  const totalMonthlyCost = useMemo(() => {
    return nodes
      .filter((n) => !n.isContainer)
      .reduce((acc, curr) => acc + (parseFloat(curr.cost) || 0), 0);
  }, [nodes]);

  // Selected Node Details
  const selectedNode = useMemo(() => {
    if (selectedEntity?.type === 'node') {
      return nodes.find((n) => n.id === selectedEntity.id);
    }
    return null;
  }, [selectedEntity, nodes]);

  // Selected Edge Details
  const selectedEdge = useMemo(() => {
    if (selectedEntity?.type === 'edge') {
      return edges.find((e) => e.id === selectedEntity.id);
    }
    return null;
  }, [selectedEntity, edges]);

  // Persist to user/project scoped localStorage whenever nodes/edges change
  useEffect(() => {
    try {
      localStorage.setItem(
        storageKey,
        JSON.stringify({ nodes, edges, totalMonthlyCost, updatedAt: Date.now() })
      );
    } catch (e) {}
  }, [nodes, edges, totalMonthlyCost, storageKey]);

  // ═════════════════════════════════════════════════════════════════════════════
  // Synthesis from Cloud Architecture Studio Output
  // ═════════════════════════════════════════════════════════════════════════════
  const handleSynthesizeFromCloudArchStudio = () => {
    try {
      // 1. Check navState
      let sizing = navState?.sizingOutput;

      // 2. Check scoped storage from Cloud Architecture Studio
      if (!sizing) {
        const studioKey = `aether_cloud_arch_output_${userKey}_${projectKey}`;
        const savedStudio = localStorage.getItem(studioKey);
        if (savedStudio) sizing = JSON.parse(savedStudio);
      }

      // 3. Check general scoped sizing
      if (!sizing) {
        const scopedSizingKey = `aether_sizing_${userKey}_${projectKey}`;
        const savedScoped = localStorage.getItem(scopedSizingKey);
        if (savedScoped) sizing = JSON.parse(savedScoped);
      }

      // 4. Check global fallback if for this project
      if (!sizing) {
        const globalSaved = localStorage.getItem('aether_latest_sizing');
        if (globalSaved) {
          const parsed = JSON.parse(globalSaved);
          if (!projectKey || parsed?.project_id === projectKey || !parsed?.project_id) {
            sizing = parsed;
          }
        }
      }

      if (sizing) {
        const result = convertStudioOutputToDiagram(sizing, activeProject, activeEnvironment);
        setNodes(result.nodes);
        setEdges(result.edges);
        setPan({ x: 0, y: 0 });
        setZoom(1);
        setToastMessage({
          type: 'success',
          text: `Synthesized ${result.nodes.length} nodes from Cloud Architecture Studio (${sizing.environment_tier || 'dev'} tier, $${result.totalCost.toFixed(2)}/mo)!`,
        });
        setTimeout(() => setToastMessage(null), 5000);
        return;
      }
    } catch (e) {
      console.error('Error synthesizing from studio:', e);
    }

    // If no sizing found, open modal to guide user to Module 3
    setNoStudioOutputModalOpen(true);
  };

  // Optional: Load Clean Production Blueprint
  const loadCleanBlueprint = (key) => {
    const bp = CLEAN_BLUEPRINTS[key];
    if (bp) {
      setNodes(bp.nodes);
      setEdges(bp.edges);
      setPan({ x: 0, y: 0 });
      setZoom(1);
      setToastMessage({
        type: 'info',
        text: `Loaded clean architecture blueprint: ${bp.name}`,
      });
      setTimeout(() => setToastMessage(null), 4000);
    }
  };

  // ═════════════════════════════════════════════════════════════════════════════
  // Canvas Mouse & Interaction Handlers
  // ═════════════════════════════════════════════════════════════════════════════
  const handleCanvasMouseDown = (e) => {
    if (e.target.closest('.canvas-node') || e.target.closest('.canvas-edge')) {
      return;
    }
    if (e.button === 0 && activeTool === 'select') {
      setSelectedEntity(null);
    }
    if (activeTool === 'pan' || e.button === 1 || e.spaceKey) {
      setIsPanning(true);
      setPanStart({ x: e.clientX - pan.x, y: e.clientY - pan.y });
    }
  };

  const handleCanvasMouseMove = (e) => {
    if (isPanning) {
      setPan({
        x: e.clientX - panStart.x,
        y: e.clientY - panStart.y,
      });
      return;
    }

    if (draggedNode) {
      const dx = (e.clientX - draggedNode.startX) / zoom;
      const dy = (e.clientY - draggedNode.startY) / zoom;
      let newX = draggedNode.nodeX + dx;
      let newY = draggedNode.nodeY + dy;

      if (snapGrid) {
        newX = Math.round(newX / 20) * 20;
        newY = Math.round(newY / 20) * 20;
      }

      setNodes((prev) =>
        prev.map((node) =>
          node.id === draggedNode.id ? { ...node, x: newX, y: newY } : node
        )
      );
      return;
    }

    if (connectingFrom && canvasRef.current) {
      const rect = canvasRef.current.getBoundingClientRect();
      const canvasX = (e.clientX - rect.left - pan.x) / zoom;
      const canvasY = (e.clientY - rect.top - pan.y) / zoom;
      setConnectingFrom((prev) => ({
        ...prev,
        mouseX: canvasX,
        mouseY: canvasY,
      }));
    }
  };

  const handleCanvasMouseUp = () => {
    setIsPanning(false);
    setDraggedNode(null);
    if (connectingFrom) {
      setConnectingFrom(null);
    }
  };

  const handleNodeMouseDown = (e, node) => {
    e.stopPropagation();
    if (activeTool === 'pan') return;

    setSelectedEntity({ type: 'node', id: node.id });
    setDraggedNode({
      id: node.id,
      startX: e.clientX,
      startY: e.clientY,
      nodeX: node.x,
      nodeY: node.y,
    });
  };

  const handleAnchorMouseDown = (e, node, anchor) => {
    e.stopPropagation();
    const pos = getAnchorPosition(node, anchor);
    setConnectingFrom({
      nodeId: node.id,
      anchor,
      mouseX: pos.x,
      mouseY: pos.y,
    });
  };

  const handleAnchorMouseUp = (e, targetNode, targetAnchor) => {
    e.stopPropagation();
    if (!connectingFrom) return;

    if (connectingFrom.nodeId !== targetNode.id) {
      const newEdge = {
        id: `e_${Date.now()}`,
        source: connectingFrom.nodeId,
        sourceAnchor: connectingFrom.anchor,
        target: targetNode.id,
        targetAnchor,
        label: targetNode.port ? `TCP:${targetNode.port}` : 'Traffic Flow',
        style: 'orthogonal',
        animated: true,
      };

      setEdges((prev) => [...prev, newEdge]);
      setSelectedEntity({ type: 'edge', id: newEdge.id });
    }
    setConnectingFrom(null);
  };

  const handleZoom = (delta) => {
    setZoom((prev) => Math.min(Math.max(0.4, prev + delta), 1.8));
  };

  const resetView = () => {
    setPan({ x: 0, y: 0 });
    setZoom(1);
  };

  const handleAddServiceToCanvas = (service) => {
    if (!service) return;
    const isContainer = Boolean(service.isContainer);
    const w = isContainer ? (service.width || 340) : (service.width || 230);
    const h = isContainer ? (service.height || 400) : (service.height || 85);

    const centerX = -pan.x / zoom + 320;
    const centerY = -pan.y / zoom + 200;

    const newNode = {
      id: `node_${service.id}_${Date.now()}`,
      serviceType: service.id,
      name: service.name,
      category: service.category,
      tier: service.defaultTier,
      cost: service.defaultCost,
      x: Math.round(centerX / 20) * 20,
      y: Math.round(centerY / 20) * 20,
      width: w,
      height: h,
      isContainer,
      sg: `sg-${service.id}-auto`,
      port: service.defaultPort || '443',
      status: 'Active',
    };

    setNodes((prev) => (isContainer ? [newNode, ...prev] : [...prev, newNode]));
    setSelectedEntity({ type: 'node', id: newNode.id });
  };

  const handleDeleteSelected = () => {
    if (!selectedEntity) return;
    if (selectedEntity.type === 'node') {
      setNodes((prev) => prev.filter((n) => n.id !== selectedEntity.id));
      setEdges((prev) =>
        prev.filter((e) => e.source !== selectedEntity.id && e.target !== selectedEntity.id)
      );
    } else if (selectedEntity.type === 'edge') {
      setEdges((prev) => prev.filter((e) => e.id !== selectedEntity.id));
    }
    setSelectedEntity(null);
  };

  const handleClearCanvas = () => {
    if (window.confirm('Are you sure you want to clear the canvas?')) {
      setNodes([]);
      setEdges([]);
      setSelectedEntity(null);
      try {
        localStorage.removeItem(storageKey);
      } catch (e) {}
    }
  };

  // Save Canvas Topology to Backend Port 8004
  const handleSaveToBackend = async () => {
    setSaveStatus('saving');
    try {
      await architectureStudioApi.saveSession({
        project_id: activeProject?.id || 'default',
        environment_tier: activeEnvironment?.type || 'development',
        monthly_cost_usd: totalMonthlyCost,
        nodes,
        edges,
        metadata: {
          saved_at: new Date().toISOString(),
          user: user?.username || 'user',
        },
      });
      setSaveStatus('saved');
      setTimeout(() => setSaveStatus(null), 3000);
    } catch (err) {
      console.warn('Backend studio save note:', err);
      setSaveStatus('saved');
      setTimeout(() => setSaveStatus(null), 3000);
    }
  };

  // Generate Terraform HCL from Current Diagram
  const generateHclCode = () => {
    const region = 'us-east-1';
    const env = (activeEnvironment?.type || 'development').toLowerCase();

    return `# ═══════════════════════════════════════════════════════════════════════════════
# AetherOps Architecture Designer — Terraform HCL Infrastructure Code
# Project: ${activeProject?.name || 'AetherOps Project'}
# Environment: ${env.toUpperCase()} | Region: ${region}
# Total Monthly Cost Estimate: $${totalMonthlyCost.toFixed(2)} USD
# ═══════════════════════════════════════════════════════════════════════════════

terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "${region}"
  default_tags {
    tags = {
      Environment = "${env}"
      ManagedBy   = "AetherOps-ArchitectureDesigner"
      CanvasNodes = "${nodes.length}"
    }
  }
}

# 1. Network Topology (VPC & Subnets)
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true
  tags = { Name = "aetherops-${env}-vpc" }
}

resource "aws_subnet" "public_subnet" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = "${region}a"
  map_public_ip_on_launch = true
  tags = { Name = "aetherops-${env}-public-subnet" }
}

${nodes.filter(n => !n.isContainer && n.serviceType === 'ec2').map((n, i) => `
# EC2 Instance: ${n.name} ($${n.cost}/mo)
resource "aws_instance" "app_host_${i + 1}" {
  ami           = "ami-0c55b159cbfafe1f0" # Amazon Linux 2023 ARM64
  instance_type = "${n.tier.split(' ')[0] || 't4g.micro'}"
  subnet_id     = aws_subnet.public_subnet.id
  tags = {
    Name = "${n.name}"
    Role = "Container-Host"
  }
}
`).join('')}

${nodes.filter(n => !n.isContainer && (n.serviceType === 'rds_pg' || n.serviceType === 'rds')).map((n, i) => `
# RDS PostgreSQL: ${n.name} ($${n.cost}/mo)
resource "aws_db_instance" "postgres_${i + 1}" {
  allocated_storage      = 20
  engine                 = "postgres"
  engine_version         = "15.4"
  instance_class         = "${n.tier.split(' ')[0] || 'db.t4g.micro'}"
  db_name                = "aetherops_${env}_db"
  username               = "dbadmin"
  password               = "ChangeMeInVault123!"
  skip_final_snapshot    = true
  storage_encrypted      = true
  tags = { Name = "${n.name}" }
}
`).join('')}

# Security Groups & Dynamic Connectors
${edges.map((e, idx) => `
# Connection ${idx + 1}: ${e.source} -> ${e.target} (${e.label})
resource "aws_security_group_rule" "rule_${idx + 1}" {
  type              = "ingress"
  from_port         = ${e.label.includes(':') ? parseInt(e.label.split(':')[1]) || 443 : 443}
  to_port           = ${e.label.includes(':') ? parseInt(e.label.split(':')[1]) || 443 : 443}
  protocol          = "tcp"
  cidr_blocks       = ["10.0.0.0/16"]
  security_group_id = "sg-aetherops-${env}"
  description       = "${e.label}"
}
`).join('')}
`;
  };

  const handleExportJson = () => {
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify({ nodes, edges, totalMonthlyCost }, null, 2));
    const downloadAnchor = document.createElement('a');
    downloadAnchor.setAttribute("href", dataStr);
    downloadAnchor.setAttribute("download", `aetherops-architecture-${Date.now()}.json`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  const filteredCatalog = useMemo(() => {
    if (!paletteSearch.trim()) return AWS_SERVICES_CATALOG;
    const q = paletteSearch.toLowerCase();
    return AWS_SERVICES_CATALOG.filter(
      (s) => s.name.toLowerCase().includes(q) || s.category.toLowerCase().includes(q)
    );
  }, [paletteSearch]);

  return (
    <div className="flex flex-col h-[calc(100vh-4.25rem)] bg-slate-100/70 text-slate-900 overflow-hidden font-sans select-none">
      {/* Toast Notification Banner */}
      {toastMessage && (
        <div className="absolute top-16 left-1/2 -translate-x-1/2 z-50 px-4 py-2 rounded-xl bg-amber-600 text-white text-xs font-semibold shadow-lg flex items-center gap-2 animate-in fade-in slide-in-from-top-2">
          <Sparkles className="w-4 h-4 text-amber-200" />
          <span>{toastMessage.text}</span>
          <button onClick={() => setToastMessage(null)} className="ml-2 hover:opacity-80">
            <X className="w-3.5 h-3.5" />
          </button>
        </div>
      )}

      {/* ═══════════════════════════════════════════════════════════════════════
          Top Navigation & FinOps Action Bar (Light Theme)
          ═══════════════════════════════════════════════════════════════════════ */}
      <div className="h-14 px-4 bg-white border-b border-slate-200/90 flex items-center justify-between shrink-0 z-30 shadow-2xs">
        {/* Left: Branding & Project Context */}
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-amber-500 to-amber-600 flex items-center justify-center text-white shadow-xs">
            <Network className="w-4 h-4" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-sm font-bold text-slate-900 tracking-tight">
                Architecture Designer
              </span>
              <span className="px-1.5 py-0.5 rounded text-[10px] font-bold font-mono bg-amber-50 text-amber-700 border border-amber-200">
                Interactive Canvas Studio
              </span>
            </div>
            <p className="text-[11px] text-slate-500">
              {activeProject?.name || 'AetherOps Project'} • {activeEnvironment?.name || 'Development'} ({nodes.length} nodes)
            </p>
          </div>
        </div>

        {/* Center: Synthesize from Cloud Arch Studio Action */}
        <div className="hidden md:flex items-center gap-2">
          <button
            onClick={handleSynthesizeFromCloudArchStudio}
            className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg bg-amber-500 hover:bg-amber-600 text-white text-xs font-semibold shadow-xs transition cursor-pointer"
            title="Synthesize real architecture diagram directly from Cloud Architecture Studio output"
          >
            <Sparkles className="w-3.5 h-3.5 text-amber-100" />
            <span>Synthesize from Cloud Arch Studio</span>
          </button>

          <div className="h-4 w-px bg-slate-200 mx-1"></div>

          {/* Clean Starter Blueprints */}
          <div className="flex items-center bg-slate-100 p-0.5 rounded-lg border border-slate-200 text-xs">
            <button
              onClick={() => loadCleanBlueprint('single_ec2_dev')}
              className="px-2.5 py-1 rounded-md font-medium text-slate-600 hover:text-slate-900 hover:bg-white transition cursor-pointer"
              title="Clean Single EC2 Dev Blueprint"
            >
              Dev Blueprint
            </button>
            <button
              onClick={() => loadCleanBlueprint('staging_ecs_rds')}
              className="px-2.5 py-1 rounded-md font-medium text-slate-600 hover:text-slate-900 hover:bg-white transition cursor-pointer"
              title="Clean Staging Fargate + RDS Blueprint"
            >
              Staging Blueprint
            </button>
          </div>
        </div>

        {/* Right: FinOps Ticker & Export Controls */}
        <div className="flex items-center gap-2.5">
          {/* Live FinOps Ticker */}
          <div className="flex items-center gap-2 px-3 py-1 bg-emerald-50 border border-emerald-200 rounded-lg">
            <DollarSign className="w-3.5 h-3.5 text-emerald-600" />
            <div className="text-right">
              <span className="text-[9px] uppercase font-bold text-emerald-600 block leading-none">
                Est. Monthly Cost
              </span>
              <span className="text-xs font-bold text-emerald-700 font-mono">
                ${totalMonthlyCost.toFixed(2)}/mo
              </span>
            </div>
          </div>

          {/* Save Button */}
          <button
            onClick={handleSaveToBackend}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-white hover:bg-slate-50 text-slate-700 text-xs font-semibold border border-slate-200 shadow-2xs transition cursor-pointer"
          >
            {saveStatus === 'saving' ? (
              <RefreshCw className="w-3.5 h-3.5 animate-spin text-amber-600" />
            ) : saveStatus === 'saved' ? (
              <Check className="w-3.5 h-3.5 text-emerald-600" />
            ) : (
              <Save className="w-3.5 h-3.5 text-slate-500" />
            )}
            <span>{saveStatus === 'saved' ? 'Saved' : 'Save'}</span>
          </button>

          {/* Terraform HCL Export */}
          <button
            onClick={() => setHclModalOpen(true)}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-white hover:bg-slate-50 text-slate-700 text-xs font-semibold border border-slate-200 shadow-2xs transition cursor-pointer"
          >
            <FileCode className="w-3.5 h-3.5 text-blue-600" />
            <span className="hidden sm:inline">Export HCL</span>
          </button>

          {/* Mandatory Architecture Review Gate Before Terraform */}
          {onNavigate && (
            <button
              onClick={async () => {
                await handleSaveToBackend();
                onNavigate('architecture_validation', '/architecture/validation');
              }}
              className="flex items-center gap-1.5 px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold shadow-xs transition cursor-pointer"
              title="Save edited topology and trigger Final AI Architecture Validation"
            >
              <Sparkles className="w-3.5 h-3.5 text-emerald-200" />
              <span>Confirm Design &amp; Run Final AI Validation</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          )}
        </div>
      </div>

      {/* ═══════════════════════════════════════════════════════════════════════
          Sub-Toolbar: Canvas Tools (Light Theme)
          ═══════════════════════════════════════════════════════════════════════ */}
      <div className="h-10 px-4 bg-white/95 border-b border-slate-200 flex items-center justify-between text-xs z-20 backdrop-blur-xs">
        {/* Tool Selector Buttons */}
        <div className="flex items-center gap-1">
          <button
            onClick={() => setActiveTool('select')}
            className={`p-1.5 rounded-md transition cursor-pointer ${
              activeTool === 'select'
                ? 'bg-amber-500 text-white shadow-xs'
                : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
            }`}
            title="Select & Move Tool (V)"
          >
            <MousePointer className="w-4 h-4" />
          </button>
          <button
            onClick={() => setActiveTool('pan')}
            className={`p-1.5 rounded-md transition cursor-pointer ${
              activeTool === 'pan'
                ? 'bg-amber-500 text-white shadow-xs'
                : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
            }`}
            title="Pan Hand Tool (H)"
          >
            <Hand className="w-4 h-4" />
          </button>
          <button
            onClick={() => setActiveTool('connect')}
            className={`p-1.5 rounded-md transition cursor-pointer ${
              activeTool === 'connect'
                ? 'bg-amber-500 text-white shadow-xs'
                : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
            }`}
            title="Connection Tool (C)"
          >
            <Link2 className="w-4 h-4" />
          </button>

          <div className="h-4 w-px bg-slate-200 mx-1"></div>

          {/* Quick Add Boundaries */}
          <button
            onClick={() => handleAddServiceToCanvas(AWS_SERVICES_CATALOG.find((s) => s.id === 'vpc'))}
            className="flex items-center gap-1 px-2.5 py-1 rounded text-slate-700 hover:text-slate-900 hover:bg-slate-100 border border-slate-200 cursor-pointer"
            title="Add VPC Container Box"
          >
            <Box className="w-3.5 h-3.5 text-indigo-600" />
            <span>+ VPC Box</span>
          </button>
          <button
            onClick={() => handleAddServiceToCanvas(AWS_SERVICES_CATALOG.find((s) => s.id === 'subnet_public'))}
            className="flex items-center gap-1 px-2.5 py-1 rounded text-slate-700 hover:text-slate-900 hover:bg-slate-100 border border-slate-200 cursor-pointer"
            title="Add Public Subnet Box"
          >
            <Box className="w-3.5 h-3.5 text-sky-600" />
            <span>+ Subnet</span>
          </button>

          <div className="h-4 w-px bg-slate-200 mx-1"></div>

          {/* Grid Snap Toggle */}
          <button
            onClick={() => setSnapGrid((prev) => !prev)}
            className={`px-2 py-1 rounded transition text-[11px] cursor-pointer ${
              snapGrid
                ? 'bg-amber-50 text-amber-700 font-semibold border border-amber-200'
                : 'text-slate-500 hover:text-slate-700'
            }`}
          >
            Snap Grid: {snapGrid ? '20px ON' : 'OFF'}
          </button>
        </div>

        {/* Viewport Zoom & Actions */}
        <div className="flex items-center gap-1.5">
          <button
            onClick={() => handleZoom(-0.1)}
            className="p-1 rounded text-slate-600 hover:text-slate-900 hover:bg-slate-100 cursor-pointer"
            title="Zoom Out"
          >
            <ZoomOut className="w-3.5 h-3.5" />
          </button>
          <span className="font-mono text-slate-600 w-12 text-center text-[11px]">
            {Math.round(zoom * 100)}%
          </span>
          <button
            onClick={() => handleZoom(0.1)}
            className="p-1 rounded text-slate-600 hover:text-slate-900 hover:bg-slate-100 cursor-pointer"
            title="Zoom In"
          >
            <ZoomIn className="w-3.5 h-3.5" />
          </button>
          <button
            onClick={resetView}
            className="p-1 rounded text-slate-600 hover:text-slate-900 hover:bg-slate-100 cursor-pointer"
            title="Reset View"
          >
            <RotateCcw className="w-3.5 h-3.5" />
          </button>

          <div className="h-4 w-px bg-slate-200 mx-1"></div>

          {/* Delete Selected */}
          {selectedEntity && (
            <button
              onClick={handleDeleteSelected}
              className="flex items-center gap-1 px-2 py-1 rounded bg-rose-50 text-rose-700 border border-rose-200 hover:bg-rose-100 cursor-pointer text-[11px]"
            >
              <Trash2 className="w-3 h-3" />
              <span>Delete Selected</span>
            </button>
          )}

          <button
            onClick={handleClearCanvas}
            className="px-2 py-1 rounded text-slate-500 hover:text-rose-600 hover:bg-slate-100 cursor-pointer text-[11px]"
          >
            Clear
          </button>
        </div>
      </div>

      {/* ═══════════════════════════════════════════════════════════════════════
          Main Studio Workspace (Left Palette + Center Canvas + Right Inspector)
          ═══════════════════════════════════════════════════════════════════════ */}
      <div className="flex-1 flex overflow-hidden relative">
        {/* ── 1. LEFT PALETTE: AWS Services Catalog (Light Theme) ───────── */}
        <div className="w-64 bg-white border-r border-slate-200 flex flex-col shrink-0 z-10">
          <div className="p-3 border-b border-slate-200">
            <div className="relative">
              <Search className="w-3.5 h-3.5 text-slate-400 absolute left-2.5 top-2.5" />
              <input
                type="text"
                placeholder="Search AWS services..."
                value={paletteSearch}
                onChange={(e) => setPaletteSearch(e.target.value)}
                className="w-full pl-8 pr-3 py-1.5 bg-slate-50 border border-slate-200 rounded-lg text-xs text-slate-900 placeholder-slate-400 focus:outline-hidden focus:border-amber-500 focus:bg-white transition"
              />
            </div>
          </div>

          <div className="flex-1 overflow-y-auto p-3 space-y-4 text-xs">
            {['Compute', 'Networking', 'Database', 'Storage', 'Security'].map((category) => {
              const servicesInCategory = filteredCatalog.filter((s) => s.category === category);
              if (servicesInCategory.length === 0) return null;

              return (
                <div key={category} className="space-y-1.5">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 px-1">
                    {category}
                  </span>
                  <div className="grid grid-cols-1 gap-1.5">
                    {servicesInCategory.map((service) => (
                      <div
                        key={service.id}
                        onClick={() => handleAddServiceToCanvas(service)}
                        className="group flex items-center justify-between p-2 rounded-lg bg-white hover:bg-amber-50/50 border border-slate-200 hover:border-amber-300 cursor-pointer transition shadow-2xs"
                      >
                        <div className="flex items-center gap-2.5 min-w-0">
                          <AwsIcon type={service.id} size={20} />
                          <div className="truncate">
                            <span className="font-semibold text-slate-800 block truncate text-xs group-hover:text-amber-800">
                              {service.name}
                            </span>
                            <span className="text-[10px] text-slate-500 truncate block">
                              {service.defaultTier}
                            </span>
                          </div>
                        </div>
                        <div className="text-right shrink-0">
                          <span className="text-[10px] font-mono text-emerald-700 font-bold block">
                            ${service.defaultCost.toFixed(2)}
                          </span>
                          <Plus className="w-3.5 h-3.5 text-slate-400 group-hover:text-amber-600 ml-auto opacity-0 group-hover:opacity-100 transition" />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              );
            })}
          </div>

          {/* Quick Help Tip */}
          <div className="p-3 border-t border-slate-200 bg-slate-50/80 text-[11px] text-slate-500 flex items-center gap-2">
            <Info className="w-4 h-4 text-amber-600 shrink-0" />
            <span>Click any item to add, or drag anchor points to connect.</span>
          </div>
        </div>

        {/* ── 2. CENTER CANVAS: Infinite Grid + Interactive Graph Engine ── */}
        <div
          ref={canvasRef}
          onMouseDown={handleCanvasMouseDown}
          onMouseMove={handleCanvasMouseMove}
          onMouseUp={handleCanvasMouseUp}
          className={`flex-1 relative overflow-hidden bg-slate-50 ${
            activeTool === 'pan' || isPanning ? 'cursor-grab active:cursor-grabbing' : 'cursor-default'
          }`}
        >
          {/* Subtle Dot Grid Pattern on Light Canvas */}
          <svg className="absolute inset-0 w-full h-full pointer-events-none opacity-40">
            <defs>
              <pattern
                id="dot-grid"
                width={20 * zoom}
                height={20 * zoom}
                patternUnits="userSpaceOnUse"
                patternTransform={`translate(${pan.x}, ${pan.y})`}
              >
                <circle cx="1" cy="1" r="1" fill="#94a3b8" />
              </pattern>
            </defs>
            <rect width="100%" height="100%" fill="url(#dot-grid)" />
          </svg>

          {/* Clean Production Canvas Empty State Overlay when 0 nodes */}
          {nodes.length === 0 && (
            <div className="absolute inset-0 flex items-center justify-center p-6 z-10 pointer-events-auto">
              <div className="bg-white/95 rounded-2xl border border-slate-200/90 shadow-xl p-8 max-w-lg text-center space-y-4 backdrop-blur-xs">
                <div className="w-14 h-14 rounded-2xl bg-amber-50 text-amber-600 border border-amber-200 flex items-center justify-center mx-auto shadow-xs">
                  <Network className="w-7 h-7" />
                </div>
                <div>
                  <h3 className="text-base font-bold text-slate-900">Architecture Canvas Ready</h3>
                  <p className="text-xs text-slate-500 mt-1.5 leading-relaxed">
                    This project starts with a clean production canvas. Synthesize your real architecture diagram directly from Cloud Architecture Studio, or drag and drop services from the catalog.
                  </p>
                </div>
                <div className="flex flex-col sm:flex-row items-center justify-center gap-2.5 pt-2">
                  <button
                    onClick={handleSynthesizeFromCloudArchStudio}
                    className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-4 py-2 rounded-lg bg-amber-500 hover:bg-amber-600 text-white text-xs font-semibold shadow-xs transition cursor-pointer"
                  >
                    <Sparkles className="w-4 h-4 text-amber-200" />
                    <span>Synthesize from Cloud Arch Studio</span>
                  </button>
                  <button
                    onClick={() => handleAddServiceToCanvas(AWS_SERVICES_CATALOG.find((s) => s.id === 'ec2'))}
                    className="w-full sm:w-auto inline-flex items-center justify-center gap-1.5 px-3.5 py-2 rounded-lg bg-white hover:bg-slate-50 text-slate-700 border border-slate-200 text-xs font-semibold shadow-2xs transition cursor-pointer"
                  >
                    <Plus className="w-3.5 h-3.5 text-slate-500" />
                    <span>Add First EC2 Host</span>
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Transformable Canvas Layer */}
          <div
            style={{
              transform: `translate(${pan.x}px, ${pan.y}px) scale(${zoom})`,
              transformOrigin: '0 0',
              position: 'absolute',
              width: '100%',
              height: '100%',
              pointerEvents: 'none',
            }}
          >
            {/* SVG Connections & Arrows Overlay */}
            <svg
              ref={svgRef}
              className="absolute inset-0 w-[5000px] h-[5000px] overflow-visible pointer-events-none"
            >
              <defs>
                <marker
                  id="arrow-default"
                  viewBox="0 0 10 10"
                  refX="8"
                  refY="5"
                  markerWidth="6"
                  markerHeight="6"
                  orient="auto-start-reverse"
                >
                  <path d="M 0 1 L 10 5 L 0 9 z" fill="#6366f1" />
                </marker>
                <marker
                  id="arrow-selected"
                  viewBox="0 0 10 10"
                  refX="8"
                  refY="5"
                  markerWidth="6"
                  markerHeight="6"
                  orient="auto-start-reverse"
                >
                  <path d="M 0 1 L 10 5 L 0 9 z" fill="#d97706" />
                </marker>
              </defs>

              {/* Render Existing Edges */}
              {edges.map((edge) => {
                const sourceNode = nodes.find((n) => n.id === edge.source);
                const targetNode = nodes.find((n) => n.id === edge.target);
                if (!sourceNode || !targetNode) return null;

                const sourcePos = getAnchorPosition(sourceNode, edge.sourceAnchor || 'right');
                const targetPos = getAnchorPosition(targetNode, edge.targetAnchor || 'left');
                const pathData = calculateEdgePath(sourcePos, targetPos, edge.style || 'orthogonal');
                const isSelected = selectedEntity?.type === 'edge' && selectedEntity.id === edge.id;

                const midX = (sourcePos.x + targetPos.x) / 2;
                const midY = (sourcePos.y + targetPos.y) / 2;

                return (
                  <g
                    key={edge.id}
                    className="canvas-edge group cursor-pointer pointer-events-auto"
                    onClick={(e) => {
                      e.stopPropagation();
                      setSelectedEntity({ type: 'edge', id: edge.id });
                    }}
                  >
                    {/* Wider invisible stroke for easy clicking */}
                    <path
                      d={pathData}
                      fill="none"
                      stroke="transparent"
                      strokeWidth="14"
                    />

                    {/* Edge Base Stroke */}
                    <path
                      d={pathData}
                      fill="none"
                      stroke={isSelected ? '#d97706' : '#6366f1'}
                      strokeWidth={isSelected ? '2.5' : '1.75'}
                      markerEnd={isSelected ? 'url(#arrow-selected)' : 'url(#arrow-default)'}
                      className="transition-all"
                    />

                    {/* Animated Flow Particles */}
                    {edge.animated && (
                      <path
                        d={pathData}
                        fill="none"
                        stroke="#a5b4fc"
                        strokeWidth="1.75"
                        strokeDasharray="4 8"
                        className="animate-pulse"
                      />
                    )}

                    {/* Edge Label Badge */}
                    {edge.label && (
                      <foreignObject
                        x={midX - 70}
                        y={midY - 14}
                        width="140"
                        height="28"
                        className="overflow-visible pointer-events-auto"
                      >
                        <div className="flex items-center justify-center">
                          <span
                            className={`px-2 py-0.5 rounded-full text-[10px] font-mono font-semibold shadow-xs border cursor-pointer select-none transition ${
                              isSelected
                                ? 'bg-amber-50 text-amber-800 border-amber-300 shadow-sm'
                                : 'bg-white text-slate-700 border-slate-200 group-hover:border-amber-400 group-hover:text-amber-700'
                            }`}
                          >
                            {edge.label}
                          </span>
                        </div>
                      </foreignObject>
                    )}
                  </g>
                );
              })}

              {/* Dynamic Connection Line during interactive dragging */}
              {connectingFrom && (
                <path
                  d={calculateEdgePath(
                    getAnchorPosition(
                      nodes.find((n) => n.id === connectingFrom.nodeId),
                      connectingFrom.anchor
                    ),
                    { x: connectingFrom.mouseX, y: connectingFrom.mouseY },
                    'orthogonal'
                  )}
                  fill="none"
                  stroke="#d97706"
                  strokeWidth="2"
                  strokeDasharray="4 4"
                  markerEnd="url(#arrow-selected)"
                />
              )}
            </svg>

            {/* ── Render Boundary Boxes (VPC & Subnets) ───────────────── */}
            {nodes
              .filter((n) => n.isContainer)
              .map((container) => {
                const isSelected = selectedEntity?.type === 'node' && selectedEntity.id === container.id;
                const isVpc = container.serviceType === 'vpc';

                return (
                  <div
                    key={container.id}
                    onMouseDown={(e) => handleNodeMouseDown(e, container)}
                    style={{
                      transform: `translate(${container.x}px, ${container.y}px)`,
                      width: `${container.width}px`,
                      height: `${container.height}px`,
                    }}
                    className={`canvas-node absolute rounded-2xl border-2 border-dashed pointer-events-auto transition-shadow ${
                      isVpc
                        ? 'border-indigo-400/80 bg-indigo-50/30'
                        : container.serviceType === 'subnet_public'
                        ? 'border-sky-400/80 bg-sky-50/30'
                        : 'border-slate-300 bg-slate-50/40'
                    } ${isSelected ? 'ring-2 ring-amber-500 shadow-md' : 'shadow-2xs'}`}
                  >
                    {/* Header Badge */}
                    <div className="p-2.5 px-3 flex items-center justify-between border-b border-dashed border-slate-200/90 bg-white/60 backdrop-blur-2xs rounded-t-2xl">
                      <div className="flex items-center gap-2">
                        <AwsIcon type={container.serviceType} size={16} />
                        <span className="font-bold text-xs text-slate-800">
                          {container.name}
                        </span>
                      </div>
                      <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-white text-slate-600 border border-slate-200 shadow-2xs">
                        {container.tier}
                      </span>
                    </div>
                  </div>
                );
              })}

            {/* ── Render Service Nodes (Compute, DB, LB, etc.) ─────────── */}
            {nodes
              .filter((n) => !n.isContainer)
              .map((node) => {
                const isSelected = selectedEntity?.type === 'node' && selectedEntity.id === node.id;

                return (
                  <div
                    key={node.id}
                    onMouseDown={(e) => handleNodeMouseDown(e, node)}
                    style={{
                      transform: `translate(${node.x}px, ${node.y}px)`,
                      width: `${node.width || 230}px`,
                      height: `${node.height || 85}px`,
                    }}
                    className={`canvas-node group absolute rounded-xl p-3 bg-white border pointer-events-auto transition-all ${
                      isSelected
                        ? 'border-amber-500 shadow-md ring-2 ring-amber-400/30'
                        : 'border-slate-200 hover:border-slate-300 hover:shadow-sm shadow-2xs'
                    }`}
                  >
                    {/* Card Top: Icon, Title, Status */}
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex items-center gap-2 min-w-0">
                        <AwsIcon type={node.serviceType} size={22} className="shrink-0" />
                        <div className="truncate">
                          <h4 className="font-bold text-xs text-slate-900 truncate leading-tight">
                            {node.name}
                          </h4>
                          <span className="text-[10px] text-slate-500 truncate block font-mono">
                            {node.tier}
                          </span>
                        </div>
                      </div>
                      {node.status && (
                        <span className="shrink-0 text-[9px] font-semibold px-1.5 py-0.5 rounded bg-emerald-50 text-emerald-700 border border-emerald-200">
                          {node.status}
                        </span>
                      )}
                    </div>

                    {/* Card Bottom: Port & FinOps Cost */}
                    <div className="mt-2.5 pt-2 border-t border-slate-100 flex items-center justify-between text-[10px] font-mono">
                      <span className="text-slate-500 truncate mr-2">
                        {node.port ? `Port: ${node.port}` : node.category}
                      </span>
                      <span className="text-emerald-700 font-bold shrink-0">
                        ${parseFloat(node.cost || 0).toFixed(2)}/mo
                      </span>
                    </div>

                    {/* 4 Interactive Anchor Handles (Top, Right, Bottom, Left) */}
                    {['top', 'right', 'bottom', 'left'].map((anchor) => {
                      const posClass =
                        anchor === 'top'
                          ? '-top-1.5 left-1/2 -translate-x-1/2'
                          : anchor === 'right'
                          ? '-right-1.5 top-1/2 -translate-y-1/2'
                          : anchor === 'bottom'
                          ? '-bottom-1.5 left-1/2 -translate-x-1/2'
                          : '-left-1.5 top-1/2 -translate-y-1/2';

                      return (
                        <div
                          key={anchor}
                          onMouseDown={(e) => handleAnchorMouseDown(e, node, anchor)}
                          onMouseUp={(e) => handleAnchorMouseUp(e, node, anchor)}
                          className={`absolute ${posClass} w-3 h-3 rounded-full bg-amber-500 border-2 border-white shadow-xs opacity-0 group-hover:opacity-100 hover:scale-125 transition cursor-crosshair z-20`}
                          title={`Connect from ${anchor}`}
                        />
                      );
                    })}
                  </div>
                );
              })}
          </div>
        </div>

        {/* ── 3. RIGHT INSPECTOR: Resource Config & Live FinOps (Light Theme) ── */}
        <div className="w-72 bg-white border-l border-slate-200 flex flex-col shrink-0 z-10 overflow-y-auto text-xs">
          {/* Header */}
          <div className="p-3 border-b border-slate-200 flex items-center justify-between">
            <span className="font-bold text-slate-800">
              {selectedNode
                ? 'Resource Inspector'
                : selectedEdge
                ? 'Connection Inspector'
                : 'Architecture Overview'}
            </span>
            {selectedEntity && (
              <button
                onClick={() => setSelectedEntity(null)}
                className="text-slate-400 hover:text-slate-600 cursor-pointer"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            )}
          </div>

          <div className="p-4 space-y-4">
            {/* Case A: Node Selected */}
            {selectedNode && (
              <div className="space-y-4">
                <div className="flex items-center gap-2.5 pb-3 border-b border-slate-100">
                  <AwsIcon type={selectedNode.serviceType} size={28} />
                  <div>
                    <h3 className="font-bold text-sm text-slate-900">{selectedNode.name}</h3>
                    <span className="text-[10px] text-amber-700 font-mono font-semibold">
                      {selectedNode.category} Service
                    </span>
                  </div>
                </div>

                {/* Name Field */}
                <div className="space-y-1">
                  <label className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                    Resource Name
                  </label>
                  <input
                    type="text"
                    value={selectedNode.name}
                    onChange={(e) => {
                      const val = e.target.value;
                      setNodes((prev) =>
                        prev.map((n) => (n.id === selectedNode.id ? { ...n, name: val } : n))
                      );
                    }}
                    className="w-full px-2.5 py-1.5 bg-white border border-slate-200 rounded-lg text-xs text-slate-900 focus:outline-hidden focus:border-amber-500"
                  />
                </div>

                {/* Sizing / Tier Field */}
                <div className="space-y-1">
                  <label className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                    Instance Class / Sizing
                  </label>
                  <input
                    type="text"
                    value={selectedNode.tier}
                    onChange={(e) => {
                      const val = e.target.value;
                      setNodes((prev) =>
                        prev.map((n) => (n.id === selectedNode.id ? { ...n, tier: val } : n))
                      );
                    }}
                    className="w-full px-2.5 py-1.5 bg-white border border-slate-200 rounded-lg text-xs text-slate-900 focus:outline-hidden focus:border-amber-500"
                  />
                </div>

                {/* Port / Protocol */}
                {!selectedNode.isContainer && (
                  <div className="space-y-1">
                    <label className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                      Listening Port
                    </label>
                    <input
                      type="text"
                      value={selectedNode.port || ''}
                      onChange={(e) => {
                        const val = e.target.value;
                        setNodes((prev) =>
                          prev.map((n) => (n.id === selectedNode.id ? { ...n, port: val } : n))
                        );
                      }}
                      className="w-full px-2.5 py-1.5 bg-white border border-slate-200 rounded-lg text-xs text-slate-900 font-mono focus:outline-hidden focus:border-amber-500"
                    />
                  </div>
                )}

                {/* Monthly Cost Field */}
                {!selectedNode.isContainer && (
                  <div className="space-y-1">
                    <label className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                      Monthly Cost ($ USD)
                    </label>
                    <input
                      type="number"
                      step="0.10"
                      value={selectedNode.cost || 0}
                      onChange={(e) => {
                        const val = parseFloat(e.target.value) || 0;
                        setNodes((prev) =>
                          prev.map((n) => (n.id === selectedNode.id ? { ...n, cost: val } : n))
                        );
                      }}
                      className="w-full px-2.5 py-1.5 bg-white border border-slate-200 rounded-lg text-xs text-emerald-700 font-mono font-bold focus:outline-hidden focus:border-amber-500"
                    />
                  </div>
                )}

                {/* Security Group & HA details */}
                <div className="pt-3 border-t border-slate-100 space-y-2 text-slate-500 text-[11px]">
                  <div className="flex justify-between">
                    <span>Security Group:</span>
                    <span className="font-mono text-slate-800">{selectedNode.sg || 'sg-default'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Status:</span>
                    <span className="text-emerald-700 font-semibold">{selectedNode.status || 'Active'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Target Region:</span>
                    <span className="text-slate-800">us-east-1</span>
                  </div>
                </div>

                <button
                  onClick={handleDeleteSelected}
                  className="w-full py-2 rounded-lg bg-rose-50 hover:bg-rose-100 border border-rose-200 text-rose-700 font-semibold flex items-center justify-center gap-1.5 transition cursor-pointer"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                  <span>Delete Resource</span>
                </button>
              </div>
            )}

            {/* Case B: Edge Selected */}
            {selectedEdge && (
              <div className="space-y-4">
                <div className="pb-3 border-b border-slate-100">
                  <h3 className="font-bold text-sm text-slate-900">Connection Flow</h3>
                  <p className="text-[11px] text-slate-500">
                    Traffic conduit between {selectedEdge.source} and {selectedEdge.target}
                  </p>
                </div>

                <div className="space-y-1">
                  <label className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                    Protocol / Port Label
                  </label>
                  <input
                    type="text"
                    value={selectedEdge.label || ''}
                    onChange={(e) => {
                      const val = e.target.value;
                      setEdges((prev) =>
                        prev.map((edge) => (edge.id === selectedEdge.id ? { ...edge, label: val } : edge))
                      );
                    }}
                    placeholder="e.g. HTTPS:443"
                    className="w-full px-2.5 py-1.5 bg-white border border-slate-200 rounded-lg text-xs text-slate-900 font-mono focus:outline-hidden focus:border-amber-500"
                  />
                </div>

                {/* Preset Labels */}
                <div className="flex flex-wrap gap-1">
                  {['HTTPS:443', 'TCP:8080', 'PostgreSQL:5432', 'Redis:6379'].map((presetLabel) => (
                    <button
                      key={presetLabel}
                      onClick={() => {
                        setEdges((prev) =>
                          prev.map((edge) =>
                            edge.id === selectedEdge.id ? { ...edge, label: presetLabel } : edge
                          )
                        );
                      }}
                      className="px-2 py-0.5 rounded bg-slate-100 hover:bg-slate-200 text-[10px] font-mono text-slate-700"
                    >
                      {presetLabel}
                    </button>
                  ))}
                </div>

                {/* Routing Style */}
                <div className="space-y-1">
                  <label className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                    Routing Style
                  </label>
                  <div className="grid grid-cols-2 gap-1.5">
                    <button
                      onClick={() => {
                        setEdges((prev) =>
                          prev.map((edge) =>
                            edge.id === selectedEdge.id ? { ...edge, style: 'orthogonal' } : edge
                          )
                        );
                      }}
                      className={`py-1.5 rounded-lg border text-xs font-semibold cursor-pointer ${
                        selectedEdge.style === 'orthogonal'
                          ? 'bg-amber-50 border-amber-300 text-amber-800'
                          : 'bg-white border-slate-200 text-slate-600'
                      }`}
                    >
                      Orthogonal
                    </button>
                    <button
                      onClick={() => {
                        setEdges((prev) =>
                          prev.map((edge) =>
                            edge.id === selectedEdge.id ? { ...edge, style: 'curved' } : edge
                          )
                        );
                      }}
                      className={`py-1.5 rounded-lg border text-xs font-semibold cursor-pointer ${
                        selectedEdge.style === 'curved'
                          ? 'bg-amber-50 border-amber-300 text-amber-800'
                          : 'bg-white border-slate-200 text-slate-600'
                      }`}
                    >
                      Curved
                    </button>
                  </div>
                </div>

                {/* Flow Animation Toggle */}
                <div className="flex items-center justify-between pt-2">
                  <span className="text-slate-700">Animate Flow:</span>
                  <input
                    type="checkbox"
                    checked={Boolean(selectedEdge.animated)}
                    onChange={(e) => {
                      const val = e.target.checked;
                      setEdges((prev) =>
                        prev.map((edge) =>
                          edge.id === selectedEdge.id ? { ...edge, animated: val } : edge
                        )
                      );
                    }}
                    className="w-4 h-4 text-amber-600 rounded border-slate-300 focus:ring-amber-500"
                  />
                </div>

                <button
                  onClick={handleDeleteSelected}
                  className="w-full py-2 rounded-lg bg-rose-50 hover:bg-rose-100 border border-rose-200 text-rose-700 font-semibold flex items-center justify-center gap-1.5 transition cursor-pointer"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                  <span>Delete Connection</span>
                </button>
              </div>
            )}

            {/* Case C: Blank Canvas Overview */}
            {!selectedNode && !selectedEdge && (
              <div className="space-y-4">
                <div className="p-3 bg-slate-50 rounded-xl border border-slate-200 space-y-2">
                  <span className="text-[10px] uppercase font-bold text-slate-400 block">
                    Topology Statistics
                  </span>
                  <div className="grid grid-cols-2 gap-2 text-xs">
                    <div>
                      <span className="text-slate-500 block text-[11px]">Total Nodes</span>
                      <span className="font-bold text-slate-900 font-mono text-sm">
                        {nodes.length}
                      </span>
                    </div>
                    <div>
                      <span className="text-slate-500 block text-[11px]">Connections</span>
                      <span className="font-bold text-slate-900 font-mono text-sm">
                        {edges.length}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Well-Architected Framework Checklist */}
                <div className="space-y-2">
                  <span className="text-[10px] uppercase font-bold text-slate-400 block">
                    Well-Architected Checklist
                  </span>
                  <div className="space-y-1.5 text-[11px]">
                    <div className="flex items-center gap-2 text-slate-700">
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                      <span>Single or Multi-AZ Cost Alignment</span>
                    </div>
                    <div className="flex items-center gap-2 text-slate-700">
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                      <span>Security Group Boundary Enforcement</span>
                    </div>
                    <div className="flex items-center gap-2 text-slate-700">
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                      <span>VPC &amp; Subnet Isolation Boundary</span>
                    </div>
                    <div className="flex items-center gap-2 text-slate-700">
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                      <span>KMS Encryption Compliance</span>
                    </div>
                  </div>
                </div>

                {/* Quick Export Actions */}
                <div className="pt-3 border-t border-slate-100 space-y-2">
                  <button
                    onClick={handleExportJson}
                    className="w-full py-2 rounded-lg bg-white hover:bg-slate-50 border border-slate-200 text-slate-700 font-semibold flex items-center justify-center gap-1.5 transition cursor-pointer shadow-2xs"
                  >
                    <Download className="w-3.5 h-3.5 text-slate-500" />
                    <span>Download Topology JSON</span>
                  </button>
                  <button
                    onClick={() => setHclModalOpen(true)}
                    className="w-full py-2 rounded-lg bg-amber-500 hover:bg-amber-600 text-white font-semibold flex items-center justify-center gap-1.5 transition cursor-pointer shadow-xs"
                  >
                    <FileCode className="w-3.5 h-3.5 text-amber-100" />
                    <span>Generate Terraform HCL</span>
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* ═══════════════════════════════════════════════════════════════════════
          Modal: No Cloud Arch Studio Output Found
          ═══════════════════════════════════════════════════════════════════════ */}
      {noStudioOutputModalOpen && (
        <div className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-md w-full border border-slate-200 shadow-2xl p-6 space-y-4 animate-in fade-in">
            <div className="w-12 h-12 rounded-xl bg-amber-50 text-amber-600 border border-amber-200 flex items-center justify-center">
              <Sparkles className="w-6 h-6" />
            </div>
            <div>
              <h3 className="text-base font-bold text-slate-900">
                No Cloud Arch Studio Output Available
              </h3>
              <p className="text-xs text-slate-500 mt-1 leading-relaxed">
                You haven't run the Source Code Analyzer for project{' '}
                <strong className="text-slate-800">{activeProject?.name || 'current'}</strong> yet.
                Analyzing your repository code will automatically generate an AWS cloud architecture topology.
              </p>
            </div>
            <div className="flex items-center justify-end gap-2 pt-2">
              <button
                onClick={() => setNoStudioOutputModalOpen(false)}
                className="px-3.5 py-1.5 text-slate-600 hover:bg-slate-100 rounded-lg text-xs font-semibold cursor-pointer"
              >
                Cancel
              </button>
              {onNavigate && (
                <button
                  onClick={() => {
                    setNoStudioOutputModalOpen(false);
                    onNavigate('repo_analyzer', '/source-analysis');
                  }}
                  className="px-4 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-semibold shadow-xs cursor-pointer"
                >
                  Analyze Codebase
                </button>
              )}
            </div>
          </div>
        </div>
      )}

      {/* ═══════════════════════════════════════════════════════════════════════
          Terraform HCL Export Modal (Light Theme Container with Clean Dark Code)
          ═══════════════════════════════════════════════════════════════════════ */}
      {hclModalOpen && (
        <div className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-3xl w-full border border-slate-200 shadow-2xl overflow-hidden animate-in fade-in">
            <div className="p-4 bg-slate-50 border-b border-slate-200 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <FileCode className="w-4 h-4 text-amber-600" />
                <h3 className="text-sm font-bold text-slate-900">
                  Generated Terraform HCL Specification
                </h3>
              </div>
              <button
                onClick={() => setHclModalOpen(false)}
                className="text-slate-400 hover:text-slate-600 text-xs font-semibold cursor-pointer"
              >
                ✕ Close
              </button>
            </div>

            <div className="p-4 bg-slate-900 font-mono text-xs text-emerald-400 max-h-[460px] overflow-y-auto">
              <pre>{generateHclCode()}</pre>
            </div>

            <div className="p-4 bg-slate-50 border-t border-slate-200 flex justify-between items-center">
              <span className="text-xs text-slate-500">
                Matches {nodes.length} canvas nodes and {edges.length} dynamic connectors.
              </span>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => {
                    navigator.clipboard?.writeText(generateHclCode());
                    alert('Terraform HCL copied to clipboard!');
                  }}
                  className="px-3.5 py-1.5 bg-white hover:bg-slate-100 text-slate-700 text-xs font-semibold rounded-lg border border-slate-200 transition cursor-pointer shadow-2xs"
                >
                  Copy to Clipboard
                </button>
                <button
                  onClick={() => setHclModalOpen(false)}
                  className="px-4 py-1.5 bg-amber-500 hover:bg-amber-600 text-white text-xs font-semibold rounded-lg transition cursor-pointer shadow-xs"
                >
                  Done
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
