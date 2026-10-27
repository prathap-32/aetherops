// frontend/src/components/ui/ErrorAlert.jsx
import React, { useState } from 'react';
import { AlertCircle, ChevronDown, ChevronRight, RefreshCw, X } from 'lucide-react';

export default function ErrorAlert({
  title = 'Unable to complete operation',
  message,
  diagnostics,
  onRetry,
  onDismiss,
  className = '',
}) {
  const [showDiagnostics, setShowDiagnostics] = useState(false);

  return (
    <div
      role="alert"
      className={`rounded-xl border border-rose-200 bg-rose-50/90 p-4 text-slate-800 shadow-xs ${className}`}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-start gap-3 min-w-0">
          <AlertCircle className="w-5 h-5 text-rose-600 shrink-0 mt-0.5" />
          <div className="min-w-0 space-y-1">
            <h4 className="text-sm font-semibold text-rose-950">{title}</h4>
            <p className="text-xs text-rose-800 leading-relaxed">
              {message || 'An unexpected problem occurred. Please verify your inputs or retry.'}
            </p>

            {diagnostics && (
              <div className="pt-2">
                <button
                  type="button"
                  onClick={() => setShowDiagnostics((prev) => !prev)}
                  className="text-[11px] font-medium text-rose-700 hover:text-rose-900 inline-flex items-center gap-1 cursor-pointer focus:outline-none"
                >
                  {showDiagnostics ? (
                    <ChevronDown className="w-3.5 h-3.5" />
                  ) : (
                    <ChevronRight className="w-3.5 h-3.5" />
                  )}
                  <span>{showDiagnostics ? 'Hide details' : 'View diagnostic details'}</span>
                </button>

                {showDiagnostics && (
                  <div className="mt-2 p-2.5 rounded-lg bg-white/90 border border-rose-200 text-[11px] font-mono text-slate-700 overflow-x-auto max-h-36">
                    {typeof diagnostics === 'object'
                      ? JSON.stringify(diagnostics, null, 2)
                      : String(diagnostics)}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        <div className="flex items-center gap-2 shrink-0">
          {onRetry && (
            <button
              type="button"
              onClick={onRetry}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-lg bg-rose-600 hover:bg-rose-700 text-white transition shadow-xs cursor-pointer"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              <span>Retry</span>
            </button>
          )}

          {onDismiss && (
            <button
              type="button"
              onClick={onDismiss}
              className="p-1 rounded-md text-rose-500 hover:text-rose-700 hover:bg-rose-100 transition cursor-pointer"
              aria-label="Dismiss alert"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
