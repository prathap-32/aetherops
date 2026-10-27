// frontend/src/components/ui/Button.jsx
import React from 'react';

const VARIANT_MAP = {
  primary: 'bg-blue-600 hover:bg-blue-700 text-white border-transparent shadow-xs focus:ring-blue-500/30',
  secondary: 'bg-white hover:bg-slate-50 text-slate-700 border-slate-200 shadow-xs focus:ring-slate-400/30',
  outline: 'bg-transparent hover:bg-blue-50 text-blue-700 border-blue-200 focus:ring-blue-500/30',
  destructive: 'bg-rose-600 hover:bg-rose-700 text-white border-transparent shadow-xs focus:ring-rose-500/30',
  ghost: 'bg-transparent hover:bg-slate-100 text-slate-600 hover:text-slate-900 border-transparent',
};

const SIZE_MAP = {
  sm: 'text-xs px-2.5 py-1.5 rounded-md gap-1.5',
  md: 'text-xs sm:text-sm px-3.5 py-2 rounded-lg gap-2',
  lg: 'text-sm px-4 py-2.5 rounded-lg gap-2',
};

export default function Button({
  children,
  variant = 'secondary',
  size = 'md',
  icon: Icon,
  iconRight: IconRight,
  isLoading = false,
  disabled = false,
  className = '',
  type = 'button',
  onClick,
  ...props
}) {
  const variantStyles = VARIANT_MAP[variant] || VARIANT_MAP.secondary;
  const sizeStyles = SIZE_MAP[size] || SIZE_MAP.md;

  return (
    <button
      type={type}
      disabled={disabled || isLoading}
      onClick={onClick}
      className={`inline-flex items-center justify-center font-medium border transition cursor-pointer select-none focus:outline-none focus:ring-2 disabled:opacity-50 disabled:cursor-not-allowed ${variantStyles} ${sizeStyles} ${className}`}
      {...props}
    >
      {isLoading ? (
        <svg
          className="animate-spin w-4 h-4 text-current shrink-0"
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
        >
          <circle
            className="opacity-25"
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            strokeWidth="4"
          />
          <path
            className="opacity-75"
            fill="currentColor"
            d="M4 12a8 8 0 018-8v8H4z"
          />
        </svg>
      ) : (
        Icon && <Icon className="w-4 h-4 shrink-0" />
      )}
      {children}
      {IconRight && !isLoading && <IconRight className="w-4 h-4 shrink-0" />}
    </button>
  );
}
