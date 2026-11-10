// frontend/src/components/ui/PageHeader.jsx
import React from 'react';

export default function PageHeader({
  title,
  description,
  badge,
  actions,
  breadcrumbs,
  className = '',
}) {
  return (
    <div className={`pb-4 border-b border-slate-200/90 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 ${className}`}>
      <div className="space-y-1">
        {breadcrumbs && (
          <div className="text-xs sm:text-sm text-slate-500 flex items-center gap-1.5 pb-1 font-medium">
            {breadcrumbs}
          </div>
        )}
        <div className="flex items-center gap-2.5 flex-wrap">
          <h1 className="text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">
            {title}
          </h1>
          {badge}
        </div>
        {description && (
          <p className="text-sm sm:text-base text-slate-600 max-w-3xl leading-relaxed">
            {description}
          </p>
        )}
      </div>

      {actions && (
        <div className="flex items-center gap-2.5 sm:gap-3 shrink-0 flex-wrap">
          {actions}
        </div>
      )}
    </div>
  );
}
