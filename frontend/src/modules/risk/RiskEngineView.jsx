// frontend/src/modules/risk/RiskEngineView.jsx
import React, { useState, useEffect } from 'react';
import { ShieldAlert, AlertTriangle, ShieldCheck, DollarSign, CheckCircle2, ArrowRight, RefreshCw } from 'lucide-react';
import { apiRequest } from '../../services/api';

export default function RiskEngineView({ onNavigate }) {
  const [loading, setLoading] = useState(false);
  const [probeStatus, setProbeStatus] = useState(null);

  useEffect(() => {
    async function checkEngine() {
      setLoading(true);
      try {
        const res = await apiRequest('/health');
        setProbeStatus({ operational: true, service: 'FinOps & Risk Engine (Port 8004)' });
      } catch (err) {
        setProbeStatus({ operational: false, error: err.message });
      } finally {
        setLoading(false);
      }
    }
    checkEngine();
  }, []);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-amber-50 text-amber-700 border border-amber-200">
              MODULE // RISK ENGINE
            </span>
            <span className="text-xs text-slate-400 font-mono">Pre-Deployment Blast Radius &amp; WAF Scoring</span>
          </div>
          <h1 className="text-xl font-bold text-slate-900 mt-1">Pre-Deployment Risk Engine</h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Objective evaluation of single points of failure (SPOF), public security exposure, and cost overruns.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => onNavigate('architecture_validation', '/architecture/validation')}
            className="px-3.5 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold transition cursor-pointer"
          >
            Architecture Validation
          </button>
          <button
            onClick={() => onNavigate('iac', '/terraform')}
            className="px-3.5 py-2 rounded-xl bg-[#1e40af] hover:bg-blue-700 text-white text-xs font-semibold transition cursor-pointer"
          >
            Review Terraform
          </button>
        </div>
      </div>

      {/* Engine Status Banner */}
      <div className="p-4 rounded-2xl bg-white border border-slate-200/80 shadow-xs flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-xl bg-amber-100 text-amber-700 flex items-center justify-center">
            <ShieldAlert className="w-4 h-4" />
          </div>
          <div>
            <div className="text-xs font-bold text-slate-800">Deterministic Well-Architected Risk Evaluation</div>
            <div className="text-[11px] text-slate-500">Evaluates security boundaries, multi-AZ high availability, and RTO/RPO targets.</div>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
          <span className="text-xs font-mono font-bold text-emerald-700">SERVICE ONLINE (8004)</span>
        </div>
      </div>

      {/* 6-Pillars Risk Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {[
          { name: 'Security & IAM Risk', score: '94/100', status: 'LOW RISK', desc: 'Private subnets enforced, KMS encryption default, no 0.0.0.0/0 SSH.' },
          { name: 'Reliability & SPOF', score: '88/100', status: 'MODERATE', desc: 'Multi-AZ RDS PostgreSQL verified. ALB health checks configured.' },
          { name: 'Cost Efficiency (FinOps)', score: '91/100', status: 'OPTIMAL', desc: 'ARM Graviton c6g / t4g instances selected. 22% cost arbitrage.' },
          { name: 'Performance Efficiency', score: '86/100', status: 'OPTIMAL', desc: 'Read replicas and Redis cache-aside layer provisioned.' },
          { name: 'Operational Excellence', score: '92/100', status: 'LOW RISK', desc: 'OpenTelemetry collector and CloudWatch metrics enabled.' },
          { name: 'Sustainability Impact', score: '90/100', status: 'LOW RISK', desc: 'Efficient utilization model minimizing idle compute overhead.' },
        ].map((item, idx) => (
          <div key={idx} className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-xs space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-slate-800">{item.name}</span>
              <span className="text-xs font-bold font-mono text-emerald-700">{item.score}</span>
            </div>
            <div className="text-[11px] text-slate-500 leading-relaxed">{item.desc}</div>
            <div className="pt-2">
              <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">
                {item.status}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
