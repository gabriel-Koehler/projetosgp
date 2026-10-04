import { parseCsvRecords } from './csv-records.js';
export function parseStudentsCsv(source, existing = []) {
  const rows = parseCsvRecords(source);
  const normalize = value => value.trim().toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '');
  const header = (rows.shift() || []).map(normalize);
  if (header.length !== 2 || !header.includes('nome') || !header.includes('matricula')) throw new Error('Use as colunas nome e matricula do modelo CSV.');
  if (!rows.length) throw new Error('O arquivo não contém alunos.');
  if (rows.length > 500) throw new Error('Importe no máximo 500 alunos por arquivo.');
  const seen = new Set(existing.map(a => a.registration));
  return rows.map((columns, index) => {
    const name = (columns[header.indexOf('nome')] || '').trim();
    const registration = (columns[header.indexOf('matricula')] || '').trim();
    let error = '';
    if (columns.length !== 2) error = 'Quantidade de colunas inválida';
    else if (!name || !registration) error = 'Nome e matrícula são obrigatórios';
    else if (name.length > 200 || registration.length > 200) error = 'Campo excede 200 caracteres';
    else if (seen.has(registration)) error = 'Matrícula duplicada no arquivo ou já cadastrada';
    if (!error) seen.add(registration);
    return { line: index + 2, name, registration, error };
  });
}

