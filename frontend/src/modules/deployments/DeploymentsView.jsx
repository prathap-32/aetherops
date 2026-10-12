// frontend/src/modules/deployments/DeploymentsView.jsx
import React from 'react';
import { Rocket, CheckCircle2, Clock, GitCommit, ExternalLink, ShieldCheck } from 'lucide-react';

export default function DeploymentsView() {
  const deployments = [
    {
      id: 'dep-9021',
      version: 'v1.4.2',
      commit: '9f2a0b1',
      env: 'Production (us-east-1)',
      status: 'SUCCESS',
      time: '12 mins ago',
      author: 'prathap32',
    },
    {
      id: 'dep-9020',
      version: 'v1.4.1',
      commit: '4c8e1a7',
      env: 'Staging (us-east-1)',
      status: 'SUCCESS',
      time: '2 hours ago',
      author: 'prathap32',
    },
  ];

  return (
    <div className="space-y-6">
      <div className="pb-4 border-b border-slate-200">
        <div className="flex items-center gap-2">
          <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold bg-blue-50 text-blue-700 border border-blue-200">
            Module 6
          </span>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Deployments & CI/CD Pipeline</h1>
        </div>
        <p className="text-sm text-slate-500 mt-1">
          Zero-downtime rolling updates, canary routing, and automated rollback health checks.
        </p>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 shadow-xs overflow-hidden">
        <div className="p-5 border-b border-slate-100 flex items-center justify-between">
          <h3 className="text-base font-bold text-slate-900">Recent Deployment Runs</h3>
          <span className="text-xs font-semibold text-emerald-700 bg-emerald-50 px-2.5 py-1 rounded-full border border-emerald-200">
            Pipeline Green
          </span>
        </div>

        <div className="divide-y divide-slate-100 text-xs">
          {deployments.map((d) => (
            <div key={d.id} className="p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3 hover:bg-slate-50 transition">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center font-bold">
                  <Rocket className="w-4 h-4" />
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-semibold text-slate-900">{d.version}</span>
                    <span className="text-slate-400 font-mono text-[11px] flex items-center gap-1">
                      <GitCommit className="w-3 h-3" />
                      {d.commit}
                    </span>
                    <span className="text-[10px] font-semibold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-200">
                      {d.status}
                    </span>
                  </div>
                  <p className="text-slate-500 mt-0.5">{d.env} • Triggered by {d.author}</p>
                </div>
              </div>
              <span className="text-slate-400 font-medium">{d.time}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
