// CSV parser: UTF-8 BOM, comma/semicolon, CRLF and quoted fields.
export function parseStudentsCsv(source, existing = []) {
  if (source.length > 1024 * 1024) throw new Error('O arquivo deve ter no máximo 1 MB.');
  source = source.replace(/^\uFEFF/, '');
  const firstLine = source.split(/\r?\n/)[0];
  const delimiter = firstLine.includes(';') ? ';' : ',';
  const rows = [];
  let row = [], field = '', quoted = false, closed = false;
  for (let i = 0; i < source.length; i++) {
    const char = source[i];
    if (quoted) {
      if (char === '"') {
        if (source[i + 1] === '"') { field += '"'; i++; }
        else { quoted = false; closed = true; }
      } else field += char;
    } else if (char === '"' && field === '' && !closed) quoted = true;
    else if (char === delimiter) { row.push(field); field = ''; closed = false; }
    else if (char === '\n' || char === '\r') {
      if (char === '\r' && source[i + 1] === '\n') i++;
      row.push(field);
      if (row.some(value => value.trim())) rows.push(row);
      row = []; field = ''; closed = false;
    } else {
      if (closed) throw new Error('CSV inválido: há texto após o fechamento de aspas.');
      field += char;
    }
  }
  if (quoted) throw new Error('CSV inválido: aspas não foram fechadas.');
  row.push(field);
  if (row.some(value => value.trim())) rows.push(row);
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

