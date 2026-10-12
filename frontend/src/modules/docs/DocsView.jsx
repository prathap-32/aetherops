// frontend/src/modules/docs/DocsView.jsx
import React from 'react';
import { BookOpen, ExternalLink, ShieldCheck, Terminal, Layers } from 'lucide-react';

export default function DocsView() {
  return (
    <div className="space-y-6 max-w-3xl">
      <div className="pb-4 border-b border-slate-200">
        <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Platform Documentation & Architecture</h1>
        <p className="text-sm text-slate-500 mt-1">
          Reference guide for Aether Cloud multi-tenant DevOps orchestrator and API contracts.
        </p>
      </div>

      <div className="space-y-4">
        <div className="bg-white rounded-xl border border-slate-200 shadow-xs p-6 space-y-3">
          <div className="flex items-center gap-2 text-slate-900 font-bold text-base">
            <Layers className="w-5 h-5 text-blue-600" />
            Decoupled Microservice Topology
          </div>
          <p className="text-sm text-slate-600 leading-relaxed">
            Aether Cloud decomposes DevOps automation into independent, headless microservices communicating via standard REST APIs and Redis pub/sub. The frontend React application acts as a single-page orchestrator, avoiding iframe recursion and preserving browser history.
          </p>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 shadow-xs p-6 space-y-3">
          <div className="flex items-center gap-2 text-slate-900 font-bold text-base">
            <ShieldCheck className="w-5 h-5 text-emerald-600" />
            Role-Based Access Control (RBAC) & Route Security
          </div>
          <p className="text-sm text-slate-600 leading-relaxed">
            Standard <span className="font-semibold text-slate-800">USER</span> accounts have full visibility into Projects, Environments, Git Connections, Repo Analyzer, and IaC Generator, while the <span className="font-semibold text-slate-800">Admin Console</span> is strictly gated to <span className="font-semibold text-slate-800">ADMIN</span> or <span className="font-semibold text-slate-800">SUPER_ADMIN</span> roles with cryptographically signed session tokens and HTTP-only cookie validation.
          </p>
        </div>
      </div>
    </div>
  );
}
