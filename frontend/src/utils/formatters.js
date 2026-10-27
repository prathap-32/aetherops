// frontend/src/utils/formatters.js

/**
 * Sanitizes and formats an AI/Architecture engine provider string into
 * a clean, professional, enterprise-grade display label.
 * Strictly prevents internal fallback messages, JSON decoder traces,
 * or raw exception strings from displaying in user interfaces.
 */
export function formatAiProvider(rawProvider) {
  if (!rawProvider || typeof rawProvider !== 'string') {
    return 'AetherOps Architecture Engine';
  }

  const lower = rawProvider.toLowerCase();

  // If the raw string contains internal error signatures or parser traces,
  // sanitize it completely to the clean engine name
  if (
    lower.includes('fallback') ||
    lower.includes('expecting') ||
    lower.includes('delimiter') ||
    lower.includes('jsondecode') ||
    lower.includes('error') ||
    lower.includes('traceback')
  ) {
    if (lower.includes('deterministic') || lower.includes('rule')) {
      return 'AetherOps Rules Engine';
    }
    return 'AetherOps Architecture Engine';
  }

  // Gemini models
  if (lower.includes('gemini-2.5-flash') || lower.includes('gemini 2.5')) {
    return 'Google Gemini 2.5 Flash';
  }
  if (lower.includes('gemini-2.0-flash') || lower.includes('gemini 2.0')) {
    return 'Google Gemini 2.0 Flash';
  }
  if (lower.includes('gemini')) {
    return 'Google Gemini Cloud AI';
  }

  // Deterministic rule engines
  if (lower.includes('deterministic_rules_engine (local)')) {
    return 'AetherOps Rules Engine (Local)';
  }
  if (lower.includes('deterministic_rules_engine') || lower.includes('deterministic')) {
    return 'AetherOps Rules Engine';
  }

  // Standard fallback
  return rawProvider.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
}

/**
 * Formats a currency number into USD with 2 decimal places.
 */
export function formatCurrency(amount) {
  const num = typeof amount === 'number' ? amount : parseFloat(amount) || 0;
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(num);
}

/**
 * Formats a standard AWS 12-digit account number with hyphens (e.g., 1092-8374-6519)
 */
export function formatAccountId(accountId) {
  if (!accountId) return '1092-8374-6519';
  const clean = String(accountId).replace(/\D/g, '');
  if (clean.length === 12) {
    return `${clean.slice(0, 4)}-${clean.slice(4, 8)}-${clean.slice(8, 12)}`;
  }
  return accountId;
}
