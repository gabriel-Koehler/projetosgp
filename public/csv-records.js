export function parseCsvRecords(source) {
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
      if (char === '"' || closed) throw new Error('CSV inválido: há texto após o fechamento de aspas.');
      field += char;
    }
  }
  if (quoted) throw new Error('CSV inválido: aspas não foram fechadas.');
  row.push(field);
  if (row.some(value => value.trim())) rows.push(row);
  return rows;
}
