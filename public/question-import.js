import { importSpreadsheet } from './spreadsheet-import.js';
import { escapeHtml as esc } from './html.js';

export function importRealQuestions(onImported) {
  importSpreadsheet({
    title: 'Importar questões',
    description: 'Envie CSV ou Excel (.xlsx) de até 5 MB e 5000 questões. Confira a prévia antes de confirmar. Apenas as linhas válidas serão gravadas.',
    modelPath: '/api/questoes/modelo',
    uploadPath: '/questions/importar',
    validLabel: 'questões válidas',
    onImported,
    renderRow: row => '<article class="import-question ' + (row.mensagens.length ? 'invalid-row' : '') + '"><small>Linha ' + row.linha + ' · ' + esc(row.dados.disciplina || '') + '</small><p>' + esc(row.dados.enunciado || '') + '</p>' + (row.dados.alternativas ? '<details><summary>Ver alternativas</summary>' + row.dados.alternativas.map((option,i) => '<p>' + String.fromCharCode(65+i) + ' · ' + esc(option) + '</p>').join('') + '</details><strong>Gabarito: ' + esc(row.dados.correta) + '</strong>' : '') + '<p>' + esc(row.mensagens.join(' ') || '✓ Válida') + '</p></article>'
  });
}
