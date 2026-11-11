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
      className={`rounded-2xl border border-rose-200 bg-rose-50/90 p-5 text-slate-900 shadow-xs ${className}`}
    >
      <div className="flex items-start justify-between gap-3.5">
        <div className="flex items-start gap-3.5 min-w-0">
          <AlertCircle className="w-6 h-6 text-rose-600 shrink-0 mt-0.5" />
          <div className="min-w-0 space-y-1.5">
            <h4 className="text-base sm:text-lg font-bold text-rose-950">{title}</h4>
            <p className="text-sm sm:text-base text-rose-900 leading-relaxed">
              {message || 'An unexpected problem occurred. Please verify your inputs or retry.'}
            </p>

            {diagnostics && (
              <div className="pt-2">
                <button
                  type="button"
                  onClick={() => setShowDiagnostics((prev) => !prev)}
                  className="text-xs sm:text-sm font-semibold text-rose-800 hover:text-rose-950 inline-flex items-center gap-1.5 cursor-pointer focus:outline-none"
                >
                  {showDiagnostics ? (
                    <ChevronDown className="w-4 h-4" />
                  ) : (
                    <ChevronRight className="w-4 h-4" />
                  )}
                  <span>{showDiagnostics ? 'Hide details' : 'View diagnostic details'}</span>
                </button>

                {showDiagnostics && (
                  <div className="mt-2.5 p-3 rounded-xl bg-white/95 border border-rose-200 text-xs sm:text-sm font-mono text-slate-800 overflow-x-auto max-h-48">
                    {typeof diagnostics === 'object'
                      ? JSON.stringify(diagnostics, null, 2)
                      : String(diagnostics)}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        <div className="flex items-center gap-2.5 shrink-0">
          {onRetry && (
            <button
              type="button"
              onClick={onRetry}
              className="inline-flex items-center gap-2 px-4 py-2.5 text-sm sm:text-base font-semibold rounded-xl bg-rose-600 hover:bg-rose-700 text-white transition shadow-xs cursor-pointer min-h-[44px]"
            >
              <RefreshCw className="w-4 h-4" />
              <span>Retry</span>
            </button>
          )}

          {onDismiss && (
            <button
              type="button"
              onClick={onDismiss}
              className="p-2 rounded-lg text-rose-600 hover:text-rose-900 hover:bg-rose-100 transition cursor-pointer min-h-[44px] min-w-[44px] flex items-center justify-center"
              aria-label="Dismiss alert"
            >
              <X className="w-5 h-5" />
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
