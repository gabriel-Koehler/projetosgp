import {
  api
} from './api.js';
const $ = id => document.getElementById(id);
const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({
  '&': '&amp;',
  '<': '&lt;',
  '>': '&gt;',
  '"': '&quot;',
  "'": '&#39;'
} [c]));
let state, user, step = 1,
  draft = {},
  selectedSemester = 's1';
const screen = $('screen'),
  notice = message => {
    $('notice').hidden = false;
    $('notice').textContent = message;
  };
const head = (title, sub, actions = '') => '<header class="section-heading"><div><h1>' + title + '</h1><p>' + sub + '</p></div><div class="actions">' + actions + '</div></header>';
const button = (label, action, cls = '') => '<button type="button" class="' + cls + '" data-action="' + action + '">' + label + '</button>';
const empty = (title, detail) => '<div class="panel empty"><h2>' + title + '</h2><p>' + detail + '</p></div>';
const options = (items, selected = '') => items.map(x => '<option value="' + esc(x.id) + '" ' + (x.id === selected ? 'selected' : '') + '>' + esc(x.name) + '</option>').join('');
const input = (label, name, type = 'text', value = '') => '<label>' + label + '<input name="' + name + '" type="' + type + '" value="' + esc(value) + '" required maxlength="200"></label>';
const select = (label, name, items, chosen) => '<label>' + label + '<select name="' + name + '">' + options(items, chosen) + '</select></label>';
const findName = (list, id) => esc(list.find(x => x.id === id)?.name || '—');
async function refresh() {
  state = await api('/workspace');
}

function page() {
  return location.hash.slice(1) || 'dashboard';
}

function render() {
  const current = page();
  document.querySelectorAll('nav a').forEach(a => {
    const active = a.hash === '#' + current;
    a.classList.toggle('active', active);
    if (active) a.setAttribute('aria-current', 'page');
    else a.removeAttribute('aria-current');
  });
  $('sidebar').classList.remove('open');
  $('menu-toggle').setAttribute('aria-expanded', 'false');
  const pages = {
    dashboard,
    classes,
    questions,
    create,
    versions,
    correction,
    results
  };
  (pages[current] || dashboard)();
  document.title = (document.querySelector('#screen h1')?.textContent || 'Painel') + ' · AvaliaSystem';
}

function dashboard() {
  const average = state.results.length ? (state.results.reduce((n, r) => n + r.grade, 0) / state.results.length).toFixed(1) : '—';
  screen.innerHTML = head('Olá, ' + esc(user.name), 'Seu espaço para organizar avaliações e acompanhar seus alunos') +
    '<div class="quick-actions"><a href="#correction"><span><strong>▦ Corrigir prova</strong><small>Registrar respostas e calcular a nota</small></span>→</a><a href="#create"><span><strong>▧ Nova avaliação</strong><small>Criar prova com o banco de questões</small></span>→</a><a href="#results"><span><strong>▥ Ver resultados</strong><small>Notas e desempenho da turma</small></span>→</a></div>' +
    '<div class="metrics">' + [
      ['Questões no banco', state.questions.length],
      ['Provas corrigidas', state.results.length],
      ['Avaliações criadas', state.evaluations.length],
      ['Alunos ativos', state.students.length]
    ].map(([label, n]) => '<div class="metric"><small>' + label + '</small><strong>' + n + '</strong></div>').join('') + '</div>' +
    '<section class="panel"><div class="section-heading"><div><h2>Visão geral</h2><p>Acompanhe o progresso das suas avaliações</p></div><span class="badge">Média geral: ' + average + '</span></div>' + (state.evaluations.length ? '<div class="table-wrap"><table><thead><tr><th>Avaliação</th><th>Turma</th><th>Versões</th><th></th></tr></thead><tbody>' + state.evaluations.map(e => '<tr><td>' + esc(e.name) + '</td><td>' + findName(state.classes, e.classId) + '</td><td>' + e.versions.length + '</td><td><a href="#versions">Ver versões →</a></td></tr>').join('') + '</tbody></table></div>' : '<div class="empty"><h3>Sua primeira avaliação começa aqui</h3><p>As questões de exemplo já estão disponíveis. Crie uma avaliação para gerar versões.</p><a class="btn" href="#create">Criar avaliação</a></div>') + '</section>';
}

function classes() {
  const filtered = state.classes.filter(c => c.semesterId === selectedSemester);
  screen.innerHTML = head('Semestres & Turmas', 'Gerencie semestres, turmas e alunos', button('+ Novo semestre', 'semester', 'secondary') + button('+ Nova turma', 'class')) +
    '<div class="toolbar"><label>Semestre<select id="semester-filter">' + options(state.semesters, selectedSemester) + '</select></label></div><div class="grid-two">' + filtered.map(c => '<section class="panel"><div class="section-heading"><div><h2>' + esc(c.name) + '</h2><span class="badge">' + esc(c.code) + '</span></div>' + button('+ Aluno', 'student:' + c.id, 'secondary') + '</div><div class="table-wrap"><table><thead><tr><th>Aluno</th><th>Matrícula</th></tr></thead><tbody>' + state.students.filter(a => a.classId === c.id).map(a => '<tr><td>' + esc(a.name) + '</td><td>' + esc(a.registration) + '</td></tr>').join('') + '</tbody></table></div>' + (state.students.some(a => a.classId === c.id) ? '' : '<p class="empty">Nenhum aluno cadastrado.</p>') + '</section>').join('') + '</div>' + (filtered.length ? '' : empty('Nenhuma turma neste semestre', 'Crie uma turma para começar.'));
  $('semester-filter').onchange = e => {
    selectedSemester = e.target.value;
    classes();
  };
}

function questions() {
  screen.innerHTML = head('Banco de Questões', state.questions.length + ' questões cadastradas', button('+ Nova questão', 'question')) + '<div class="toolbar"><label>Buscar questão<input id="search-question" type="search" placeholder="Buscar por enunciado ou disciplina"></label></div><div id="question-list"></div>';
  const list = () => {
    const term = $('search-question').value.toLocaleLowerCase('pt-BR');
    const matches = state.questions.filter(q => (q.statement + ' ' + q.subject).toLocaleLowerCase('pt-BR').includes(term));
    $('question-list').innerHTML = matches.map(q => '<article class="question-card"><div class="question-meta"><span>' + esc(q.subject) + ' · ' + esc(q.id.slice(0, 8)) + '</span><span class="badge">' + esc(q.difficulty) + '</span></div><h3>' + esc(q.statement) + '</h3><div class="question-options">' + q.options.map((o, i) => '<div class="' + (q.answer === String.fromCharCode(65 + i) ? 'correct' : '') + '">' + String.fromCharCode(65 + i) + ' &nbsp; ' + esc(o) + '</div>').join('') + '</div><div class="question-footer"><small>Gabarito: <span class="badge">' + q.answer + '</span></small>' + button('Excluir', 'delete-question:' + q.id, 'danger') + '</div></article>').join('') || empty('Nenhuma questão encontrada', 'Cadastre uma questão ou ajuste a busca.');
  };
  $('search-question').oninput = list;
  list();
}

function create() {
  screen.innerHTML = head('Nova avaliação', 'Crie e configure uma avaliação em 4 etapas') + '<div class="steps">' + ['Configurar', 'Questões', 'Gabarito', 'Versões'].map((name, i) => '<span class="' + (step === i + 1 ? 'active' : '') + '">' + (i + 1) + ' · ' + name + '</span>').join('') + '</div><form id="evaluation-form" class="panel"><div id="step-body"></div><p id="wizard-error" role="alert" hidden></p><div class="actions">' + (step > 1 ? button('← Voltar', 'previous', 'secondary') : '') + '<a class="btn secondary" href="#dashboard">Cancelar</a><button type="submit">' + (step === 4 ? 'Gerar avaliação' : 'Próxima →') + '</button></div></form>';
  const body = $('step-body');
  if (step === 1) body.innerHTML = '<div class="grid-two">' + input('Nome da avaliação', 'name', 'text', draft.name || '') + select('Turma', 'classId', state.classes, draft.classId) + '</div>';
  if (step === 2) body.innerHTML = '<h2>Selecione as questões</h2>' + state.questions.map(q => '<label class="check-row"><input type="checkbox" name="questionIds" value="' + q.id + '" ' + (draft.questionIds?.includes(q.id) ? 'checked' : '') + '><span>' + esc(q.statement) + '<small> · ' + esc(q.subject) + '</small></span></label>').join('') + (state.questions.length ? '' : '<p>Cadastre questões no banco antes de continuar.</p>');
  if (step === 3) body.innerHTML = '<h2>Confira o gabarito</h2>' + draft.questionIds.map(id => {
    const q = state.questions.find(q => q.id === id);
    return '<p>' + esc(q.statement) + '<br><span class="badge">' + q.answer + ' · ' + esc(q.options[q.answer.charCodeAt(0) - 65]) + '</span></p>';
  }).join('');
  if (step === 4) body.innerHTML = '<h2>Versões e embaralhamento</h2><label>Quantidade de versões<select name="versionCount">' + [1, 2, 3, 4, 5].map(n => '<option ' + (n === (draft.versionCount || 3) ? 'selected' : '') + '>' + n + '</option>').join('') + '</select></label><br><label class="check-row"><input type="checkbox" name="shuffleQuestions" ' + (draft.shuffleQuestions !== false ? 'checked' : '') + '>Embaralhar questões</label><label class="check-row"><input type="checkbox" name="shuffleAlternatives" ' + (draft.shuffleAlternatives !== false ? 'checked' : '') + '>Embaralhar alternativas e ajustar o gabarito</label><p class="muted">' + esc(draft.name) + ' · ' + draft.questionIds.length + ' questões · ' + findName(state.classes, draft.classId) + '</p>';
  $('evaluation-form').onsubmit = async e => {
    e.preventDefault();
    const f = new FormData(e.target);
    if (step === 1) {
      draft.name = f.get('name');
      draft.classId = f.get('classId');
      if (!draft.classId) return notice('Cadastre uma turma antes de continuar.');
    }
    if (step === 2) {
      draft.questionIds = f.getAll('questionIds');
      if (!draft.questionIds.length) return notice('Selecione pelo menos uma questão.');
    }
    if (step < 4) {
      step++;
      create();
      return;
    }
    draft.versionCount = Number(f.get('versionCount'));
    draft.shuffleQuestions = f.has('shuffleQuestions');
    draft.shuffleAlternatives = f.has('shuffleAlternatives');
    const submit = e.submitter;
    submit.disabled = true;
    try {
      await api('/evaluations', {
        method: 'POST',
        body: draft
      });
      await refresh();
      draft = {};
      step = 1;
      location.hash = 'versions';
      notice('Avaliação gerada com sucesso.');
    } catch (err) {
      $('wizard-error').hidden = false;
      $('wizard-error').textContent = err.message;
    } finally {
      submit.disabled = false;
    }
  };
}

function versions() {
  screen.innerHTML = head('Versões & QR Code', 'Consulte questões, gabaritos e QR Codes', '<a class="btn" href="#create">+ Nova avaliação</a>') +
    (state.evaluations.length ? state.evaluations.map(e => '<section class="panel"><div class="section-heading"><div><h2>' + esc(e.name) + '</h2><p>' + findName(state.classes, e.classId) + '</p></div><a href="#correction">Iniciar correção →</a></div><div class="version-grid">' + e.versions.map(v => '<article class="panel"><h3>Versão ' + esc(v.name) + '</h3><p class="muted">' + v.questions.length + ' questões</p><ol>' + v.questions.map(q => '<li>' + esc(q.statement) + '<p><span class="badge">' + q.answerLetter + ' · ' + esc(q.correctAnswer) + '</span></p></li>').join('') + '</ol>' + button('Ver QR Code', 'qr:' + e.id + ':' + v.name, 'secondary') + '</article>').join('') + '</div></section>').join('') : empty('Nenhuma versão gerada', 'Crie uma avaliação para consultar os gabaritos e QR Codes.'));
}

function correction() {
  screen.innerHTML = head('Correção Automática', 'Simulação: informe as alternativas lidas para calcular a nota') +
    (state.evaluations.length ? '<form id="correction-form" class="panel"><p class="muted">A leitura óptica por câmera será integrada à API real. Neste MVP, as respostas são informadas manualmente.</p>' + select('Avaliação', 'evaluationId', state.evaluations) + '<div id="correction-details"></div><button type="submit">Corrigir e salvar resultado</button><p id="correction-error" role="alert" hidden></p></form>' : empty('Crie uma avaliação primeiro', 'A correção precisa de uma versão e de um aluno da turma.'));
  if (!state.evaluations.length) return;
  const form = $('correction-form');
  const details = () => {
    const evaluation = state.evaluations.find(e => e.id === form.elements.evaluationId.value);
    $('correction-details').innerHTML = '<div class="grid-two">' + select('Aluno', 'studentId', state.students.filter(a => a.classId === evaluation.classId)) + select('Versão', 'version', evaluation.versions.map(v => ({
      id: v.name,
      name: 'Versão ' + v.name
    }))) + '</div><br><div id="answers"></div>';
    const answers = () => {
      const version = evaluation.versions.find(v => v.name === form.elements.version.value);
      $('answers').innerHTML = version.questions.map((q, i) => '<label>Resposta da questão ' + (i + 1) + '<select name="answer" required><option value="">Selecione</option>' + ['A', 'B', 'C', 'D'].map(a => '<option>' + a + '</option>').join('') + '</select></label><br>').join('');
    };
    form.elements.version.onchange = answers;
    answers();
  };
  form.elements.evaluationId.onchange = details;
  details();
  form.onsubmit = async e => {
    e.preventDefault();
    const f = new FormData(form);
    e.submitter.disabled = true;
    try {
      const result = await api('/results', {
        method: 'POST',
        body: {
          evaluationId: f.get('evaluationId'),
          studentId: f.get('studentId'),
          version: f.get('version'),
          answers: f.getAll('answer')
        }
      });
      await refresh();
      location.hash = 'results';
      notice('Correção salva. Nota: ' + result.grade.toFixed(1));
    } catch (err) {
      $('correction-error').hidden = false;
      $('correction-error').textContent = err.message;
    } finally {
      e.submitter.disabled = false;
    }
  };
}

function results() {
  const rows = state.results,
    avg = rows.length ? (rows.reduce((n, r) => n + r.grade, 0) / rows.length).toFixed(1) : '—';
  screen.innerHTML = head('Resultados', 'Notas e desempenho das avaliações', rows.length ? button('Exportar CSV', 'export', 'secondary') + button('Imprimir relatório', 'print', 'secondary') : '') +
    '<div class="metrics">' + [
      ['Média geral', avg],
      ['Provas corrigidas', rows.length],
      ['Aprovados', rows.filter(r => r.grade >= 6).length],
      ['Reprovados', rows.filter(r => r.grade < 6).length]
    ].map(([label, n]) => '<div class="metric"><small>' + label + '</small><strong>' + n + '</strong></div>').join('') + '</div>' +
    (rows.length ? '<section class="panel"><h2>Notas por aluno</h2><div class="chart">' + rows.map(r => '<div class="chart-column"><small>' + r.grade.toFixed(1) + '</small><div class="chart-bar" style="height:' + r.grade * 12 + 'px"></div><small>' + findName(state.students, r.studentId).split(' ')[0] + '</small></div>').join('') + '</div></section><section class="panel table-wrap"><table><thead><tr><th>Aluno</th><th>Avaliação</th><th>Versão</th><th>Acertos</th><th>Nota</th></tr></thead><tbody>' + rows.map(r => '<tr><td>' + findName(state.students, r.studentId) + '</td><td>' + findName(state.evaluations, r.evaluationId) + '</td><td>' + esc(r.version) + '</td><td>' + r.correct + '/' + r.total + '</td><td><span class="badge">' + r.grade.toFixed(1) + '</span></td></tr>').join('') + '</tbody></table></section>' : empty('Ainda não há resultados', 'Corrija uma avaliação para acompanhar o desempenho dos alunos.'));
}

function modal(title, fields, onSave) {
  $('modal-title').textContent = title;
  $('modal-fields').innerHTML = fields;
  $('modal-error').hidden = true;
  $('modal-form').querySelector('[type=submit]').hidden = false;
  $('modal-form').onsubmit = async e => {
    e.preventDefault();
    e.submitter.disabled = true;
    try {
      await onSave(new FormData(e.target));
      await refresh();
      $('modal').close();
      render();
      notice('Dados salvos com sucesso.');
    } catch (err) {
      $('modal-error').textContent = err.message;
      $('modal-error').hidden = false;
    } finally {
      e.submitter.disabled = false;
    }
  };
  $('modal').showModal();
}
$('close-modal').onclick = () => $('modal').close();
document.addEventListener('click', async event => {
  const target = event.target.closest('[data-action]');
  if (!target) return;
  const [action, id, version] = target.dataset.action.split(':');
  try {
    if (action === 'previous') {
      step = Math.max(1, step - 1);
      create();
    }
    if (action === 'semester') modal('Novo semestre', input('Nome do semestre', 'name'), f => api('/semesters', {
      method: 'POST',
      body: Object.fromEntries(f)
    }));
    if (action === 'class') modal('Nova turma', input('Nome da turma', 'name') + input('Código', 'code') + select('Semestre', 'semesterId', state.semesters, selectedSemester), f => api('/classes', {
      method: 'POST',
      body: Object.fromEntries(f)
    }));
    if (action === 'student') modal('Novo aluno', input('Nome completo', 'name') + input('Matrícula', 'registration'), f => api('/students', {
      method: 'POST',
      body: {
        ...Object.fromEntries(f),
        classId: id
      }
    }));
    if (action === 'question') modal('Nova questão', '<label>Enunciado<textarea name="statement" required maxlength="2000"></textarea></label>' + input('Disciplina', 'subject') + select('Dificuldade', 'difficulty', ['Fácil', 'Médio', 'Difícil'].map(n => ({
      id: n,
      name: n
    }))) + '<div class="option-grid">' + ['A', 'B', 'C', 'D'].map(a => input('Alternativa ' + a, 'option' + a)).join('') + '</div>' + select('Gabarito', 'answer', ['A', 'B', 'C', 'D'].map(n => ({
      id: n,
      name: n
    }))), f => api('/questions', {
      method: 'POST',
      body: {
        statement: f.get('statement'),
        subject: f.get('subject'),
        difficulty: f.get('difficulty'),
        answer: f.get('answer'),
        options: ['A', 'B', 'C', 'D'].map(a => f.get('option' + a))
      }
    }));
    if (action === 'delete-question' && confirm('Excluir esta questão do banco? As versões já geradas serão preservadas.')) {
      await api('/questions/' + id, {
        method: 'DELETE'
      });
      await refresh();
      questions();
      notice('Questão excluída.');
    }
    if (action === 'qr') {
      const qr = await api('/evaluations/' + id + '/qr/' + version);
      modal('QR Code · Versão ' + version, '<img class="qr-code" src="' + qr.image + '" alt="QR Code da versão"><p class="muted">Identifica a avaliação e a versão.</p><a class="btn" download="qr-' + version + '.png" href="' + qr.image + '">Baixar PNG</a>', async () => {});
      $('modal-form').querySelector('[type=submit]').hidden = true;
    }
    if (action === 'print') window.print();
    if (action === 'export') {
      const cell = v => '"' + String(v).replace(/^[=+@-]/, "'").replace(/"/g, '""') + '"';
      const rows = [
        ['Aluno', 'Avaliação', 'Versão', 'Acertos', 'Nota'], ...state.results.map(r => [state.students.find(a => a.id === r.studentId)?.name, state.evaluations.find(e => e.id === r.evaluationId)?.name, r.version, r.correct, r.grade])
      ];
      const url = URL.createObjectURL(new Blob(['\uFEFF' + rows.map(r => r.map(cell).join(';')).join('\r\n')], {
        type: 'text/csv;charset=utf-8'
      }));
      const a = document.createElement('a');
      a.href = url;
      a.download = 'resultados.csv';
      a.click();
      setTimeout(() => URL.revokeObjectURL(url), 1000);
    }
  } catch (err) {
    notice(err.message);
  }
});
$('logout').onclick = async () => {
  try {
    await api('/auth/logout', {
      method: 'POST'
    });
    location.assign('/');
  } catch (e) {
    notice(e.message);
  }
};
$('menu-toggle').onclick = () => {
  $('sidebar').classList.toggle('open');
  $('menu-toggle').setAttribute('aria-expanded', String($('sidebar').classList.contains('open')));
};
window.addEventListener('hashchange', () => {
  if (state) render();
});
try {
  user = await api('/auth/me');
  $('professor-name').textContent = user.name;
  await refresh();
  render();
} catch (e) {
  screen.innerHTML = '<div class="panel"><h1>Não foi possível carregar</h1><p id="load-error"></p><button onclick="location.reload()">Tentar novamente</button> <a href="/">Voltar ao login</a></div>';
  $('load-error').textContent = e.message;
}
