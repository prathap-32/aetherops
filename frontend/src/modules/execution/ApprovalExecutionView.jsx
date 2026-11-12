import React, { useMemo, useState } from 'react';
import {
  ShieldCheck, Clock3, CheckCircle2, XCircle, AlertTriangle, Play,
  TerminalSquare, FileCode2, History, RotateCcw, Search, Filter,
  ChevronRight, ArrowUpRight, Plus, Minus, RefreshCw, LockKeyhole,
  Cloud, Server, Database, Network, HardDrive, Eye, Check, X,
  CalendarDays, UserRound, Hash, Activity, ArrowRight, CircleDot
} from 'lucide-react';

const INITIAL_PLANS = [
  {
    id: 'PLAN-2026-0142', name: 'Production VPC & Compute Foundation',
    project: 'Aether Cloud Platform', environment: 'Production', region: 'ap-south-1',
    created: '12 Nov 2026, 10:42 AM', owner: 'Prathap', status: 'Pending approval',
    digest: 'sha256:8f2c9d71a43e6b90c4d1a2f7', create: 5, update: 1, destroy: 0,
    risk: 'Medium', estimatedCost: '$48.20 / month',
    resources: [
      { address: 'aws_vpc.main', type: 'aws_vpc', action: 'create', name: 'Aether production VPC', detail: 'CIDR: 10.20.0.0/16', icon: Network },
      { address: 'aws_subnet.public_a', type: 'aws_subnet', action: 'create', name: 'Public subnet A', detail: 'Availability Zone: ap-south-1a', icon: Network },
      { address: 'aws_subnet.private_a', type: 'aws_subnet', action: 'create', name: 'Private subnet A', detail: 'Availability Zone: ap-south-1a', icon: Network },
      { address: 'aws_instance.app', type: 'aws_instance', action: 'create', name: 'Application EC2 instance', detail: 'Instance type: t3.medium', icon: Server },
      { address: 'aws_security_group.app', type: 'aws_security_group', action: 'create', name: 'Application security group', detail: 'Inbound rules: 2', icon: LockKeyhole },
      { address: 'aws_route_table.public', type: 'aws_route_table', action: 'update', name: 'Public route table', detail: 'Add default route', icon: Network }
    ]
  },
  {
    id: 'PLAN-2026-0141', name: 'Development RDS Configuration',
    project: 'Aether Cloud Platform', environment: 'Development', region: 'ap-south-1',
    created: '12 Nov 2026, 09:18 AM', owner: 'Platform Engineer', status: 'Pending approval',
    digest: 'sha256:3a7d1e90b2c4f681a5d9c3e7', create: 2, update: 2, destroy: 0,
    risk: 'Low', estimatedCost: '$31.60 / month',
    resources: [
      { address: 'aws_db_subnet_group.main', type: 'aws_db_subnet_group', action: 'create', name: 'Database subnet group', detail: '2 private subnets', icon: Database },
      { address: 'aws_db_instance.postgres', type: 'aws_db_instance', action: 'create', name: 'PostgreSQL database', detail: 'db.t3.micro', icon: Database },
      { address: 'aws_security_group.db', type: 'aws_security_group', action: 'update', name: 'Database security group', detail: 'Restrict inbound access', icon: LockKeyhole },
      { address: 'aws_db_parameter_group.main', type: 'aws_db_parameter_group', action: 'update', name: 'Database parameters', detail: 'Apply approved parameter settings', icon: Database }
    ]
  },
  {
    id: 'PLAN-2026-0139', name: 'Storage Lifecycle Policy',
    project: 'Aether Cloud Platform', environment: 'Staging', region: 'ap-south-1',
    created: '11 Nov 2026, 04:26 PM', owner: 'Prathap', status: 'Approved',
    digest: 'sha256:bc1e48a7d9032f6156a0e4c8', create: 1, update: 0, destroy: 0,
    risk: 'Low', estimatedCost: '$4.80 / month',
    resources: [
      { address: 'aws_s3_bucket.artifacts', type: 'aws_s3_bucket', action: 'create', name: 'Build artifacts bucket', detail: 'Versioning enabled', icon: HardDrive }
    ]
  }
];

const NAV_ITEMS = [
  { id: 'overview', label: 'Overview', icon: Activity },
  { id: 'approvals', label: 'Approval queue', icon: ShieldCheck },
  { id: 'plan', label: 'Terraform plan review', icon: FileCode2 },
  { id: 'console', label: 'Execution console', icon: TerminalSquare },
  { id: 'history', label: 'Execution history', icon: History },
  { id: 'rollback', label: 'Rollback records', icon: RotateCcw }
];

const statusClass = (status) => {
  if (status === 'Approved' || status === 'Succeeded') return 'bg-emerald-50 text-emerald-700 border-emerald-200';
  if (status === 'Failed' || status === 'Rejected') return 'bg-rose-50 text-rose-700 border-rose-200';
  if (status === 'Executing') return 'bg-blue-50 text-blue-700 border-blue-200';
  return 'bg-amber-50 text-amber-700 border-amber-200';
};

const actionStyle = (action) => action === 'create'
  ? 'bg-emerald-50 text-emerald-700'
  : action === 'update'
    ? 'bg-amber-50 text-amber-700'
    : 'bg-rose-50 text-rose-700';

export default function ApprovalExecutionView({ activeProject, activeEnvironment, user }) {
  const [plans, setPlans] = useState(INITIAL_PLANS);
  const [activeTab, setActiveTab] = useState('overview');
  const [selectedId, setSelectedId] = useState(INITIAL_PLANS[0].id);
  const [search, setSearch] = useState('');
  const [filter, setFilter] = useState('All');
  const [reviewNote, setReviewNote] = useState('');
  const [showApprovalConfirm, setShowApprovalConfirm] = useState(false);
  const [executionLogs, setExecutionLogs] = useState([]);
  const [executionStatus, setExecutionStatus] = useState('Idle');
  const [showExecutionConfirm, setShowExecutionConfirm] = useState(false);
  const [notice, setNotice] = useState('This is an interactive UI preview using sample data. No AWS infrastructure changes will be made.');

  const selectedPlan = plans.find((plan) => plan.id === selectedId) || plans[0];
  const pendingCount = plans.filter((plan) => plan.status === 'Pending approval').length;
  const approvedCount = plans.filter((plan) => plan.status === 'Approved').length;
  const succeededCount = plans.filter((plan) => plan.status === 'Succeeded').length;
  const filteredPlans = useMemo(() => plans.filter((plan) => {
    const matchesSearch = (plan.name + plan.id + plan.project).toLowerCase().includes(search.toLowerCase());
    const matchesFilter = filter === 'All' || plan.status === filter;
    return matchesSearch && matchesFilter;
  }), [plans, search, filter]);

  const selectPlan = (plan) => {
    setSelectedId(plan.id);
    setActiveTab('plan');
    setReviewNote('');
  };

  const approvePlan = () => {
    setPlans((current) => current.map((plan) => plan.id === selectedId
      ? { ...plan, status: 'Approved' } : plan));
    setShowApprovalConfirm(false);
    setNotice('Sample approval recorded locally for ' + selectedId + '. No backend request was made.');
  };

  const rejectPlan = () => {
    setPlans((current) => current.map((plan) => plan.id === selectedId
      ? { ...plan, status: 'Rejected' } : plan));
    setShowApprovalConfirm(false);
    setNotice('Sample rejection recorded locally for ' + selectedId + '.');
  };

  const runExecutionPreview = () => {
    setShowExecutionConfirm(false);
    setActiveTab('console');
    setExecutionStatus('Executing');
    setExecutionLogs([
      '[10:45:01] Initializing execution preview...',
      '[10:45:02] Selected plan: ' + selectedPlan.id,
      '[10:45:03] Verifying approval receipt and plan digest...',
      '[10:45:04] Approval verified (UI preview).',
      '[10:45:05] Acquiring infrastructure state lock...',
      '[10:45:06] Preparing Terraform apply operation...'
    ]);
    setNotice('Execution is simulated in the frontend. No Terraform command or AWS API was called.');
    window.setTimeout(() => {
      setExecutionLogs((logs) => [...logs,
        '[10:45:08] Applying planned resource changes (simulation)...',
        '[10:45:10] Resource operations completed in preview mode.',
        '[10:45:11] Releasing infrastructure state lock...',
        '[10:45:12] Execution preview completed successfully.'
      ]);
      setExecutionStatus('Succeeded');
      setPlans((current) => current.map((plan) => plan.id === selectedId
        ? { ...plan, status: 'Succeeded' } : plan));
    }, 1800);
  };

  const pageTitle = NAV_ITEMS.find((item) => item.id === activeTab)?.label || 'Overview';

  return (
    <div className="space-y-5 pb-8">
      <div className="flex flex-col xl:flex-row xl:items-center xl:justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-blue-700 mb-2">
            <ShieldCheck className="w-4 h-4" /> Infrastructure governance
            <span className="text-slate-300">/</span> Module 09
          </div>
          <div className="flex flex-wrap items-center gap-3">
            <h1 className="text-2xl font-bold tracking-tight text-slate-900">Approval &amp; Execution</h1>
            <span className="px-2.5 py-1 rounded-full border text-[11px] font-semibold bg-blue-50 text-blue-700 border-blue-200">Terraform workflow</span>
          </div>
          <p className="text-sm text-slate-500 mt-1">Review infrastructure changes, authorize a Terraform plan, and track execution outcomes.</p>
        </div>
        <div className="flex flex-wrap items-center gap-2 text-xs">
          <div className="px-3 py-2 rounded-lg border border-slate-200 bg-white text-slate-600">
            <span className="text-slate-400">Project</span><span className="font-semibold text-slate-800 ml-2">{activeProject?.name || activeProject?.id || 'Aether Cloud Platform'}</span>
          </div>
          <div className="px-3 py-2 rounded-lg border border-slate-200 bg-white text-slate-600">
            <span className="text-slate-400">Environment</span><span className="font-semibold text-slate-800 ml-2">{activeEnvironment?.name || activeEnvironment?.type || 'Production'}</span>
          </div>
          <span className="px-3 py-2 rounded-lg bg-slate-100 text-slate-600 font-medium">UI preview</span>
        </div>
      </div>

      <div className="flex items-start gap-2.5 rounded-xl border border-blue-200 bg-blue-50/80 px-4 py-3 text-xs text-blue-900">
        <AlertTriangle className="w-4 h-4 mt-0.5 shrink-0 text-blue-700" />
        <div><span className="font-bold">Preview mode:</span> {notice}</div>
      </div>

      <div className="flex gap-1 overflow-x-auto border-b border-slate-200">
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon;
          const active = activeTab === item.id;
          return (
            <button key={item.id} onClick={() => setActiveTab(item.id)}
              className={'flex items-center gap-2 whitespace-nowrap px-3.5 py-3 text-xs font-semibold border-b-2 transition ' +
                (active ? 'border-blue-700 text-blue-700' : 'border-transparent text-slate-500 hover:text-slate-800 hover:border-slate-300')}>
              <Icon className="w-4 h-4" />{item.label}
              {item.id === 'approvals' && pendingCount > 0 && <span className="rounded-full bg-amber-100 text-amber-800 px-1.5 py-0.5 text-[10px]">{pendingCount}</span>}
            </button>
          );
        })}
      </div>

      {activeTab === 'overview' && (
        <div className="space-y-5">
          <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-3">
            {[
              { label: 'Pending approvals', value: pendingCount, sub: 'Require engineer review', icon: Clock3, tone: 'amber' },
              { label: 'Approved plans', value: approvedCount, sub: 'Authorized for execution', icon: ShieldCheck, tone: 'blue' },
              { label: 'Successful executions', value: succeededCount, sub: 'Completed in preview', icon: CheckCircle2, tone: 'emerald' },
              { label: 'Total plans', value: plans.length, sub: 'Tracked in this workspace', icon: FileCode2, tone: 'slate' }
            ].map((card) => {
              const Icon = card.icon;
              const tone = card.tone === 'amber' ? 'text-amber-700 bg-amber-50' : card.tone === 'blue' ? 'text-blue-700 bg-blue-50' : card.tone === 'emerald' ? 'text-emerald-700 bg-emerald-50' : 'text-slate-700 bg-slate-100';
              return <div key={card.label} className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
                <div className="flex items-center justify-between"><span className="text-xs font-medium text-slate-500">{card.label}</span><span className={'p-2 rounded-lg ' + tone}><Icon className="w-4 h-4" /></span></div>
                <div className="text-2xl font-bold text-slate-900 mt-3">{card.value}</div>
                <div className="text-[11px] text-slate-400 mt-1">{card.sub}</div>
              </div>;
            })}
          </div>

          <div className="grid grid-cols-1 xl:grid-cols-3 gap-4">
            <section className="xl:col-span-2 rounded-xl border border-slate-200 bg-white overflow-hidden">
              <div className="flex items-center justify-between p-4 border-b border-slate-100">
                <div><h2 className="text-sm font-bold text-slate-900">Plans requiring attention</h2><p className="text-xs text-slate-500 mt-1">Review the proposed infrastructure changes before execution.</p></div>
                <button onClick={() => setActiveTab('approvals')} className="text-xs font-semibold text-blue-700 hover:text-blue-900 flex items-center gap-1">View queue <ArrowRight className="w-3.5 h-3.5" /></button>
              </div>
              <div className="divide-y divide-slate-100">
                {plans.filter((plan) => plan.status === 'Pending approval').map((plan) => (
                  <button key={plan.id} onClick={() => selectPlan(plan)} className="w-full text-left p-4 hover:bg-slate-50 transition">
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                      <div className="min-w-0"><div className="text-sm font-semibold text-slate-800 truncate">{plan.name}</div><div className="text-[11px] text-slate-500 mt-1">{plan.id} <span className="mx-1.5 text-slate-300">•</span>{plan.environment} <span className="mx-1.5 text-slate-300">•</span>{plan.region}</div></div>
                      <div className="flex items-center gap-3"><div className="text-right"><div className="text-xs font-semibold text-slate-700">{plan.create} create · {plan.update} change · {plan.destroy} destroy</div><div className="text-[11px] text-slate-400 mt-1">Risk: {plan.risk}</div></div><ChevronRight className="w-4 h-4 text-slate-400" /></div>
                    </div>
                  </button>
                ))}
                {pendingCount === 0 && <div className="p-8 text-center text-sm text-slate-500">No plans are waiting for approval.</div>}
              </div>
            </section>
            <section className="rounded-xl border border-slate-200 bg-white p-4">
              <h2 className="text-sm font-bold text-slate-900">Approval workflow</h2>
              <p className="text-xs text-slate-500 mt-1">Every infrastructure change follows a controlled sequence.</p>
              <div className="mt-5 space-y-4">
                {[
                  ['01', 'Terraform plan received', 'Plan and digest are available'],
                  ['02', 'Review resource changes', 'Inspect create, update and destroy actions'],
                  ['03', 'Explicit approval', 'Record reviewer decision and note'],
                  ['04', 'Execute approved plan', 'Run only the approved plan revision'],
                  ['05', 'Record outcome', 'Preserve logs and execution result']
                ].map((step, index) => <div key={step[0]} className="flex gap-3"><div className="flex flex-col items-center"><span className="w-7 h-7 rounded-full bg-slate-100 text-slate-600 text-[10px] font-bold flex items-center justify-center">{step[0]}</span>{index < 4 && <span className="w-px h-6 bg-slate-200" />}</div><div><div className="text-xs font-semibold text-slate-800">{step[1]}</div><div className="text-[11px] text-slate-500 mt-0.5">{step[2]}</div></div></div>)}
              </div>
            </section>
          </div>
        </div>
      )}

      {(activeTab === 'approvals' || activeTab === 'history') && (
        <section className="rounded-xl border border-slate-200 bg-white overflow-hidden">
          <div className="p-4 border-b border-slate-100 flex flex-col md:flex-row md:items-center justify-between gap-3">
            <div><h2 className="text-sm font-bold text-slate-900">{activeTab === 'approvals' ? 'Approval queue' : 'Execution history'}</h2><p className="text-xs text-slate-500 mt-1">{activeTab === 'approvals' ? 'Select a plan to inspect its changes and make an approval decision.' : 'Previously reviewed plans and their current recorded outcomes.'}</p></div>
            <div className="flex flex-wrap gap-2">
              <div className="relative"><Search className="w-3.5 h-3.5 absolute left-3 top-2.5 text-slate-400" /><input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search plans..." className="pl-9 pr-3 py-2 rounded-lg border border-slate-200 text-xs outline-none focus:border-blue-400 w-48" /></div>
              <select value={filter} onChange={(event) => setFilter(event.target.value)} className="px-3 py-2 rounded-lg border border-slate-200 text-xs text-slate-700 bg-white"><option>All</option><option>Pending approval</option><option>Approved</option><option>Succeeded</option><option>Rejected</option></select>
            </div>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 text-slate-500"><tr><th className="px-4 py-3 font-semibold">Plan</th><th className="px-4 py-3 font-semibold">Environment</th><th className="px-4 py-3 font-semibold">Changes</th><th className="px-4 py-3 font-semibold">Risk</th><th className="px-4 py-3 font-semibold">Status</th><th className="px-4 py-3"></th></tr></thead>
              <tbody className="divide-y divide-slate-100">
                {filteredPlans.filter((plan) => activeTab !== 'approvals' || plan.status === 'Pending approval').map((plan) => <tr key={plan.id} className="hover:bg-slate-50">
                  <td className="px-4 py-3"><div className="font-semibold text-slate-800">{plan.name}</div><div className="text-[10px] text-slate-400 mt-1 font-mono">{plan.id}</div></td>
                  <td className="px-4 py-3 text-slate-600">{plan.environment}<div className="text-[10px] text-slate-400 mt-1">{plan.region}</div></td>
                  <td className="px-4 py-3"><span className="text-emerald-700">+{plan.create}</span><span className="text-amber-700 ml-2">~{plan.update}</span><span className="text-rose-700 ml-2">-{plan.destroy}</span></td>
                  <td className="px-4 py-3 text-slate-600">{plan.risk}</td>
                  <td className="px-4 py-3"><span className={'px-2 py-1 rounded-full border text-[10px] font-semibold ' + statusClass(plan.status)}>{plan.status}</span></td>
                  <td className="px-4 py-3 text-right"><button onClick={() => selectPlan(plan)} className="text-blue-700 font-semibold hover:text-blue-900">Review <ArrowUpRight className="w-3 h-3 inline ml-1" /></button></td>
                </tr>)}
                {filteredPlans.length === 0 && <tr><td colSpan="6" className="px-4 py-10 text-center text-slate-500">No matching plans found.</td></tr>}
              </tbody>
            </table>
          </div>
        </section>
      )}

      {activeTab === 'plan' && selectedPlan && (
        <div className="space-y-4">
          <div className="rounded-xl border border-slate-200 bg-white p-4">
            <div className="flex flex-col lg:flex-row lg:items-start justify-between gap-4">
              <div><div className="flex items-center gap-2"><span className="font-mono text-[11px] text-blue-700">{selectedPlan.id}</span><span className={'px-2 py-0.5 rounded-full border text-[10px] font-semibold ' + statusClass(selectedPlan.status)}>{selectedPlan.status}</span></div><h2 className="text-lg font-bold text-slate-900 mt-2">{selectedPlan.name}</h2><p className="text-xs text-slate-500 mt-1">{selectedPlan.project} · {selectedPlan.environment} · {selectedPlan.region}</p></div>
              <div className="flex flex-wrap gap-2"><button onClick={() => setActiveTab('approvals')} className="px-3 py-2 border border-slate-200 rounded-lg text-xs font-semibold text-slate-600 hover:bg-slate-50">Back to queue</button>{selectedPlan.status === 'Pending approval' && <button onClick={() => setShowApprovalConfirm(true)} className="px-3 py-2 bg-blue-700 hover:bg-blue-800 text-white rounded-lg text-xs font-semibold flex items-center gap-2"><ShieldCheck className="w-3.5 h-3.5" />Review decision</button>}</div>
            </div>
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 mt-5">
              {[['To create', selectedPlan.create, 'text-emerald-700'], ['To change', selectedPlan.update, 'text-amber-700'], ['To destroy', selectedPlan.destroy, 'text-rose-700'], ['Estimated monthly cost', selectedPlan.estimatedCost, 'text-slate-800']].map((item) => <div key={item[0]} className="rounded-lg bg-slate-50 border border-slate-100 p-3"><div className="text-[11px] text-slate-500">{item[0]}</div><div className={'text-lg font-bold mt-1 ' + item[2]}>{item[1]}</div></div>)}
            </div>
          </div>
          <section className="rounded-xl border border-slate-200 bg-white overflow-hidden">
            <div className="p-4 border-b border-slate-100 flex flex-wrap items-center justify-between gap-2"><div><h3 className="text-sm font-bold text-slate-900">Resource change details</h3><p className="text-xs text-slate-500 mt-1">Review each proposed Terraform resource operation.</p></div><span className="text-xs text-slate-500">{selectedPlan.resources.length} resources in plan</span></div>
            <div className="divide-y divide-slate-100">{selectedPlan.resources.map((resource) => { const Icon = resource.icon; return <div key={resource.address} className="p-4 flex items-start gap-3"><span className="p-2 rounded-lg bg-slate-100 text-slate-600"><Icon className="w-4 h-4" /></span><div className="flex-1 min-w-0"><div className="flex flex-wrap items-center gap-2"><span className="text-xs font-semibold text-slate-800">{resource.name}</span><span className={'px-2 py-0.5 rounded text-[10px] font-bold uppercase ' + actionStyle(resource.action)}>{resource.action}</span></div><div className="font-mono text-[11px] text-blue-700 mt-1 break-all">{resource.address}</div><div className="text-[11px] text-slate-500 mt-1">{resource.type} · {resource.detail}</div></div><Eye className="w-4 h-4 text-slate-300 shrink-0" /></div>; })}</div>
            <div className="p-4 bg-slate-50 border-t border-slate-100"><div className="text-[11px] text-slate-500">Plan integrity digest</div><div className="font-mono text-[11px] text-slate-700 mt-1 break-all">{selectedPlan.digest}</div></div>
          </section>
          {selectedPlan.status === 'Approved' && <div className="rounded-xl border border-emerald-200 bg-emerald-50 p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3"><div><div className="text-sm font-bold text-emerald-900">Approval granted</div><div className="text-xs text-emerald-800 mt-1">This plan is marked as approved in the UI preview.</div></div><button onClick={() => setShowExecutionConfirm(true)} className="px-4 py-2.5 rounded-lg bg-emerald-700 hover:bg-emerald-800 text-white text-xs font-semibold flex items-center gap-2"><Play className="w-3.5 h-3.5" />Preview execution</button></div>}
          {(selectedPlan.status === 'Succeeded' || selectedPlan.status === 'Executing') && <button onClick={() => setActiveTab('console')} className="px-4 py-2.5 rounded-lg bg-slate-900 text-white text-xs font-semibold">Open execution console <ArrowRight className="inline w-3.5 h-3.5 ml-1" /></button>}
        </div>
      )}

      {activeTab === 'console' && (
        <div className="space-y-4">
          <div className="rounded-xl border border-slate-200 bg-white p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3"><div><h2 className="text-sm font-bold text-slate-900">Terraform execution console</h2><p className="text-xs text-slate-500 mt-1">Execution output and operation status for the selected plan.</p></div><span className={'px-2.5 py-1 rounded-full border text-[11px] font-semibold ' + statusClass(executionStatus)}>{executionStatus}</span></div>
          <div className="rounded-xl overflow-hidden border border-slate-800 bg-slate-950">
            <div className="px-4 py-3 bg-slate-900 border-b border-slate-800 flex items-center justify-between"><div className="flex items-center gap-2 text-slate-200 text-xs font-semibold"><TerminalSquare className="w-4 h-4 text-emerald-400" />Execution output <span className="text-slate-500 font-normal">· {selectedPlan?.id}</span></div><span className="text-[10px] text-slate-400">PREVIEW TERMINAL</span></div>
            <div className="p-4 min-h-64 max-h-96 overflow-y-auto font-mono text-[11px] leading-6">{executionLogs.length ? executionLogs.map((line, index) => <div key={index} className="text-emerald-300"><span className="text-slate-600 mr-3">{String(index + 1).padStart(2, '0')}</span>{line}</div>) : <div className="text-slate-500">No execution has been started for this preview. Select an approved plan and choose Preview execution.</div>}</div>
          </div>
          <div className="flex flex-wrap gap-2"><button onClick={() => setActiveTab('plan')} className="px-3 py-2 rounded-lg border border-slate-200 text-xs font-semibold text-slate-700">Back to plan</button>{selectedPlan?.status === 'Approved' && <button onClick={() => setShowExecutionConfirm(true)} className="px-4 py-2 rounded-lg bg-blue-700 hover:bg-blue-800 text-white text-xs font-semibold"><Play className="inline w-3.5 h-3.5 mr-1" />Start preview</button>}</div>
        </div>
      )}

      {activeTab === 'rollback' && (
        <section className="rounded-xl border border-slate-200 bg-white p-6">
          <div className="flex items-start gap-3"><span className="p-2 rounded-lg bg-slate-100 text-slate-600"><RotateCcw className="w-5 h-5" /></span><div><h2 className="text-sm font-bold text-slate-900">Rollback records</h2><p className="text-xs text-slate-500 mt-1">Rollback tracking will be connected to execution state and Terraform recovery workflows in a later integration stage.</p></div></div>
          <div className="mt-6 rounded-lg border border-dashed border-slate-300 p-8 text-center"><History className="w-7 h-7 text-slate-300 mx-auto" /><div className="text-sm font-semibold text-slate-700 mt-2">No rollback records in this preview</div><div className="text-xs text-slate-500 mt-1">This screen is ready for rollback history integration.</div></div>
        </section>
      )}

      {showApprovalConfirm && selectedPlan && (
        <div className="fixed inset-0 z-50 bg-slate-950/40 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="w-full max-w-lg rounded-2xl bg-white shadow-2xl p-5">
            <div className="flex items-center justify-between"><h2 className="text-base font-bold text-slate-900">Review approval decision</h2><button onClick={() => setShowApprovalConfirm(false)} className="p-1.5 rounded-lg hover:bg-slate-100"><X className="w-4 h-4" /></button></div>
            <p className="text-xs text-slate-500 mt-2">You are reviewing <span className="font-semibold text-slate-800">{selectedPlan.id}</span>. Confirm only after checking the resource changes and plan digest.</p>
            <label className="block text-xs font-semibold text-slate-700 mt-4 mb-1.5">Review note</label><textarea value={reviewNote} onChange={(event) => setReviewNote(event.target.value)} rows="3" placeholder="Add the reason for your approval or rejection..." className="w-full border border-slate-200 rounded-lg p-3 text-xs outline-none focus:border-blue-400 resize-y" />
            <div className="flex flex-wrap justify-end gap-2 mt-4"><button onClick={() => setShowApprovalConfirm(false)} className="px-3 py-2 rounded-lg border border-slate-200 text-xs font-semibold text-slate-600">Cancel</button><button onClick={rejectPlan} className="px-3 py-2 rounded-lg border border-rose-200 text-rose-700 hover:bg-rose-50 text-xs font-semibold">Reject plan</button><button onClick={approvePlan} className="px-3 py-2 rounded-lg bg-blue-700 hover:bg-blue-800 text-white text-xs font-semibold"><Check className="inline w-3.5 h-3.5 mr-1" />Approve plan</button></div>
          </div>
        </div>
      )}

      {showExecutionConfirm && selectedPlan && (
        <div className="fixed inset-0 z-50 bg-slate-950/40 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="w-full max-w-md rounded-2xl bg-white shadow-2xl p-5">
            <div className="flex items-center gap-2 text-amber-700"><AlertTriangle className="w-5 h-5" /><h2 className="text-base font-bold text-slate-900">Confirm execution preview</h2></div>
            <p className="text-xs text-slate-600 mt-3">This frontend-only preview will simulate the execution flow for <span className="font-semibold">{selectedPlan.id}</span>. It will not contact AWS or run Terraform.</p>
            <div className="flex justify-end gap-2 mt-5"><button onClick={() => setShowExecutionConfirm(false)} className="px-3 py-2 rounded-lg border border-slate-200 text-xs font-semibold text-slate-600">Cancel</button><button onClick={runExecutionPreview} className="px-4 py-2 rounded-lg bg-blue-700 hover:bg-blue-800 text-white text-xs font-semibold"><Play className="inline w-3.5 h-3.5 mr-1" />Run preview</button></div>
          </div>
        </div>
      )}
    </div>
  );
}
