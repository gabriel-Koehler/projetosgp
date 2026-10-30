import { parseCsvRecords } from './csv-records.js';
export const questionFingerprint = q => JSON.stringify([q.statement, q.subject, q.options, q.answer]);
export function parseQuestionsCsv(source, existing = []) {
  const records = parseCsvRecords(source);
  const normalize = value => value.trim().toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '');
  const header = (records.shift() || []).map(normalize);
  const expected = ['enunciado', 'disciplina', 'dificuldade', 'alternativa_a', 'alternativa_b', 'alternativa_c', 'alternativa_d', 'gabarito'];
  if (header.length !== expected.length || !expected.every(key => header.includes(key))) throw new Error('Use as oito colunas do modelo de questões.');
  if (!records.length || records.length > 500) throw new Error('O arquivo deve conter entre 1 e 500 questões.');
  const seen = new Set(existing.map(questionFingerprint));
  return records.map((columns, index) => {
    const get = key => (columns[header.indexOf(key)] || '').trim();
    const question = { statement: get('enunciado'), subject: get('disciplina'),
      difficulty: ({ facil: 'Fácil', medio: 'Médio', dificil: 'Difícil' })[normalize(get('dificuldade'))] || '',
      options: ['a','b','c','d'].map(a => get('alternativa_' + a)), answer: get('gabarito').toUpperCase() };
    let error = '';
    if (columns.length !== 8) error = 'Quantidade de colunas inválida';
    else if (!question.statement || !question.subject || question.options.some(o => !o)) error = 'Enunciado, disciplina e quatro alternativas são obrigatórios';
    else if (question.statement.length > 2000 || question.subject.length > 200 || question.options.some(o => o.length > 500)) error = 'Campo excede o limite permitido';
    else if (!question.difficulty) error = 'Dificuldade deve ser Fácil, Médio ou Difícil';
    else if (!/^[A-D]$/.test(question.answer)) error = 'Gabarito deve ser A, B, C ou D';
    else if (seen.has(questionFingerprint(question))) error = 'Questão duplicada no arquivo ou no banco';
    if (!error) seen.add(questionFingerprint(question));
    return { line: index + 2, question, error };
  });
}

