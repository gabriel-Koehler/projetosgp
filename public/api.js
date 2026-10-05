import {
  requestBody,
  responseData,
  errorMessage
} from './api-contract.js';
const base = (window.APP_CONFIG?.apiBaseUrl || '/api').replace(/\/$/, '');
const real = window.APP_CONFIG?.dataMode === 'real';
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
      body: body === undefined ? undefined : JSON.stringify(requestBody(path, body, real))
    });
    const text = await response.text();
    let payload;
    try {
      payload = text ? JSON.parse(text) : null;
    } catch {
      throw new Error(errorMessage(null, response.status >= 400 ? response.status : 502));
    }
    if (!response.ok) {
      if (response.status === 401 && (!path.startsWith('/auth/') || path === '/auth/me')) location.assign('/?expired=1');
      throw new Error(errorMessage(payload, response.status));
    }
    return response.status === 204 ? null : responseData(path, payload, real);
  } catch (error) {
    if (error.name === 'AbortError' || error instanceof TypeError) throw new Error('Não foi possível conectar. Tente novamente.');
    throw error;
  } finally {
    clearTimeout(timeout);
  }
}
