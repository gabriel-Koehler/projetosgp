import { parseQuestionsCsv } from './question-csv.js';
import { parseStudentsCsv } from './student-csv.js';
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
  const collections = ['semesters', 'classes', 'students', 'questions', 'evaluations', 'results'];
  const values = await Promise.all(collections.map(name => api('/' + name)));
  state = Object.fromEntries(collections.map((name, index) => [name, values[index]]));
}

function page() {
  return location.hash.slice(1).split('?')[0] || 'dashboard';
}

function render() {
  const current = page();
  document.querySelectorAll('nav a').forEach(a => {
    const active = a.hash === '#' + (current === 'class' ? 'classes' : current === 'evaluation' ? 'versions' : current);
    a.classList.toggle('active', active);
    if (active) a.setAttribute('aria-current', 'page');
    else a.removeAttribute('aria-current');
  });
  $('sidebar').classList.remove('open');
  $('menu-toggle').setAttribute('aria-expanded', 'false');
  const pages = {
    dashboard,
    classes,
    class: classDetails,
    questions,
    create,
    versions,
    evaluation: evaluationConfirmation,
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


function routeParams() { return new URLSearchParams(location.hash.split('?')[1] || ''); }
function classes() {
  selectedSemester = routeParams().get('semester') || selectedSemester;
  if (!state.semesters.some(s => s.id === selectedSemester)) selectedSemester = state.semesters[0]?.id;
  const semester = state.semesters.find(s => s.id === selectedSemester);
  const filtered = state.classes.filter(c => c.semesterId === selectedSemester);
  screen.innerHTML = head('Semestres & Turmas', 'Organize seus períodos letivos e acompanhe as turmas', button('+ Novo semestre', 'semester', 'secondary') + (semester ? button('+ Nova turma', 'class') : '')) +
    '<div class="semester-layout"><aside class="panel semester-list" aria-label="Semestres"><h2>Semestres</h2>' + state.semesters.map(s => {
      const rooms = state.classes.filter(c => c.semesterId === s.id);
      const students = state.students.filter(a => rooms.some(c => c.id === a.classId)).length;
      return '<a class="semester-card ' + (s.id === selectedSemester ? 'selected' : '') + '" href="#classes?semester=' + encodeURIComponent(s.id) + '" ' + (s.id === selectedSemester ? 'aria-current="true"' : '') + '><strong>' + esc(s.name) + '</strong><span class="badge">' + (s.active ? 'Ativo' : 'Inativo') + '</span><small>' + rooms.length + ' turmas · ' + students + ' alunos</small></a>';
    }).join('') + (state.semesters.length ? '' : '<p>Nenhum semestre cadastrado.</p>') + '</aside><section aria-label="Turmas do semestre"><div class="section-heading"><div><h2>Turmas — ' + esc(semester?.name || 'Selecione um semestre') + '</h2><p>' + filtered.length + ' turmas neste semestre</p></div></div><div class="class-grid">' +
    filtered.map(c => {
      const students = state.students.filter(a => a.classId === c.id).length;
      const exams = state.evaluations.filter(e => e.classId === c.id).length;
      return '<article class="panel class-card"><span class="badge">' + esc(c.code) + '</span><h3>' + esc(c.name) + '</h3><div class="class-counts"><span><strong>' + students + '</strong> alunos</span><span><strong>' + exams + '</strong> avaliações</span></div><a class="btn secondary" href="#class?id=' + encodeURIComponent(c.id) + '">Ver turma e alunos →</a></article>';
    }).join('') + '</div>' + (filtered.length ? '' : empty('Nenhuma turma neste semestre', 'Use Nova turma para cadastrar a primeira turma vinculada a este semestre.')) + '</section></div>';
}
function classDetails() {
  const room = state.classes.find(c => c.id === routeParams().get('id'));
  if (!room) {
    screen.innerHTML = head('Turma não encontrada', 'A turma pode não estar disponível nesta conta.') + '<a class="btn" href="#classes">Voltar aos semestres</a>';
    return;
  }
  selectedSemester = room.semesterId;
  const students = state.students.filter(a => a.classId === room.id);
  screen.innerHTML = '<a class="breadcrumb" href="#classes?semester=' + encodeURIComponent(room.semesterId) + '">← Semestres & Turmas · ' + findName(state.semesters, room.semesterId) + '</a>' +
    head(esc(room.name), esc(room.code) + ' · ' + students.length + ' alunos', button('Importar alunos', 'import-students:' + room.id, 'secondary') + button('+ Adicionar aluno', 'student:' + room.id)) +

    '<section class="panel"><h2>Alunos da turma</h2><label>Buscar aluno<input id="student-search" type="search" placeholder="Nome ou matrícula"></label><p id="student-count" class="muted" role="status"></p><div id="student-list"></div></section>';
  const renderStudents = () => {
    const term = $('student-search').value.trim().toLocaleLowerCase('pt-BR');
    const found = students.filter(a => (a.name + ' ' + a.registration).toLocaleLowerCase('pt-BR').includes(term));
    $('student-count').textContent = found.length + ' de ' + students.length + ' alunos';
    $('student-list').innerHTML = found.length ? '<div class="table-wrap"><table><thead><tr><th>Nome</th><th>Matrícula</th></tr></thead><tbody>' + found.map(a => '<tr><td>' + esc(a.name) + '</td><td>' + esc(a.registration) + '</td></tr>').join('') + '</tbody></table></div>' : '<p class="empty">' + (students.length ? 'Nenhum aluno encontrado para essa busca.' : 'Nenhum aluno cadastrado. Adicione um aluno ou importe o modelo CSV.') + '</p>';
  };
  $('student-search').oninput = renderStudents;
  renderStudents();
}

function importStudents(classId) {
  const room = state.classes.find(c => c.id === classId);
  if (!room) return notice('Turma não encontrada.');
  const dialog = $('modal'), form = $('modal-form');
  $('modal-title').textContent = 'Importar alunos · ' + room.name;
  $('modal-error').hidden = true;
  $('modal-fields').innerHTML = '<p class="muted">Envie uma planilha salva como CSV UTF-8 (até 500 alunos e 1 MB). Confira a prévia antes de confirmar. Matrículas devem ser únicas em todo o banco.</p><a href="/modelo_alunos.csv" download="modelo_alunos.csv">↓ Baixar modelo_alunos.csv</a><label>Arquivo CSV<input id="students-file" type="file" accept=".csv,text/csv" required></label><p id="import-summary" role="status">Nenhum arquivo selecionado.</p><div id="import-preview" class="import-preview"></div>';
  const submit = form.querySelector('[type=submit]');
  submit.hidden = false; submit.disabled = true; submit.textContent = 'Importar alunos válidos';
  let rows = [], reading = 0;
  const preview = () => {
    const valid = rows.filter(r => !r.error);
    $('import-summary').textContent = valid.length + ' válidos · ' + (rows.length - valid.length) + ' inválidos. Somente as linhas válidas serão importadas.';
    $('import-preview').innerHTML = '<table><thead><tr><th>Linha</th><th>Nome</th><th>Matrícula</th><th>Validação</th></tr></thead><tbody>' + rows.map(r => '<tr class="' + (r.error ? 'invalid-row' : '') + '"><td>' + r.line + '</td><td>' + esc(r.name) + '</td><td>' + esc(r.registration) + '</td><td>' + (r.error ? esc(r.error) : '✓ Válido') + '</td></tr>').join('') + '</tbody></table>';
    submit.disabled = !valid.length;
    submit.textContent = 'Importar ' + valid.length + ' alunos válidos';
  };
  $('students-file').onchange = async event => {
    const current = ++reading;
    rows = []; submit.disabled = true; $('modal-error').hidden = true;
    $('import-preview').innerHTML = ''; $('import-summary').textContent = 'Lendo arquivo…';
    const file = event.target.files[0];
    if (!file) { $('import-summary').textContent = 'Nenhum arquivo selecionado.'; return; }
    try {
      if (!file.name.toLowerCase().endsWith('.csv') || file.size > 1024 * 1024) throw new Error('Selecione um arquivo .csv de até 1 MB.');
      const content = await file.text();
      if (current !== reading || !dialog.open) return;
      rows = parseStudentsCsv(content, state.students);
      preview();
    } catch (error) {
      if (current !== reading || !dialog.open) return;
      $('modal-error').textContent = error.message; $('modal-error').hidden = false;
      $('import-summary').textContent = 'Não foi possível validar o arquivo.';
    }
  };
  form.onsubmit = async event => {
    event.preventDefault();
    const valid = rows.filter(r => !r.error);
    if (!valid.length || submit.disabled) return;
    submit.disabled = true; submit.textContent = 'Importando…'; $('modal-error').hidden = true;
    $('students-file').disabled = true; $('close-modal').disabled = true;
    const preventClose = event => event.preventDefault();
    dialog.addEventListener('cancel', preventClose);
    try {
      const result = await api('/students/import', { method: 'POST', body: { classId, students: valid.map(({ name, registration }) => ({ name, registration })) } });
      state.students.push(...result);
      dialog.close(); render();
      notice(result.length + ' alunos importados para ' + room.name + '.');
    } catch (error) {
      $('modal-error').textContent = error.message; $('modal-error').hidden = false;
      submit.disabled = false;
    } finally {
      dialog.removeEventListener('cancel', preventClose);
      $('students-file').disabled = false; $('close-modal').disabled = false;
      submit.textContent = 'Importar alunos válidos';
    }
  };
  dialog.showModal();
}


let questionFilters = { text: '', subject: '', difficulty: '' };
function questions() {
  const subjects = [...new Set(state.questions.map(q => q.subject))].sort();
  if (!subjects.includes(questionFilters.subject)) questionFilters.subject = '';
  screen.innerHTML = head('Banco de Questões', state.questions.length + ' questões cadastradas', button('Importar questões', 'import-questions', 'secondary') + button('+ Nova questão', 'question')) +
    '<div class="toolbar question-filters"><label>Buscar questão<input id="search-question" type="search" placeholder="Enunciado ou disciplina" value="' + esc(questionFilters.text) + '"></label><label>Disciplina<select id="filter-subject"><option value="">Todas as disciplinas</option>' + subjects.map(subject => '<option ' + (subject === questionFilters.subject ? 'selected' : '') + '>' + esc(subject) + '</option>').join('') + '</select></label><label>Dificuldade<select id="filter-difficulty"><option value="">Todas as dificuldades</option>' + ['Fácil','Médio','Difícil'].map(d => '<option ' + (d === questionFilters.difficulty ? 'selected' : '') + '>' + d + '</option>').join('') + '</select></label></div><p id="question-count" class="muted" role="status"></p><div id="question-list"></div>';
  const list = () => {
    questionFilters = { text: $('search-question').value, subject: $('filter-subject').value, difficulty: $('filter-difficulty').value };
    const term = questionFilters.text.trim().toLocaleLowerCase('pt-BR');
    const matches = state.questions.filter(q => (q.statement + ' ' + q.subject).toLocaleLowerCase('pt-BR').includes(term) && (!questionFilters.subject || q.subject === questionFilters.subject) && (!questionFilters.difficulty || q.difficulty === questionFilters.difficulty));
    $('question-count').textContent = matches.length + ' questões encontradas';
    $('question-list').innerHTML = matches.map(q => '<article class="question-card"><div class="question-meta"><span>' + esc(q.subject) + ' · ' + esc(q.id.slice(0,8)) + '</span><span class="badge">' + esc(q.difficulty) + '</span></div><h3>' + esc(q.statement) + '</h3><details class="question-alternatives"><summary>Ver alternativas A–D</summary><div class="question-options">' + q.options.map((o,i) => '<div class="' + (q.answer === String.fromCharCode(65+i) ? 'correct' : '') + '">' + String.fromCharCode(65+i) + ' · ' + esc(o) + '</div>').join('') + '</div></details><div class="question-footer"><span>Gabarito: <strong class="badge">' + q.answer + '</strong></span><div class="actions">' + button('Editar', 'edit-question:' + q.id, 'secondary') + button('Excluir', 'delete-question:' + q.id, 'danger') + '</div></div></article>').join('') || empty('Nenhuma questão encontrada', 'Cadastre uma questão ou ajuste os filtros.');
  };
  $('search-question').oninput = list;
  $('filter-subject').onchange = list;
  $('filter-difficulty').onchange = list;
  list();
}

function editQuestion(id) {
  const question = id ? state.questions.find(q => q.id === id) : null;
  if (id && !question) return notice('Questão não encontrada.');
  const fields = '<label>Enunciado<textarea name="statement" required maxlength="2000"></textarea></label>' +
    input('Disciplina','subject') + select('Dificuldade','difficulty',['Fácil','Médio','Difícil'].map(name => ({id:name,name}))) +
    '<div class="option-grid">' + ['A','B','C','D'].map(a => '<label data-option="' + a + '">Alternativa ' + a + '<input name="option' + a + '" required maxlength="500"></label>').join('') + '</div>' +
    select('Resposta correta','answer',['A','B','C','D'].map(name => ({id:name,name}))) + '<p id="answer-highlight" class="badge" role="status"></p>';
  modal(id ? 'Editar questão' : 'Nova questão', fields, async form => {
    const body = { statement: form.get('statement'), subject: form.get('subject'), difficulty: form.get('difficulty'), options: ['A','B','C','D'].map(a => form.get('option'+a)), answer: form.get('answer') };
    await api('/questions' + (id ? '/' + id : ''), { method: id ? 'PUT' : 'POST', body });
  });
  const form = $('modal-form');
  if (question) {
    for (const key of ['statement','subject','difficulty','answer']) form.elements[key].value = question[key];
    question.options.forEach((option, i) => { form.elements['option'+String.fromCharCode(65+i)].value = option; });
  }
  const highlight = () => {
    const answer = form.elements.answer.value;
    $('answer-highlight').textContent = 'Gabarito: ' + answer;
    form.querySelectorAll('[data-option]').forEach(label => label.classList.toggle('answer-choice', label.dataset.option === answer));
  };
  form.elements.answer.onchange = highlight;
  highlight();
}

function importQuestions() {
  const dialog = $('modal'), form = $('modal-form');
  $('modal-title').textContent = 'Importar questões';
  $('modal-error').hidden = true;
  $('modal-fields').innerHTML = '<p class="muted">Envie CSV UTF-8 de até 1 MB e 500 questões. Confira enunciado, alternativas e gabarito antes de confirmar.</p><a href="/modelo_questoes.csv" download="modelo_questoes.csv">↓ Baixar modelo_questoes.csv</a><label>Arquivo CSV<input id="questions-file" type="file" accept=".csv,text/csv" required></label><p id="question-import-summary" role="status">Nenhum arquivo selecionado.</p><div id="question-import-preview" class="import-preview"></div>';
  const submit = form.querySelector('[type=submit]');
  submit.hidden = false; submit.disabled = true; submit.textContent = 'Importar questões válidas';
  let rows = [], reading = 0;
  $('questions-file').onchange = async event => {
    const ticket = ++reading;
    rows = []; submit.disabled = true; $('modal-error').hidden = true;
    $('question-import-preview').innerHTML = ''; $('question-import-summary').textContent = 'Validando arquivo…';
    const file = event.target.files[0];
    if (!file) { $('question-import-summary').textContent = 'Nenhum arquivo selecionado.'; return; }
    try {
      if (!file.name.toLowerCase().endsWith('.csv') || file.size > 1024*1024) throw new Error('Selecione um arquivo .csv de até 1 MB.');
      const content = await file.text();
      if (ticket !== reading || !dialog.open) return;
      rows = parseQuestionsCsv(content, state.questions);
      const valid = rows.filter(r => !r.error);
      $('question-import-summary').textContent = valid.length + ' válidas · ' + (rows.length-valid.length) + ' inválidas. Somente as válidas serão importadas.';
      $('question-import-preview').innerHTML = rows.map(r => '<article class="import-question ' + (r.error ? 'invalid-row' : '') + '"><small>Linha ' + r.line + ' · ' + esc(r.question.subject) + ' · ' + esc(r.question.difficulty) + '</small><p>' + esc(r.question.statement) + '</p><details><summary>Ver alternativas</summary>' + r.question.options.map((o,i) => '<p>' + String.fromCharCode(65+i) + ' · ' + esc(o) + '</p>').join('') + '</details><strong>Gabarito: ' + esc(r.question.answer || '—') + '</strong><p>' + esc(r.error || '✓ Válida') + '</p></article>').join('');
      submit.disabled = !valid.length; submit.textContent = 'Importar ' + valid.length + ' questões válidas';
    } catch(error) {
      if (ticket !== reading || !dialog.open) return;
      $('modal-error').textContent = error.message; $('modal-error').hidden = false;
      $('question-import-summary').textContent = 'Não foi possível validar o arquivo.';
    }
  };
  form.onsubmit = async event => {
    event.preventDefault();
    if (submit.disabled) return;
    const valid = rows.filter(r => !r.error);
    if (!valid.length) return;
    submit.disabled = true; submit.textContent = 'Importando…';
    $('questions-file').disabled = true; $('close-modal').disabled = true;
    const preventClose = event => event.preventDefault();
    dialog.addEventListener('cancel', preventClose);
    try {
      const imported = await api('/questions/import', { method:'POST', body: { questions: valid.map(r => r.question) } });
      state.questions.push(...imported);
      questionFilters = {text:'',subject:'',difficulty:''};
      dialog.close(); render(); notice(imported.length + ' questões importadas.');
    } catch(error) {
      $('modal-error').textContent = error.message; $('modal-error').hidden = false; submit.disabled = false;
    } finally {
      dialog.removeEventListener('cancel', preventClose);
      $('questions-file').disabled = false; $('close-modal').disabled = false;
      submit.textContent = 'Importar questões válidas';
    }
  };
  dialog.showModal();
}


function draftKey() { return 'avalia-draft:' + user.id; }
function persistDraft() {
  try { sessionStorage.setItem(draftKey(), JSON.stringify({ step, draft, questionEntry })); } catch {}
}
function captureWizard() {
  const form = $('evaluation-form');
  if (!form) return;
  const data = new FormData(form);
  if (step === 1) {
    draft.name = data.get('name') || '';
    draft.semesterId = data.get('semesterId') || '';
    draft.classId = data.get('classId') || '';
  } else if (step === 3) {
    draft.versionCount = Number(data.get('versionCount')) || 3;
    draft.versionNames = data.getAll('versionName');
    draft.shuffleQuestions = data.has('shuffleQuestions');
    draft.shuffleAlternatives = data.has('shuffleAlternatives');
  }
  persistDraft();
}
function clearDraft() {
  draft = {}; questionEntry = {}; step = 1;
  try { sessionStorage.removeItem(draftKey()); } catch {}
}
function create() {
  draft.questionIds = (draft.questionIds || []).filter(id => state.questions.some(q => q.id === id));
  if (step > 1 && !state.classes.some(c => c.id === draft.classId)) step = 1;
  if (step > 2 && !draft.questionIds.length) step = 2;
  screen.innerHTML = head('Nova avaliação', 'Crie sua avaliação em 3 etapas') +
    '<ol class="steps wizard-steps">' + ['Turma','Questões','Versões'].map((name,i) => '<li class="' + (step === i+1 ? 'active' : '') + '" ' + (step === i+1 ? 'aria-current="step"' : '') + '>' + (i+1) + ' · ' + name + '</li>').join('') +
    '</ol><form id="evaluation-form" class="panel"><div id="step-body"></div><p id="wizard-error" role="alert" hidden></p><div class="actions">' +
    (step > 1 ? button('← Voltar','previous','secondary') : '') + button('Cancelar','cancel-evaluation','secondary') + '<button type="submit">' + (step === 3 ? 'Gerar avaliação' : 'Próxima →') + '</button></div></form>';
  const body = $('step-body'), form = $('evaluation-form');
  if (step === 1) {
    draft.semesterId ||= state.classes.find(c => c.id === draft.classId)?.semesterId || selectedSemester || state.semesters[0]?.id;
    body.innerHTML = '<div class="grid-two">' + input('Nome da avaliação','name','text',draft.name || '') + select('Semestre','semesterId',state.semesters,draft.semesterId) + '</div><h2 class="wizard-subheading">Selecione a turma</h2><div id="wizard-classes" class="class-grid"></div>';
    const rooms = () => {
      const matches = state.classes.filter(c => c.semesterId === form.elements.semesterId.value);
      $('wizard-classes').innerHTML = matches.map(c => '<label class="class-choice"><input type="radio" name="classId" value="' + esc(c.id) + '" required ' + (draft.classId === c.id ? 'checked' : '') + '><span><strong>' + esc(c.name) + '</strong><small>' + esc(c.code) + ' · ' + state.students.filter(a => a.classId === c.id).length + ' alunos</small></span></label>').join('') || '<p class="empty">Este semestre não tem turmas. <a href="#classes">Cadastrar turma</a></p>';
    };
    form.elements.semesterId.onchange = () => { draft.classId = ''; rooms(); captureWizard(); };
    rooms();
  }
  if (step === 2) questionWorkspace(body);
  if (step === 3) {
    const names = draft.versionNames || ['A','B','C'];
    body.innerHTML = '<div class="wizard-summary"><strong>' + esc(draft.name) + '</strong><span>' + findName(state.classes,draft.classId) + ' · ' + draft.questionIds.length + ' questões</span></div>' +
      '<div class="grid-two"><section><h2>Configurar versões</h2><label>Quantidade de versões<select name="versionCount">' + [1,2,3,4,5].map(n => '<option '+(n === (draft.versionCount || 3) ? 'selected' : '')+'>'+n+'</option>').join('') + '</select></label><div id="version-names" class="version-name-fields"></div><p class="muted">Nomes únicos, com até 30 caracteres: letras, números, espaços, hífen ou sublinhado.</p><label class="check-row"><input type="checkbox" name="shuffleQuestions" ' + (draft.shuffleQuestions !== false ? 'checked' : '') + '>Embaralhar questões</label><label class="check-row"><input type="checkbox" name="shuffleAlternatives" ' + (draft.shuffleAlternatives !== false ? 'checked' : '') + '>Embaralhar alternativas e ajustar o gabarito</label><p class="muted">Todas as versões usam as mesmas questões selecionadas.</p></section><section><h2>Confira as questões e gabaritos</h2><ol class="wizard-answer-review">' +
      draft.questionIds.map(id => { const q=state.questions.find(q=>q.id===id);return '<li>'+esc(q.statement)+'<p><span class="badge">Gabarito '+q.answer+' · '+esc(q.options[q.answer.charCodeAt(0)-65])+'</span></p></li>'; }).join('') + '</ol></section></div>';
    const renderNames = values => {
      $('version-names').innerHTML = Array.from({length:Number(form.elements.versionCount.value)},(_,i) => '<label>Nome da versão '+(i+1)+'<input name="versionName" value="'+esc(values[i] ?? String.fromCharCode(65+i))+'" required maxlength="30"></label>').join('');
    };
    renderNames(names);
    form.elements.versionCount.onchange = () => { const values=Array.from(form.querySelectorAll('[name=versionName]')).map(e=>e.value);renderNames(values);captureWizard(); };
  }
  form.addEventListener('input', event => { if(event.target.form === form)captureWizard(); });
  form.addEventListener('change', event => { if(event.target.form === form)captureWizard(); });
  form.onsubmit = async event => {
    event.preventDefault(); captureWizard();
    if (step === 1 && (!draft.name.trim() || !draft.classId)) return notice('Informe o nome e selecione uma turma.');
    if (step === 2 && !draft.questionIds.length) return notice('Selecione pelo menos uma questão.');
    if (step === 2 && draft.questionIds.length > 100) return notice('Selecione no máximo 100 questões por avaliação.');
    if (step < 3) { step++;persistDraft();create();return; }
    const names=draft.versionNames.map(name=>name.trim());
    if (names.some(name=>!name || !/^[\p{L}\p{N}_ -]+$/u.test(name)) || new Set(names.map(name=>name.toLocaleLowerCase('pt-BR'))).size !== names.length) {
      $('wizard-error').hidden=false;$('wizard-error').textContent='Informe nomes válidos e diferentes para todas as versões.';return;
    }
    const buttons=form.querySelectorAll('.actions button');
    buttons.forEach(button=>{button.disabled=true;});
    event.submitter.textContent='Gerando avaliação…';
    $('wizard-error').hidden=true;
    try {
      const evaluation=await api('/evaluations',{method:'POST',body:{
        name:draft.name.trim(),classId:draft.classId,questionIds:draft.questionIds,
        versionCount:draft.versionCount,versionNames:names,
        shuffleQuestions:draft.shuffleQuestions,shuffleAlternatives:draft.shuffleAlternatives
      }});
      state.evaluations.push(evaluation);
      clearDraft();
      location.hash='evaluation?id='+encodeURIComponent(evaluation.id)+'&created=1';
      notice('Avaliação criada. Selecione uma versão para conferir questões e gabarito.');
    } catch(error) {
      if(document.contains(form)){ $('wizard-error').hidden=false;$('wizard-error').textContent=error.message; }
    } finally { buttons.forEach(button=>{button.disabled=false;});event.submitter.textContent='Gerar avaliação'; }
  };
  persistDraft();
}

// Separate form ownership avoids nesting forms inside the evaluation wizard.
let questionEntry = {};
let questionSaving = false;
function questionWorkspace(body) {
  draft.questionIds ||= [];
  body.innerHTML = '<div class="question-workspace"><section class="question-editor" aria-labelledby="new-question-title"><h2 id="new-question-title">Criar questões para esta prova</h2><p class="muted">Cada questão salva entra na prova e no banco geral. Você pode criar várias em sequência.</p><div id="question-entry-fields"><label>Enunciado<textarea form="question-entry-form" name="statement" required maxlength="2000" placeholder="Escreva o enunciado da questão"></textarea></label><div class="option-grid"><label>Disciplina<input form="question-entry-form" name="subject" required maxlength="100" placeholder="Ex.: Direito Civil"></label><label>Dificuldade<select form="question-entry-form" name="difficulty"><option>Fácil</option><option>Médio</option><option>Difícil</option></select></label></div><div class="option-grid">' + ['A', 'B', 'C', 'D'].map(a => '<label>Alternativa ' + a + '<input form="question-entry-form" name="option' + a + '" required maxlength="500"></label>').join('') + '</div><label>Resposta correta<select form="question-entry-form" name="answer"><option>A</option><option>B</option><option>C</option><option>D</option></select></label><p id="question-entry-error" role="alert" hidden></p><button form="question-entry-form" type="submit" id="save-question-entry">Salvar e criar outra questão</button></div></section><section class="question-bank-side" aria-labelledby="question-bank-title"><div class="section-heading"><div><h2 id="question-bank-title">Banco de questões</h2><p>Adicione questões existentes à prova.</p></div><span id="bank-total" class="badge"></span></div><label>Buscar no banco<input id="wizard-bank-search" type="search" placeholder="Enunciado ou disciplina"></label><p id="selected-total" role="status"></p><div id="wizard-bank-list"></div></section></div>';
  // The owner form lives outside the wizard; an empty editor never blocks Próxima.
  const owner = document.createElement('form');
  owner.id = 'question-entry-form';
  $('evaluation-form').after(owner);
  const fields = $('question-entry-fields');
  fields.querySelectorAll('[name]').forEach(field => {
    if (questionEntry[field.name] !== undefined) field.value = questionEntry[field.name];
    field.oninput = () => { questionEntry[field.name] = field.value; persistDraft(); };
  });
  function renderBank() {
    const term = $('wizard-bank-search').value.trim().toLocaleLowerCase('pt-BR');
    const matches = state.questions.filter(q => (q.statement + ' ' + q.subject).toLocaleLowerCase('pt-BR').includes(term));
    $('bank-total').textContent = state.questions.length + ' no banco';
    $('selected-total').textContent = draft.questionIds.length + ' questão(ões) adicionada(s) à prova';
    $('wizard-bank-list').innerHTML = matches.map(q => '<label class="wizard-bank-item"><input type="checkbox" name="questionIds" value="' + esc(q.id) + '" ' + (draft.questionIds.includes(q.id) ? 'checked' : '') + '><span><strong>' + esc(q.statement) + '</strong><small>' + esc(q.subject) + ' · ' + esc(q.difficulty) + '</small><small>' + (draft.questionIds.includes(q.id) ? 'Adicionada à prova' : 'Adicionar à prova') + '</small></span></label>').join('') || '<p class="empty">Nenhuma questão encontrada. Crie uma ao lado ou ajuste a busca.</p>';
    $('wizard-bank-list').querySelectorAll('input').forEach(input => {
      input.onchange = () => {
        if (input.checked) draft.questionIds = [...new Set([...draft.questionIds, input.value])];
        else draft.questionIds = draft.questionIds.filter(id => id !== input.value);
        persistDraft();
        renderBank();
      };
    });
  }
  $('wizard-bank-search').oninput = renderBank;
  renderBank();
  owner.onsubmit = async event => {
    event.preventDefault();
    if (questionSaving) return;
    questionSaving = true;
    const save = $('save-question-entry');
    const navigation = $('evaluation-form').querySelectorAll('.actions button');
    save.disabled = true;
    navigation.forEach(button => { button.disabled = true; });
    save.textContent = 'Salvando questão…';
    $('question-entry-error').hidden = true;
    const formData = new FormData(owner);
    try {
      const question = await api('/questions', { method: 'POST', body: {
        statement: formData.get('statement'), subject: formData.get('subject'),
        difficulty: formData.get('difficulty'), answer: formData.get('answer'),
        options: ['A', 'B', 'C', 'D'].map(a => formData.get('option' + a))
      } });
      state.questions.push(question);
      draft.questionIds = [...new Set([...draft.questionIds, question.id])];
      questionEntry = { subject: formData.get('subject'), difficulty: formData.get('difficulty') };
      persistDraft();
      if (document.contains(body)) {
        owner.reset();
        owner.elements.subject.value = questionEntry.subject;
        owner.elements.difficulty.value = questionEntry.difficulty;
      }
      // Clear the filter to make the new bank entry visible immediately.
      if (document.contains(body)) {
        $('wizard-bank-search').value = '';
        renderBank();
        owner.elements.statement.focus();
      }
      notice('Questão salva no banco geral e adicionada à prova. Você já pode criar a próxima.');
    } catch (error) {
      if (document.contains(body)) {
        $('question-entry-error').textContent = error.message;
        $('question-entry-error').hidden = false;
      }
    } finally {
      questionSaving = false;
      save.disabled = false;
      navigation.forEach(button => { button.disabled = false; });
      save.textContent = 'Salvar e criar outra questão';
    }
  };
}


function versionCards(evaluation, activeName = null) {
  return '<div class="version-grid">' + evaluation.versions.map(version =>
    '<article class="panel version-choice ' + (version.name === activeName ? 'selected' : '') + '"><h3>Versão ' + esc(version.name) + '</h3><p class="muted">' + version.questions.length + ' questões · gabarito próprio</p><div class="actions"><a class="btn secondary" ' + (version.name === activeName ? 'aria-current="true"' : '') + ' href="#evaluation?id=' + encodeURIComponent(evaluation.id) + '&version=' + encodeURIComponent(version.name) + '">Abrir versão ' + esc(version.name) + '</a>' +
    button('Ver QR Code','qr:'+evaluation.id+':'+encodeURIComponent(version.name),'secondary') + '</div></article>').join('') + '</div>';
}
function versions() {
  screen.innerHTML=head('Versões & QR Code','Consulte avaliações, questões e gabaritos','<a class="btn" href="#create">+ Nova avaliação</a>')+
    (state.evaluations.length ? state.evaluations.map(e=>'<section class="panel"><div class="section-heading"><div><h2>'+esc(e.name)+'</h2><p>'+findName(state.classes,e.classId)+'</p></div><a href="#evaluation?id='+encodeURIComponent(e.id)+'">Consultar avaliação →</a></div>'+versionCards(e)+'</section>').join('') : empty('Nenhuma versão gerada','Crie uma avaliação para consultar os gabaritos e QR Codes.'));
}

function documentActions(evaluation, version) {
  const params = new URLSearchParams({evaluation: evaluation.id, version: version.name});
  return '<section class="panel document-actions"><h2>Documentos · Versão ' + esc(version.name) + '</h2><div class="actions">' +
    [['exam','Imprimir prova'],['answers','Imprimir folha de respostas'],['key','Imprimir gabarito']].map(([type,label]) => '<a class="btn secondary" target="_blank" rel="noopener" href="/print?' + params.toString() + '&type=' + type + '">' + label + '</a>').join('') +
    button('Liberar gabarito ao aluno','publish-key:' + evaluation.id + ':' + encodeURIComponent(version.name)) + '</div></section>';
}
function evaluationConfirmation() {
  const params=routeParams(), evaluation=state.evaluations.find(e=>e.id===params.get('id'));
  if(!evaluation){screen.innerHTML=head('Avaliação não encontrada','Verifique o link ou selecione outra avaliação.')+'<a class="btn" href="#versions">Voltar às avaliações</a>';return;}
  const version=evaluation.versions.find(v=>v.name===params.get('version')) || evaluation.versions[0];
  screen.innerHTML='<a class="breadcrumb" href="#versions">← Todas as avaliações</a>'+
    head(params.get('created') ? 'Avaliação criada com sucesso' : esc(evaluation.name),esc(evaluation.name)+' · '+findName(state.classes,evaluation.classId)+' · '+evaluation.versions.length+' versões',
      '<a class="btn secondary" href="#create">Criar outra avaliação</a><a class="btn" href="#correction">Ir para correção</a>')+
    versionCards(evaluation,version.name)+documentActions(evaluation,version)+
    '<section class="panel version-detail"><h2>Questões e gabarito · Versão '+esc(version.name)+'</h2><ol>'+version.questions.map(q=>'<li><h3>'+esc(q.statement)+'</h3><div class="question-options">'+q.options.map((o,i)=>'<div class="'+(String.fromCharCode(65+i)===q.answerLetter?'correct':'')+'">'+String.fromCharCode(65+i)+' · '+esc(o)+'</div>').join('')+'</div><p><span class="badge">Gabarito: '+q.answerLetter+'</span></p></li>').join('')+'</ol></section>';
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
  $('modal-form').querySelector('[type=submit]').disabled = false;
  $('modal-form').querySelector('[type=submit]').textContent = 'Salvar';
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
    if (action === 'cancel-evaluation') {
      if (confirm('Descartar o rascunho da avaliação? As questões já salvas permanecerão no banco.')) { clearDraft(); location.hash = 'dashboard'; }
    }
    if (action === 'previous') {
      captureWizard();
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
    if (action === 'import-students') importStudents(id);
    if (action === 'student') modal('Novo aluno', input('Nome completo', 'name') + input('Matrícula', 'registration'), f => api('/students', {
      method: 'POST',
      body: {
        ...Object.fromEntries(f),
        classId: id
      }
    }));
    if (action === 'question') editQuestion();
    if (action === 'edit-question') editQuestion(id);
    if (action === 'import-questions') importQuestions();
    if (action === 'delete-question' && confirm('Excluir esta questão do banco? As versões já geradas serão preservadas.')) {
      await api('/questions/' + id, {
        method: 'DELETE'
      });
      await refresh();
      questions();
      notice('Questão excluída.');
    }
    if (action === 'qr') {
      const versionName = decodeURIComponent(version);
      const qr = await api('/evaluations/' + id + '/qr/' + encodeURIComponent(versionName));
      modal('QR Code · Versão ' + versionName, '<img class="qr-code" src="' + qr.image + '" alt="QR Code da versão"><p class="muted">Identifica a avaliação e a versão.</p><a class="btn" download="qr-' + version + '.png" href="' + qr.image + '">Baixar PNG</a>', async () => {});
      $('modal-form').querySelector('[type=submit]').hidden = true;
    }

    if (action === 'publish-key') {
      if (!confirm('Liberar o gabarito desta versão? Qualquer pessoa com o link poderá ver as respostas corretas.')) return;
      const name = decodeURIComponent(version);
      const link = await api('/evaluations/' + id + '/versoes/' + encodeURIComponent(name) + '/publicar', {method:'POST'});
      const url = location.origin + link.path;
      modal('Gabarito liberado · ' + name,
        '<p>Compartilhe este link quando os alunos puderem consultar as respostas. O link não mostra alunos, notas ou respostas individuais.</p><label>Link público<input id="public-key-link" readonly value="' + esc(url) + '"></label><div class="actions"><a class="btn secondary" target="_blank" rel="noopener" href="' + esc(link.path) + '">Abrir tela do aluno</a>' + button('Copiar link','copy-key','secondary') + button('Revogar acesso','revoke-key:' + id + ':' + version,'danger') + '</div>', async()=>{});
      $('modal-form').querySelector('[type=submit]').hidden=true;
    }
    if (action === 'copy-key') {
      const input=$('public-key-link');
      try { await navigator.clipboard.writeText(input.value); notice('Link copiado.'); }
      catch { input.focus(); input.select(); notice('Selecione e copie o link exibido.'); }
    }
    if (action === 'revoke-key') {
      if(!confirm('Revogar o link público deste gabarito?'))return;
      await api('/evaluations/' + id + '/versoes/' + encodeURIComponent(decodeURIComponent(version)) + '/publicar',{method:'DELETE'});
      $('modal').close(); notice('Acesso público revogado.');
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
  try {
    const saved = JSON.parse(sessionStorage.getItem(draftKey()) || 'null');
    if (saved && saved.draft && Array.isArray(saved.draft.questionIds)) {
      draft = saved.draft; step = [1,2,3].includes(saved.step) ? saved.step : 1;
      questionEntry = saved.questionEntry || {};
    }
  } catch {}
  render();
} catch (e) {
  screen.innerHTML = '<div class="panel"><h1>Não foi possível carregar</h1><p id="load-error"></p><button onclick="location.reload()">Tentar novamente</button> <a href="/">Voltar ao login</a></div>';
  $('load-error').textContent = e.message;
}
