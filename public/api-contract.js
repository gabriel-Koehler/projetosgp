// Contract adapters keep the UI's shape stable across N1 and the persistent API.
export function requestBody(path, body, real) {
  if (!real || body === undefined) return body;
  if (path === '/auth/login') return {
    username: body.email.trim(),
    password: body.password
  };
  if (/^\/semesters(?:\/[^/]+)?$/.test(path)) return {
    nome: body.name,
    data_inicio: body.startDate || null,
    data_fim: body.endDate || null
  };
  if (/^\/semesters\/[^/]+\/ativo$/.test(path)) return {
    ativo: body.active
  };
  if (/^\/classes(?:\/[^/]+)?$/.test(path)) return {
    nome: body.name,
    semestre_id: Number(body.semesterId),
    disciplina: body.subject || null
  };
  return body;
}
export function responseData(path, payload, real) {
  if (!real) return payload?.data;
  const map = value => {
    if (!value) return value;
    if (path.startsWith('/auth/')) return {
      id: value.username,
      name: value.nome,
      email: value.username
    };
    if (path.startsWith('/semesters')) return {
      id: String(value.id),
      name: value.nome,
      active: value.ativo,
      startDate: value.data_inicio,
      endDate: value.data_fim
    };
    if (path.startsWith('/classes')) return {
      id: String(value.id),
      name: value.nome,
      semesterId: String(value.semestre_id),
      subject: value.disciplina || '',
      code: value.disciplina || 'Sem disciplina'
    };
    return value;
  };
  return Array.isArray(payload) ? payload.map(map) : map(payload);
}
export function errorMessage(payload, status) {
  if (typeof payload?.error?.message === 'string') return payload.error.message;
  if (typeof payload?.detail === 'string') return payload.detail;
  if (Array.isArray(payload?.detail)) return 'Confira os campos informados. Há valores inválidos ou obrigatórios ausentes.';
  if (status === 401) return 'Sua sessão expirou. Entre novamente.';
  if (status === 409) return 'Este cadastro já existe ou possui vínculos que impedem a operação.';
  if (status >= 500) return 'Serviço indisponível. Tente novamente em instantes.';
  return 'Não foi possível concluir a operação.';
}
