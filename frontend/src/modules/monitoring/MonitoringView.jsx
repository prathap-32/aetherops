// frontend/src/modules/monitoring/MonitoringView.jsx
import React from 'react';
import { DollarSign, Cpu, Radio } from 'lucide-react';

export default function MonitoringView() {
  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-4 border-b border-slate-200">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Infrastructure Monitoring &amp; Observability</h1>
            <span className="px-2.5 py-0.5 rounded text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
              CloudWatch Telemetry Active
            </span>
          </div>
          <p className="text-sm text-slate-500 mt-1">
            CloudWatch metric aggregations, cluster utilization, and AWS resource health metrics.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-semibold uppercase tracking-wider">Estimated Monthly Spend</span>
            <DollarSign className="w-5 h-5 text-emerald-600" />
          </div>
          <p className="text-2xl font-bold text-slate-900 mt-2">$84.20</p>
          <p className="text-xs text-emerald-600 font-medium mt-1">14% below budgeted limit ($100)</p>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-semibold uppercase tracking-wider">Avg CPU Utilization</span>
            <Cpu className="w-5 h-5 text-blue-600" />
          </div>
          <p className="text-2xl font-bold text-slate-900 mt-2">28.4%</p>
          <p className="text-xs text-slate-500 mt-1">Across 4 auto-scaled pods</p>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-semibold uppercase tracking-wider">API Health Status</span>
            <Radio className="w-5 h-5 text-emerald-500 animate-pulse" />
          </div>
          <p className="text-2xl font-bold text-slate-900 mt-2">99.98%</p>
          <p className="text-xs text-slate-500 mt-1">Zero 5xx errors recorded in 24h</p>
        </div>
      </div>
    </div>
  );
}
