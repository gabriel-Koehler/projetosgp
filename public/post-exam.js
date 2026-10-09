import {
  api
} from './api.js';
import {
  escapeHtml as esc
} from './html.js';
const letters = ['A', 'B', 'C', 'D'];
const choose = (label, name, items) => `<label>${label}<select name="${name}">${items.map(i => `<option value="${esc(i.id)}">${esc(i.name)}</option>`).join('')}</select></label>`;
const title = (name, sub) => `<header class="section-heading"><div><h1>${name}</h1><p>${sub}</p></div></header>`;
const find = (items, id) => items.find(i => i.id === id)?.name || '—';

export function renderCorrection(root, state, refresh, notice) {
  root.innerHTML = title('Correção de provas', 'Envie uma folha, simule a leitura e confira as respostas antes de salvar.') +
    (!state.evaluations.length ? '<section class="panel empty"><h2>Crie uma avaliação primeiro</h2><a href="#create" class="btn">Criar avaliação</a></section>' : `<form id="correction-form" class="panel correction-panel">
    <span class="badge">Ambiente de simulação</span><p>A leitura gera respostas fictícias. O arquivo fica apenas neste navegador; não há reconhecimento óptico nesta etapa.</p>
    <h2>1. Identifique a prova</h2>${choose('Avaliação', 'evaluationId', state.evaluations)}<div id="correction-context" class="grid-two"></div>
    <h2>2. Envie a folha de respostas</h2><label>Imagem PNG/JPEG ou PDF · até 10 MB<input id="answer-file" type="file" accept="image/png,image/jpeg,application/pdf"></label>
    <div id="file-preview"></div><div class="actions"><button type="button" id="simulate-reading" disabled>Simular leitura</button><button type="button" id="manual-reading" class="secondary">Informar respostas manualmente</button></div>
    <div id="reading-status" role="status" aria-live="polite"></div><progress id="reading-progress" max="3" value="0" hidden aria-label="Progresso da leitura simulada"></progress>
    <section id="answer-review" hidden><h2>3. Revise as respostas</h2><p>Confira cada marcação e ajuste o que for necessário. A nota será calculada pelo gabarito da versão selecionada.</p><div id="read-answers" class="review-grid"></div><label class="confirm-review"><input id="review-confirmation" type="checkbox" required>Conferi as respostas e a identificação do aluno e da versão.</label><button type="submit" id="save-correction">Corrigir e salvar resultado</button></section>
    <p id="correction-error" role="alert" class="form-error" hidden></p></form>`);
  if (!state.evaluations.length) return () => {};
  const form = root.querySelector('form'),
    $ = id => form.querySelector('#' + id);
  let file = null,
    url = null,
    generation = 0,
    disposed = false,
    busy = false;
  const error = message => {
    $('correction-error').textContent = message;
    $('correction-error').hidden = !message;
  };
  const evaluation = () => state.evaluations.find(e => e.id === form.elements.evaluationId.value);
  const version = () => evaluation().versions.find(v => v.name === form.elements.version.value);
  const clearFile = (preserveInput = false) => {
    if (url) URL.revokeObjectURL(url);
    url = null;
    file = null;
    if (!preserveInput) $('answer-file').value = '';
    $('file-preview').replaceChildren();
    $('simulate-reading').disabled = true;
  };
  const reset = (preserveInput = false) => {
    generation++;
    $('answer-review').hidden = true;
    $('read-answers').replaceChildren();
    $('review-confirmation').checked = false;
    $('reading-status').textContent = '';
    $('reading-progress').hidden = true;
    error('');
    clearFile(preserveInput === true);
  };
  const context = () => {
    reset();
    $('correction-context').innerHTML = choose('Aluno', 'studentId', state.students.filter(s => s.classId === evaluation().classId)) + choose('Versão', 'version', evaluation().versions.map(v => ({
      id: v.name,
      name: 'Versão ' + v.name
    })));
    form.elements.studentId.required = true;
    form.elements.version.onchange = reset;
    form.elements.studentId.onchange = reset;
    const noStudents = !form.elements.studentId.value;
    $('manual-reading').disabled = noStudents;
    $('answer-file').disabled = noStudents;
    if (noStudents) error('Esta turma não tem alunos. Cadastre os alunos antes de corrigir.');
  };
  form.elements.evaluationId.onchange = context;
  context();
  const lock = value => {
    busy = value;
    for (const el of [form.elements.evaluationId, form.elements.studentId, form.elements.version, $('answer-file'), $('manual-reading')]) el.disabled = value;
    $('simulate-reading').disabled = value || !file;
    $('save-correction').disabled = value;
  };
  $('answer-file').onchange = async () => {
    const selected = $('answer-file').files[0];
    reset(true);
    if (!selected) return;
    if (!['image/png', 'image/jpeg', 'application/pdf'].includes(selected.type) || !selected.size || selected.size > 10 * 1024 * 1024) {
      error('Escolha um PNG, JPEG ou PDF válido de até 10 MB.');
      return;
    }
    const ticket = generation;
    const bytes = new Uint8Array(await selected.slice(0, 8).arrayBuffer());
    if (disposed || ticket !== generation) return;
    const valid = selected.type === 'application/pdf' ? String.fromCharCode(...bytes.slice(0, 5)) === '%PDF-' : selected.type === 'image/png' ? [137, 80, 78, 71, 13, 10, 26, 10].every((n, i) => bytes[i] === n) : bytes[0] === 255 && bytes[1] === 216 && bytes[2] === 255;
    if (!valid) {
      error('O conteúdo do arquivo não corresponde ao formato informado.');
      return;
    }
    file = selected;
    url = URL.createObjectURL(file);
    $('file-preview').innerHTML = `<p><strong>${esc(file.name)}</strong> · ${(file.size/1024).toFixed(1)} KB · pronto para simular</p>` + (file.type.startsWith('image/') ? `<img src="${url}" alt="Prévia da folha enviada">` : '<p class="muted">PDF selecionado. A simulação não extrai dados do documento.</p>');
    $('simulate-reading').disabled = false;
  };
  const review = answers => {
    $('read-answers').innerHTML = version().questions.map((q, i) => `<label>Questão ${i+1}<select name="answer" required aria-label="Resposta da questão ${i+1}"><option value="">Selecione</option>${letters.map(a=>`<option ${answers[i]===a?'selected':''}>${a}</option>`).join('')}</select></label>`).join('');
    $('answer-review').hidden = false;
    $('review-confirmation').checked = false;
    $('read-answers').onchange = () => {
      $('review-confirmation').checked = false;
    };
    $('answer-review').scrollIntoView({
      block: 'nearest',
      behavior: 'smooth'
    });
  };
  $('manual-reading').onclick = () => {
    generation++;
    error('');
    $('reading-status').textContent = 'Entrada manual: informe todas as respostas.';
    $('reading-progress').hidden = true;
    review([]);
  };
  $('simulate-reading').onclick = async () => {
    if (!file || busy) return;
    error('');
    $('answer-review').hidden = true;
    lock(true);
    const ticket = ++generation;
    const phases = ['Arquivo recebido · simulação iniciada', 'Identificação da versão · usando sua seleção', 'Marcações fictícias geradas · revise abaixo'];
    $('reading-progress').hidden = false;
    $('reading-progress').value = 0;
    for (let i = 0; i < phases.length; i++) {
      await new Promise(resolve => setTimeout(resolve, 450));
      if (disposed || ticket !== generation) return;
      $('reading-status').textContent = phases[i];
      $('reading-progress').value = i + 1;
    }
    // Independent of the answer key: these are deliberately fictitious choices.
    const random = crypto.getRandomValues(new Uint8Array(version().questions.length));
    review([...random].map(n => letters[n % 4]));
    lock(false);
  };
  form.onsubmit = async event => {
    event.preventDefault();
    if (busy || $('answer-review').hidden || !$('review-confirmation').checked) return;
    const fields = new FormData(form);
    lock(true);
    error('');
    try {
      const result = await api('/results', {
        method: 'POST',
        body: {
          evaluationId: fields.get('evaluationId'),
          studentId: fields.get('studentId'),
          version: fields.get('version'),
          answers: fields.getAll('answer')
        }
      });
      await refresh();
      if (!disposed) {
        notice('Correção salva. Nota: ' + result.grade.toFixed(1));
        location.hash = 'results?evaluation=' + encodeURIComponent(result.evaluationId);
      }
    } catch (err) {
      if (!disposed) error(err.message);
    } finally {
      if (!disposed) lock(false);
    }
  };
  return () => {
    disposed = true;
    generation++;
    if (url) URL.revokeObjectURL(url);
  };
}

export function renderResults(root, state) {
  let disposed = false,
    requestId = 0;
  root.innerHTML = title('Resultados e estatísticas', 'Acompanhe as notas e identifique as questões que merecem revisão.') +
    (!state.evaluations.length ? '<section class="panel empty"><h2>Nenhuma avaliação criada</h2><a href="#create" class="btn">Criar avaliação</a></section>' : `<section class="panel result-filters"><div class="grid-two">${choose('Avaliação','resultEvaluation',state.evaluations)}<div id="result-student-filter"></div></div><p id="result-class" class="muted"></p></section><div id="result-content"></div>`);
  if (!state.evaluations.length) return () => {};
  const selector = root.querySelector('[name=resultEvaluation]'),
    content = root.querySelector('#result-content');
  const initial = new URLSearchParams(location.hash.split('?')[1] || '').get('evaluation');
  if (state.evaluations.some(e => e.id === initial)) selector.value = initial;
  const draw = async () => {
    const ticket = ++requestId,
      evaluation = state.evaluations.find(e => e.id === selector.value),
      student = root.querySelector('[name=resultStudent]').value;
    const rows = state.results.filter(r => r.evaluationId === evaluation.id && (!student || r.studentId === student));
    content.innerHTML = '<section class="panel" role="status">Carregando estatísticas…</section>';
    try {
      const stats = await api('/evaluations/' + encodeURIComponent(evaluation.id) + '/estatisticas' + (student ? '?student_id=' + encodeURIComponent(student) : ''));
      if (disposed || ticket !== requestId) return;
      content.innerHTML = `<p class="result-scope"><strong>${esc(evaluation.name)}</strong> · ${esc(find(state.classes,evaluation.classId))} · ${student?esc(find(state.students,student)):"Todos os alunos"}</p><div class="metrics result-metrics"><div class="metric"><small>Média · 0 a 10</small><strong>${stats.average===null?'—':stats.average.toFixed(1)}</strong></div><div class="metric"><small>Provas corrigidas</small><strong>${stats.count}</strong></div><div class="metric"><small>Acertos registrados</small><strong>${rows.reduce((n,r)=>n+r.correct,0)}</strong></div></div>` +
        (!rows.length ? '<section class="panel empty"><h2>Ainda não há resultados neste filtro</h2><p>Corrija uma prova para acompanhar o desempenho.</p><a class="btn" href="#correction">Corrigir prova</a></section>' : `<section class="panel"><div class="section-heading"><h2>Notas por aluno</h2><div class="actions"><button id="export-filtered" class="secondary">Exportar CSV</button><button id="print-results" class="secondary">Imprimir relatório</button></div></div><div class="table-wrap"><table><thead><tr><th>Aluno</th><th>Versão</th><th>Acertos</th><th>Nota</th><th>Respostas</th></tr></thead><tbody>${rows.map(r=>`<tr><td>${esc(find(state.students,r.studentId))}</td><td>${esc(r.version)}</td><td>${r.correct}/${r.total}</td><td><span class="badge">${r.grade.toFixed(1)}</span></td><td><button class="secondary result-detail" data-result="${esc(r.id)}">Conferir</button></td></tr>`).join('')}</tbody></table></div><div id="result-detail" tabindex="-1"></div></section>
        <section class="panel"><h2>Desempenho por questão</h2><p class="muted">${stats.count} prova(s) neste filtro. As alternativas A–D abaixo usam a ordem original do cadastro, reunindo todas as versões embaralhadas.</p><div class="statistics-list">${stats.questions.map((q,i)=>`<article class="stat-question"><h3>${i+1}. ${esc(q.statement)}</h3><p><strong>${q.hitRate}% de acertos</strong> · ${q.correct}/${q.total} respostas</p><meter min="0" max="100" value="${q.hitRate}" aria-label="Percentual de acertos da questão ${i+1}"></meter><div class="alternative-counts">${q.alternatives.map(a=>`<div><span>${letters[a.index]} · ${esc(a.text)} ${q.mostSelected.includes(a.index)?'<small class="badge">Mais marcada'+(q.mostSelected.length>1?' · empate':'')+'</small>':''}</span><strong>${a.count}</strong></div>`).join('')}</div></article>`).join('')}</div></section>`);
      if (!rows.length) return;
      content.querySelector('#print-results').onclick = () => window.print();
      content.querySelector('#export-filtered').onclick = () => exportCsv(rows, state);
      content.querySelectorAll('.result-detail').forEach(button => button.onclick = () => {
        const result = rows.find(r => r.id === button.dataset.result),
          version = evaluation.versions.find(v => v.name === result.version),
          detail = content.querySelector('#result-detail');
        detail.innerHTML = `<h3>${esc(find(state.students,result.studentId))} · Versão ${esc(result.version)}</h3><p>Nota ${result.grade.toFixed(1)} · ${new Date(result.createdAt).toLocaleString('pt-BR')}</p><ol class="result-answers">${version.questions.map((q,i)=>`<li><p>${esc(q.statement)}</p><span class="badge ${q.answerLetter===result.answers[i]?'':'answer-incorrect'}">${q.answerLetter===result.answers[i]?'Acertou':'Errou'}</span><p>Resposta: ${result.answers[i]} · ${esc(q.options[letters.indexOf(result.answers[i])])}<br>Gabarito: ${q.answerLetter} · ${esc(q.correctAnswer)}</p></li>`).join('')}</ol>`;
        detail.focus();
        detail.scrollIntoView({
          block: 'start',
          behavior: 'smooth'
        });
      });
    } catch (err) {
      if (!disposed && ticket === requestId) {
        content.innerHTML = '<section class="panel"><p role="alert"></p><button id="retry-results">Tentar novamente</button></section>';
        content.querySelector('[role=alert]').textContent = err.message;
        content.querySelector('button').onclick = draw;
      }
    }
  };
  const filters = () => {
    const evaluation = state.evaluations.find(e => e.id === selector.value);
    root.querySelector('#result-class').textContent = 'Turma: ' + find(state.classes, evaluation.classId);
    root.querySelector('#result-student-filter').innerHTML = choose('Aluno', 'resultStudent', [{
      id: '',
      name: 'Todos os alunos'
    }, ...state.students.filter(s => s.classId === evaluation.classId)]);
    root.querySelector('[name=resultStudent]').onchange = draw;
    draw();
  };
  selector.onchange = filters;
  filters();
  return () => {
    disposed = true;
    requestId++;
  };
}

function exportCsv(rows, state) {
  const cell = value => '"' + String(value ?? '').replace(/^[=+@-]/, "'").replace(/"/g, '""') + '"';
  const records = [
    ['Aluno', 'Avaliação', 'Versão', 'Acertos', 'Total', 'Nota'], ...rows.map(r => [find(state.students, r.studentId), find(state.evaluations, r.evaluationId), r.version, r.correct, r.total, r.grade])
  ];
  const url = URL.createObjectURL(new Blob(['\uFEFF' + records.map(row => row.map(cell).join(';')).join('\r\n')], {
    type: 'text/csv;charset=utf-8'
  }));
  const link = document.createElement('a');
  link.href = url;
  link.download = 'resultados-filtrados.csv';
  link.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
