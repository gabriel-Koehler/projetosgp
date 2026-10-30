import { api } from './api.js';
import { escapeHtml as esc } from './html.js';

export function importRealQuestions(onImported) {
  const $ = id => document.getElementById(id);
  const dialog = $('modal'), form = $('modal-form');
  $('modal-title').textContent = 'Importar questões';
  $('modal-error').hidden = true;
  $('modal-fields').innerHTML = '<p class="muted">Envie CSV ou Excel (.xlsx) de até 5 MB e 5000 questões. Confira a prévia antes de confirmar. Apenas as linhas válidas serão gravadas.</p><div class="actions"><a href="/api/questoes/modelo.csv" download>↓ Modelo CSV</a><a href="/api/questoes/modelo.xlsx" download>↓ Modelo Excel</a></div><label>Arquivo CSV ou Excel<input id="questions-file" type="file" accept=".csv,.xlsx" required></label><p id="question-import-summary" role="status">Nenhum arquivo selecionado.</p><div id="question-import-preview" class="import-preview"></div>';
  const submit = form.querySelector('[type=submit]');
  const fileInput = $('questions-file');
  submit.hidden = false; submit.disabled = true; submit.textContent = 'Importar questões válidas';
  let selectedFile, version = 0;
  const error = message => { $('modal-error').textContent = message; $('modal-error').hidden = false; };
  const upload = (file, confirm) => {
    const body = new FormData(); body.append('arquivo', file);
    return api('/questions/importar?confirmar=' + confirm, {method:'POST', body});
  };
  $('questions-file').onchange = async event => {
    const ticket = ++version;
    selectedFile = undefined; submit.disabled = true; $('modal-error').hidden = true;
    $('question-import-preview').innerHTML = '';
    const file = event.target.files[0];
    if (!file) { $('question-import-summary').textContent = 'Nenhum arquivo selecionado.'; return; }
    $('question-import-summary').textContent = 'Validando arquivo…';
    try {
      if (!/\.(csv|xlsx)$/i.test(file.name) || file.size > 5 * 1024 * 1024) throw new Error('Selecione CSV ou Excel (.xlsx) de até 5 MB.');
      const preview = await upload(file, false);
      if (ticket !== version || !dialog.open || $('questions-file') !== fileInput) return;
      const rows = [
        ...preview.validas.map(row => ({...row, mensagens:[]})),
        ...preview.erros.map(row => ({...row, dados:{}}))
      ].sort((a,b) => a.linha - b.linha);
      $('question-import-summary').textContent = preview.validas.length + ' válidas · ' + preview.erros.length + ' inválidas. Nada foi gravado ainda.';
      $('question-import-preview').innerHTML = rows.map(row => '<article class="import-question ' + (row.mensagens.length ? 'invalid-row' : '') + '"><small>Linha ' + row.linha + ' · ' + esc(row.dados.disciplina || '') + '</small><p>' + esc(row.dados.enunciado || '') + '</p>' + (row.dados.alternativas ? '<details><summary>Ver alternativas</summary>' + row.dados.alternativas.map((option,i) => '<p>' + String.fromCharCode(65+i) + ' · ' + esc(option) + '</p>').join('') + '</details><strong>Gabarito: ' + esc(row.dados.correta) + '</strong>' : '') + '<p>' + esc(row.mensagens.join(' ') || '✓ Válida') + '</p></article>').join('');
      selectedFile = file; submit.disabled = !preview.validas.length;
      submit.textContent = 'Importar ' + preview.validas.length + ' questões válidas';
    } catch (e) {
      if (ticket !== version || !dialog.open || $('questions-file') !== fileInput) return;
      error(e.message); $('question-import-summary').textContent = 'Não foi possível validar o arquivo.';
    }
  };
  form.onsubmit = async event => {
    event.preventDefault();
    if (submit.disabled || !selectedFile) return;
    submit.disabled = true; submit.textContent = 'Importando…';
    $('questions-file').disabled = true; $('close-modal').disabled = true;
    const preventClose = event => event.preventDefault();
    dialog.addEventListener('cancel', preventClose);
    try {
      const result = await upload(selectedFile, true);
      // The server validates again against the current database before committing.
      selectedFile = undefined;
      if (!result.importados) {
        $('question-import-summary').textContent = 'Nenhuma questão importada. Selecione o arquivo novamente para atualizar a prévia.';
        error(result.erros.map(row => 'Linha ' + row.linha + ': ' + row.mensagens.join(' ')).join('\n'));
      } else {
        dialog.close();
        await onImported(result.importados);
      }
    } catch (e) {
      error(e.message);
      // A timeout may happen after a commit. A fresh preview prevents blind retries.
      selectedFile = undefined;
      $('question-import-summary').textContent = 'Confira o banco e selecione o arquivo novamente antes de tentar outra importação.';
    } finally {
      dialog.removeEventListener('cancel', preventClose);
      $('questions-file').disabled = false; $('close-modal').disabled = false;
      if (!selectedFile) fileInput.value = '';
      submit.textContent = 'Importar questões válidas';
    }
  };
  dialog.showModal();
}
