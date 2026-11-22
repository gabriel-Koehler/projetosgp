import { api } from './api.js';

export function importSpreadsheet({title, description, modelPath, uploadPath, validLabel, renderRow, onImported, maxBytes = 5 * 1024 * 1024}) {
  const $ = id => document.getElementById(id);
  const dialog = $('modal'), form = $('modal-form');
  $('modal-title').textContent = title;
  $('modal-error').hidden = true;
  $('modal-fields').innerHTML = `
    <p class="muted">${description}</p>
    <div class="actions">
      <a href="${modelPath}.csv" download>↓ Modelo CSV</a>
      <a href="${modelPath}.xlsx" download>↓ Modelo Excel</a>
    </div>
    <label>Arquivo CSV ou Excel<input id="spreadsheet-file" type="file" accept=".csv,.xlsx" required></label>
    <p id="spreadsheet-summary" role="status">Nenhum arquivo selecionado.</p>
    <div id="spreadsheet-preview" class="import-preview"></div>`;
  const submit = form.querySelector('[type=submit]');
  const fileInput = $('spreadsheet-file');
  const summary = $('spreadsheet-summary');
  const previewPanel = $('spreadsheet-preview');
  submit.hidden = false; submit.disabled = true; submit.textContent = 'Importar ' + validLabel;
  let selectedFile, version = 0;
  const error = message => { $('modal-error').textContent = message; $('modal-error').hidden = false; };
  const upload = (file, confirm) => {
    const body = new FormData(); body.append('arquivo', file);
    return api(uploadPath + '?confirmar=' + confirm, {method:'POST', body});
  };
  fileInput.onchange = async event => {
    const ticket = ++version;
    selectedFile = undefined; submit.disabled = true; $('modal-error').hidden = true;
    previewPanel.innerHTML = '';
    const file = event.target.files[0];
    if (!file) { summary.textContent = 'Nenhum arquivo selecionado.'; return; }
    summary.textContent = 'Validando arquivo…';
    try {
      if (!/\.(csv|xlsx)$/i.test(file.name) || file.size > maxBytes) throw new Error('Selecione CSV ou Excel (.xlsx) de até ' + (maxBytes / 1024 / 1024) + ' MB.');
      const preview = await upload(file, false);
      if (ticket !== version || !dialog.open || $('spreadsheet-file') !== fileInput) return;
      const rows = [
        ...preview.validas.map(row => ({...row, mensagens:[]})),
        ...preview.erros.map(row => ({...row, dados:{}}))
      ].sort((a,b) => a.linha - b.linha);
      summary.textContent = preview.validas.length + ' válidas · ' + preview.erros.length + ' inválidas. Nada foi gravado ainda.';
      previewPanel.innerHTML = rows.map(renderRow).join('');
      selectedFile = file; submit.disabled = !preview.validas.length;
      submit.textContent = 'Importar ' + preview.validas.length + ' ' + validLabel;
    } catch (e) {
      if (ticket !== version || !dialog.open || $('spreadsheet-file') !== fileInput) return;
      error(e.message); summary.textContent = 'Não foi possível validar o arquivo.';
    }
  };
  form.onsubmit = async event => {
    event.preventDefault();
    if (submit.disabled || !selectedFile) return;
    submit.disabled = true; submit.textContent = 'Importando…';
    fileInput.disabled = true; $('close-modal').disabled = true;
    const preventClose = event => event.preventDefault();
    dialog.addEventListener('cancel', preventClose);
    try {
      const result = await upload(selectedFile, true);
      // The server validates again against the current database before committing.
      selectedFile = undefined;
      if (!result.importados) {
        summary.textContent = 'Nenhum registro importado. Selecione o arquivo novamente para atualizar a prévia.';
        error(result.erros.map(row => 'Linha ' + row.linha + ': ' + row.mensagens.join(' ')).join('\n'));
      } else {
        dialog.close();
        await onImported(result.importados, result.erros.length);
      }
    } catch (e) {
      error(e.message);
      // A timeout may happen after a commit. A fresh preview prevents blind retries.
      selectedFile = undefined;
      summary.textContent = 'Confira a lista e selecione o arquivo novamente antes de tentar outra importação.';
    } finally {
      dialog.removeEventListener('cancel', preventClose);
      fileInput.disabled = false; $('close-modal').disabled = false;
      if (!selectedFile) fileInput.value = '';
      submit.textContent = 'Importar ' + validLabel;
    }
  };
  dialog.showModal();
}
