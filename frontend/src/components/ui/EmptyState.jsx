// frontend/src/components/ui/EmptyState.jsx
import React from 'react';

export default function EmptyState({
  icon: Icon,
  title,
  description,
  action,
  secondaryAction,
  className = '',
}) {
  return (
    <div
      className={`rounded-2xl border border-slate-200/90 bg-white p-8 sm:p-12 text-center max-w-xl mx-auto shadow-xs ${className}`}
    >
      {Icon && (
        <div className="w-16 h-16 rounded-2xl bg-blue-50 text-blue-700 border border-blue-100 flex items-center justify-center mx-auto mb-5 shadow-2xs">
          <Icon className="w-8 h-8" />
        </div>
      )}
      <h3 className="text-lg sm:text-xl font-bold text-slate-900 tracking-tight">
        {title}
      </h3>
      {description && (
        <p className="text-sm sm:text-base text-slate-600 mt-2.5 leading-relaxed max-w-md mx-auto">
          {description}
        </p>
      )}
      {(action || secondaryAction) && (
        <div className="mt-6 flex flex-wrap items-center justify-center gap-3.5">
          {action}
          {secondaryAction}
        </div>
      )}
    </div>
  );
}
