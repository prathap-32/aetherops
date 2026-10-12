// frontend/src/modules/optimization/OptimizationView.jsx
import React, { useState, useEffect } from 'react';
import { DollarSign, TrendingDown, Cpu, HardDrive, RefreshCw, CheckCircle2, ArrowRight } from 'lucide-react';

export default function OptimizationView({ onNavigate }) {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">
              MODULE // FINOPS OPTIMIZER
            </span>
            <span className="text-xs text-slate-400 font-mono">Module 4: FinOps Cost Arbitrage (Port 8004)</span>
          </div>
          <h1 className="text-xl font-bold text-slate-900 mt-1">Continuous Risk &amp; Optimization</h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Continuous resource rightsizing, spot instance arbitrage, and multi-region pricing catalog evaluation.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => onNavigate('monitoring', '/monitoring')}
            className="px-3.5 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold transition cursor-pointer"
          >
            Observability Metrics
          </button>
        </div>
      </div>

      {/* FinOps Opportunities Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-xs space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-800">ARM Graviton Savings</span>
            <TrendingDown className="w-4 h-4 text-emerald-600" />
          </div>
          <div className="text-2xl font-black font-mono text-emerald-600">-$38.40 / mo</div>
          <p className="text-xs text-slate-500">Migrating x86 t3.medium to AWS Graviton t4g.medium yields 20% cost savings with better performance.</p>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-xs space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-800">Storage Optimization</span>
            <HardDrive className="w-4 h-4 text-blue-600" />
          </div>
          <div className="text-2xl font-black font-mono text-blue-600">gp2 &rarr; gp3</div>
          <p className="text-xs text-slate-500">Upgrading EBS volumes to gp3 saves 20% baseline storage cost while decoupling baseline IOPS.</p>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-xs space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-800">NAT Gateway Arbitrage</span>
            <DollarSign className="w-4 h-4 text-amber-600" />
          </div>
          <div className="text-2xl font-black font-mono text-slate-900">VPC Endpoints</div>
          <p className="text-xs text-slate-500">Routing S3 and DynamoDB traffic through free VPC Gateway Endpoints eliminates data transfer fees.</p>
        </div>
      </div>
    </div>
  );
}
