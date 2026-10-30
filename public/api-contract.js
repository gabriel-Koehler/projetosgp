// Contract adapters keep the UI's shape stable across N1 and the persistent API.
export function requestBody(path, body, real) {
  if (!real || body === undefined) return body;
  if (path === '/evaluations') return {
    nome: body.name, turma_id: Number(body.classId), questao_ids: body.questionIds.map(Number),
    nota_maxima: body.maxGrade ?? 10, gabaritos: body.answerOverrides || {},
    configuracao: {
      quantidade: body.versionCount, nomenclatura: 'personalizada', nomes_personalizados: body.versionNames,
      mesmas_questoes: body.sameQuestions !== false,
      questoes_por_versao: body.sameQuestions === false ? body.questionsPerVersion : null,
      embaralhar_questoes: !!body.shuffleQuestions, embaralhar_alternativas: !!body.shuffleAlternatives
    }
  };
  if (/^\/questions(?:\/[^/?]+)?$/.test(path)) return {
    enunciado: body.statement,
    alternativas: body.options,
    correta: body.answer,
    disciplina: body.subject || null,
    categoria: body.category || null,
    dificuldade: ({'Fácil':'facil','Médio':'media','Difícil':'dificil'})[body.difficulty] || null
  };
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
  if (path.startsWith('/questions/importar')) return payload;
  if (path.startsWith('/questions') && payload?.itens) return {
    ...payload, itens: payload.itens.map(value => responseData('/questions/item', value, true))
  };
  const map = value => {
    if (!value) return value;
    if (path.startsWith('/public/gabaritos')) return {
      name: value.avaliacao, version: value.versao,
      questions: value.gabarito.map(item => ({position:item.questao,answerLetter:item.alternativa}))
    };
    if (path.startsWith('/evaluations')) return {
      id: String(value.id), name: value.nome, classId: value.turma_id == null ? '' : String(value.turma_id),
      className: value.turma_nome, semesterName: value.semestre_nome,
      maxGrade: value.nota_maxima, keyPublished: value.gabarito_liberado, createdAt: value.criada_em,
      versionCount: value.quantidade_versoes ?? value.versoes?.length ?? 0,
      questionCount: value.quantidade_questoes ?? value.versoes?.[0]?.questoes.length ?? 0,
      versions: value.versoes?.map(version => ({
        id: String(version.id), name: version.nome, code: version.codigo,
        studentUrl: version.url_aluno, qrUrl: version.url_qrcode,
        questions: version.questoes.map(question => ({
          id: question.questao_id, position: question.numero, statement: question.enunciado,
          options: question.alternativas, answerLetter: question.correta,
          correctAnswer: question.alternativas[question.correta.charCodeAt(0)-65],
          originalOrder: question.ordem_original
        }))
      }))
    };
    if (path.startsWith('/questions') && value.enunciado !== undefined) return {
      id: String(value.id), statement: value.enunciado, options: value.alternativas,
      answer: value.correta, subject: value.disciplina || '', category: value.categoria || '',
      difficulty: ({facil:'Fácil',media:'Médio',dificil:'Difícil'})[value.dificuldade] || ''
    };
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
