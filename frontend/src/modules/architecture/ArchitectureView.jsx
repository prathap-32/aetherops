// frontend/src/modules/architecture/ArchitectureView.jsx
import React, { useState } from 'react';
import {
  Layers,
  Shield,
  Server,
  Database,
  Globe,
  ArrowRight,
  Download,
  Share2,
  Lock,
  Cpu,
  CheckCircle2,
  ExternalLink,
  ChevronRight
} from 'lucide-react';

export default function ArchitectureView({ onNavigate }) {
  const [selectedNode, setSelectedNode] = useState('app-service');

  const nodes = [
    {
      id: 'igw',
      name: 'Internet Gateway',
      tier: 'Edge Ingress',
      type: 'Networking',
      cidr: '0.0.0.0/0',
      status: 'Active',
      description: 'Public Internet Gateway routing traffic to AWS VPC.',
    },
    {
      id: 'alb',
      name: 'Application Load Balancer (ALB)',
      tier: 'Public Subnet (us-east-1a, us-east-1b)',
      type: 'Load Balancer',
      cidr: '10.0.1.0/24, 10.0.2.0/24',
      status: 'Active',
      description: 'Dual-AZ SSL/TLS termination with path-based routing.',
    },
    {
      id: 'app-service',
      name: 'App Cluster (FastAPI / Node)',
      tier: 'Private Subnet (us-east-1a, us-east-1b)',
      type: 'Compute (ECS / t3.medium)',
      cidr: '10.0.10.0/24, 10.0.20.0/24',
      status: 'Target Sized',
      description: 'Auto-scaling container group running microservice application logic.',
    },
    {
      id: 'database',
      name: 'Amazon RDS PostgreSQL',
      tier: 'Isolated Database Subnet (Multi-AZ)',
      type: 'Database (db.t3.medium)',
      cidr: '10.0.50.0/24, 10.0.60.0/24',
      status: 'Target Sized',
      description: 'Encrypted at rest with KMS, automatic backup snapshots, and failover replica.',
    },
    {
      id: 'redis',
      name: 'ElastiCache Redis',
      tier: 'Isolated Cache Subnet',
      type: 'In-Memory Cache (cache.t3.micro)',
      cidr: '10.0.70.0/24',
      status: 'Target Sized',
      description: 'Session store and low-latency API response caching layer.',
    },
  ];

  const currentNode = nodes.find((n) => n.id === selectedNode) || nodes[0];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-4 border-b border-slate-200">
        <div>
          <div className="flex items-center gap-2">
            <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold bg-sky-50 text-sky-700 border border-sky-200">
              Module 4
            </span>
            <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Cloud Architecture Studio</h1>
          </div>
          <p className="text-sm text-slate-500 mt-1">
            Visual topology synthesis of multi-tier VPC networks, subnets, and compute placements.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => alert('Exporting Terraform HCL specification...')}
            className="inline-flex items-center gap-1.5 px-3.5 py-2 text-xs font-semibold text-slate-700 bg-white border border-slate-200 rounded-lg hover:bg-slate-50 transition shadow-xs"
          >
            <Download className="w-4 h-4 text-slate-500" />
            Export HCL
          </button>
          {onNavigate && (
            <button
              onClick={() => onNavigate('iac')}
              className="inline-flex items-center gap-1.5 px-4 py-2 text-xs font-semibold text-white bg-blue-600 hover:bg-blue-700 rounded-lg shadow-xs transition"
            >
              Generate IaC
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Visual Topology Diagram */}
        <div className="lg:col-span-2 bg-white rounded-xl border border-slate-200 shadow-xs p-6 space-y-6">
          <div className="flex items-center justify-between pb-3 border-b border-slate-100">
            <div className="flex items-center gap-2">
              <Globe className="w-4 h-4 text-blue-600" />
              <span className="text-xs font-bold uppercase tracking-wider text-slate-700">
                AWS VPC Topology (10.0.0.0/16 - us-east-1)
              </span>
            </div>
            <span className="text-[11px] font-mono text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-200">
              High Availability Enabled
            </span>
          </div>

          <div className="space-y-4">
            {nodes.map((node) => {
              const isSelected = selectedNode === node.id;
              return (
                <div
                  key={node.id}
                  onClick={() => setSelectedNode(node.id)}
                  className={`p-4 rounded-xl border transition cursor-pointer flex items-center justify-between ${
                    isSelected
                      ? 'border-blue-500 bg-blue-50/40 ring-2 ring-blue-500/20'
                      : 'border-slate-200 hover:border-slate-300 bg-slate-50/50 hover:bg-slate-50'
                  }`}
                >
                  <div className="flex items-center gap-3.5">
                    <div
                      className={`w-10 h-10 rounded-lg flex items-center justify-center shrink-0 ${
                        isSelected
                          ? 'bg-blue-600 text-white'
                          : 'bg-white border border-slate-200 text-slate-600'
                      }`}
                    >
                      {node.type.includes('Networking') && <Globe className="w-5 h-5" />}
                      {node.type.includes('Load Balancer') && <Layers className="w-5 h-5" />}
                      {node.type.includes('Compute') && <Server className="w-5 h-5" />}
                      {node.type.includes('Database') && <Database className="w-5 h-5" />}
                      {node.type.includes('Cache') && <Cpu className="w-5 h-5" />}
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <h4 className="text-sm font-semibold text-slate-900">{node.name}</h4>
                        <span className="text-[10px] font-mono text-slate-500 bg-white px-1.5 py-0.5 rounded border border-slate-200">
                          {node.cidr}
                        </span>
                      </div>
                      <p className="text-xs text-slate-500 mt-0.5">{node.tier}</p>
                    </div>
                  </div>

                  <span
                    className={`text-xs font-semibold px-2.5 py-1 rounded-full ${
                      isSelected
                        ? 'bg-blue-100 text-blue-800'
                        : 'bg-slate-100 text-slate-600'
                    }`}
                  >
                    {node.status}
                  </span>
                </div>
              );
            })}
          </div>
        </div>

        {/* Node Inspection Panel */}
        <div className="bg-white rounded-xl border border-slate-200 shadow-xs p-6 space-y-5">
          <div className="flex items-center gap-2 pb-3 border-b border-slate-100 text-slate-900 font-bold text-sm">
            <Shield className="w-4 h-4 text-indigo-600" />
            Component Inspector
          </div>

          <div className="space-y-4 text-xs">
            <div>
              <p className="text-slate-400 font-semibold uppercase tracking-wider text-[10px]">Component Name</p>
              <p className="text-sm font-bold text-slate-900 mt-1">{currentNode.name}</p>
            </div>

            <div>
              <p className="text-slate-400 font-semibold uppercase tracking-wider text-[10px]">Subnet Placement</p>
              <p className="text-slate-800 mt-1 font-medium">{currentNode.tier}</p>
            </div>

            <div>
              <p className="text-slate-400 font-semibold uppercase tracking-wider text-[10px]">CIDR Block</p>
              <p className="font-mono text-slate-800 bg-slate-50 p-2 rounded-lg border border-slate-200 mt-1">
                {currentNode.cidr}
              </p>
            </div>

            <div>
              <p className="text-slate-400 font-semibold uppercase tracking-wider text-[10px]">Description & Security</p>
              <p className="text-slate-600 mt-1 leading-relaxed">{currentNode.description}</p>
            </div>

            <div className="pt-3 border-t border-slate-100 space-y-2">
              <div className="flex items-center justify-between text-slate-600">
                <span>Security Group:</span>
                <span className="font-mono text-slate-900 font-semibold">sg-0a91e4f</span>
              </div>
              <div className="flex items-center justify-between text-slate-600">
                <span>Encryption at Rest:</span>
                <span className="font-semibold text-emerald-600">AWS KMS (Active)</span>
              </div>
              <div className="flex items-center justify-between text-slate-600">
                <span>Auto-Recovery:</span>
                <span className="font-semibold text-emerald-600">CloudWatch Enabled</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
