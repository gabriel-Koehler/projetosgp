const base = (window.APP_CONFIG?.apiBaseUrl || '/api').replace(/\/$/, '');
const resources = {
  semesters: 'semestres',
  classes: 'turmas',
  students: 'alunos',
  questions: 'questoes',
  evaluations: 'avaliacoes',
  results: 'resultados'
};
const route = path => path.replace(/^\/([^/]+)/, (_, name) => '/' + (resources[name] || name));
export async function api(path, {
  method = 'GET',
  body
} = {}) {
  const controller = new AbortController(),
    timeout = setTimeout(() => controller.abort(), 12000);
  try {
    const response = await fetch(base + route(path), {
      method,
      credentials: 'include',
      signal: controller.signal,
      headers: {
        'Content-Type': 'application/json'
      },
      body: body === undefined ? undefined : JSON.stringify(body)
    });
    const payload = await response.json();
    if (!response.ok) {
      if (response.status === 401 && (!path.startsWith('/auth/') || path === '/auth/me')) location.assign('/');
      throw new Error(payload.error?.message || 'Não foi possível concluir a operação.');
    }
    return payload.data;
  } catch (e) {
    if (e.name === 'AbortError' || e instanceof TypeError) throw new Error('Não foi possível conectar. Tente novamente.');
    throw e;
  } finally {
    clearTimeout(timeout);
  }
}
