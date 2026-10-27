// frontend/src/components/ui/Badge.jsx
import React from 'react';

const VARIANT_MAP = {
  success: 'bg-emerald-50 text-emerald-700 border-emerald-200',
  warning: 'bg-amber-50 text-amber-700 border-amber-200',
  error: 'bg-rose-50 text-rose-700 border-rose-200',
  info: 'bg-blue-50 text-blue-700 border-blue-200',
  indigo: 'bg-indigo-50 text-indigo-700 border-indigo-200',
  purple: 'bg-violet-50 text-violet-700 border-violet-200',
  neutral: 'bg-slate-100 text-slate-700 border-slate-200',
};

const DOT_MAP = {
  success: 'bg-emerald-500',
  warning: 'bg-amber-500',
  error: 'bg-rose-500',
  info: 'bg-blue-500',
  indigo: 'bg-indigo-500',
  purple: 'bg-violet-500',
  neutral: 'bg-slate-400',
};

export default function Badge({
  children,
  variant = 'neutral',
  size = 'md',
  dot = false,
  className = '',
}) {
  const variantStyles = VARIANT_MAP[variant] || VARIANT_MAP.neutral;
  const dotColor = DOT_MAP[variant] || DOT_MAP.neutral;
  const sizeStyles = size === 'sm' ? 'text-[10px] px-1.5 py-0.5' : 'text-xs px-2.5 py-1';

  return (
    <span
      className={`inline-flex items-center gap-1.5 font-medium rounded-md border ${variantStyles} ${sizeStyles} ${className}`}
    >
      {dot && <span className={`w-1.5 h-1.5 rounded-full ${dotColor}`} />}
      {children}
    </span>
  );
}
