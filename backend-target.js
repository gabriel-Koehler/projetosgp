// Resolve at request time: service bindings may be injected after module loading.
export function backendTarget(env = process.env) {
  let value = env.PYTHON_API_URL || env.API_TARGET;
  let publicRoute = false;
  if (!value && env.VERCEL) {
    value = env.VERCEL_ENV === 'preview'
      ? (env.VERCEL_URL && 'https://' + env.VERCEL_URL)
      : env.PUBLIC_BASE_URL || (env.VERCEL_PROJECT_PRODUCTION_URL && 'https://' + env.VERCEL_PROJECT_PRODUCTION_URL);
    publicRoute = true;
    if (!value) throw new Error('API_ORIGIN_MISSING');
  }
  const url = new URL(value || 'http://127.0.0.1:8000');
  if (!['http:', 'https:'].includes(url.protocol) || url.username || url.password) throw new Error('API_ORIGIN_INVALID');
  if (env.VERCEL && (url.protocol !== 'https:' || ['localhost', '127.0.0.1', '[::1]'].includes(url.hostname))) {
    throw new Error('API_ORIGIN_INVALID');
  }
  return {origin:url.origin, publicRoute};
}
