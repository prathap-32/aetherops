// frontend/src/modules/designer/ArchitectureDesigner.jsx
import React, { useState } from 'react';
import { Palette, Layers, Network, Plus, ArrowRight, ShieldCheck, Sparkles, CheckCircle2 } from 'lucide-react';

export default function ArchitectureDesigner({ onNavigate }) {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-purple-50 text-purple-700 border border-purple-200">
              MODULE // DESIGNER
            </span>
            <span className="text-xs text-slate-400 font-mono">React Flow Topology Canvas</span>
          </div>
          <h1 className="text-xl font-bold text-slate-900 mt-1">Architecture Designer Studio</h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Interactive drag-and-drop cloud architecture diagram editor with Well-Architected validation.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => onNavigate('architecture', '/architecture')}
            className="px-3.5 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold transition cursor-pointer"
          >
            AI Architecture Engine
          </button>
          <button
            onClick={() => onNavigate('iac', '/terraform')}
            className="px-3.5 py-2 rounded-xl bg-[#1e40af] hover:bg-blue-700 text-white text-xs font-semibold transition flex items-center gap-1.5 cursor-pointer"
          >
            <span>Export to Terraform</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Canvas Placeholder & Architecture Tools */}
      <div className="bg-slate-900 rounded-2xl border border-slate-800 p-8 text-white min-h-[460px] flex flex-col items-center justify-center text-center relative overflow-hidden">
        {/* Background Grid Pattern */}
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#1f2937_1px,transparent_1px),linear-gradient(to_bottom,#1f2937_1px,transparent_1px)] bg-[size:32px_32px] opacity-25"></div>

        <div className="relative z-10 max-w-md space-y-4">
          <div className="w-14 h-14 rounded-2xl bg-purple-600/20 text-purple-400 border border-purple-500/30 flex items-center justify-center mx-auto shadow-lg shadow-purple-500/20">
            <Palette className="w-7 h-7" />
          </div>
          <div>
            <h3 className="text-lg font-bold">Interactive Topology Canvas</h3>
            <p className="text-xs text-slate-400 mt-1 leading-relaxed">
              Design multi-tier AWS architectures with custom VPC CIDR ranges, subnets, EC2 instances, RDS databases, and ALB listeners.
            </p>
          </div>
          <div className="p-4 rounded-xl bg-slate-800/80 border border-slate-700 text-left text-xs space-y-2 font-mono">
            <div className="text-purple-300 font-bold">Canvas Specifications:</div>
            <div className="text-slate-300 flex items-center gap-2">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
              <span>React Flow v11 Node DAG Engine</span>
            </div>
            <div className="text-slate-300 flex items-center gap-2">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
              <span>Multi-Region AWS Catalog Integration</span>
            </div>
            <div className="text-slate-300 flex items-center gap-2">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
              <span>Automatic Terraform HCL Code Synthesis</span>
            </div>
          </div>
          <button
            onClick={() => onNavigate('architecture', '/architecture')}
            className="px-4 py-2 rounded-xl bg-purple-600 hover:bg-purple-500 text-white text-xs font-semibold transition cursor-pointer"
          >
            Generate Architecture from Profile
          </button>
        </div>
      </div>
    </div>
  );
}
