import { api } from './api.js';
import { escapeHtml as esc } from './html.js';
import { importSpreadsheet } from './spreadsheet-import.js';

const action = (label, kind, id = '', style = 'secondary') =>
  `<button type="button" class="${style}" data-roster="${kind}" data-id="${esc(id)}">${label}</button>`;

function studentFields(student) {
  return `<label>Nome completo<input name="nome" value="${esc(student?.nome || '')}" required maxlength="200"></label>
    <label>Matrícula<input name="matricula" value="${esc(student?.matricula || '')}" required maxlength="50"></label>
    <label>E-mail (opcional)<input name="email" type="email" value="${esc(student?.email || '')}" maxlength="254"></label>`;
}

function importRow({linha, dados, mensagens}) {
  return `<article class="import-question ${mensagens.length ? 'invalid-row' : ''}">
    <small>Linha ${linha}</small>
    ${dados.nome ? `<p><strong>${esc(dados.nome)}</strong> · ${esc(dados.matricula)}${dados.email ? ' · ' + esc(dados.email) : ''}</p>` : ''}
    <p>${esc(mensagens.join(' ') || 'Válida')}</p>
  </article>`;
}

export function renderClassStudents(root, state, id, {modal, notice, real}) {
  const room = state.classes.find(item => item.id === id);
  if (!room) {
    root.innerHTML = '<section class="panel empty"><h1>Turma não encontrada</h1><a class="btn secondary" href="#classes">Voltar aos semestres</a></section>';
    return () => {};
  }

  const endpoint = '/turmas/' + encodeURIComponent(room.id) + '/alunos';
  const semester = state.semesters.find(item => item.id === room.semesterId);
  root.innerHTML = `<a class="breadcrumb" href="#classes?semester=${encodeURIComponent(room.semesterId)}">← Semestres &amp; Turmas</a>
    <header class="section-heading"><div><h1>${esc(room.name)}</h1><p>${[semester?.name, room.subject || room.code].filter(Boolean).map(esc).join(' · ')}</p></div>
      <div class="actions">${action('Importar alunos', 'import')}${action('+ Adicionar aluno', 'add', '', '')}</div>
    </header>
    <p id="roster-error" class="form-error" role="alert" hidden></p>
    <section class="panel"><h2>Alunos da turma</h2>
      <label>Buscar aluno<input id="student-search" type="search" placeholder="Nome, matrícula ou e-mail"></label>
      <p id="student-count" class="muted" role="status">Carregando alunos…</p>
      <div id="student-list"></div>
    </section>`;

  const search = root.querySelector('#student-search');
  const count = root.querySelector('#student-count');
  const list = root.querySelector('#student-list');
  const error = root.querySelector('#roster-error');
  let students = [];
  let loaded = false;
  let disposed = false;
  let removing = false;
  let loadVersion = 0;

  function showError(message) {
    if (disposed) return;
    error.textContent = message;
    error.hidden = false;
  }

  function renderList() {
    if (!loaded || disposed) return;
    const term = search.value.trim().toLocaleLowerCase('pt-BR');
    const filtered = students.filter(student =>
      [student.nome, student.matricula, student.email].some(value => (value || '').toLocaleLowerCase('pt-BR').includes(term))
    );
    count.textContent = filtered.length + ' de ' + students.length + ' alunos';
    list.innerHTML = filtered.length
      ? `<div class="table-wrap"><table><thead><tr><th>Nome</th><th>Matrícula</th><th>E-mail</th><th>Ações</th></tr></thead>
        <tbody>${filtered.map(student => `<tr><td>${esc(student.nome)}</td><td>${esc(student.matricula)}</td><td>${esc(student.email || '—')}</td>
          <td><div class="actions">${action('Editar', 'edit', student.id)}${action('Remover', 'delete', student.id, 'danger')}</div></td></tr>`).join('')}</tbody></table></div>`
      : '<p class="empty">' + (students.length ? 'Nenhum aluno encontrado para essa busca.' : 'Adicione um aluno ou importe uma planilha para começar.') + '</p>';
  }

  async function load() {
    const version = ++loadVersion;
    try {
      const response = await api(endpoint);
      if (disposed || version !== loadVersion) return;
      students = response;
      loaded = true;
      if (!real) {
        state.students = state.students.filter(student => student.classId !== room.id);
        state.students.push(...students.map(student => ({
          id: student.id, classId: room.id, name: student.nome, registration: student.matricula, email: student.email
        })));
      }
      renderList();
    } catch (failure) {
      if (disposed || version !== loadVersion) return;
      count.textContent = 'Não foi possível carregar a lista de alunos.';
      list.innerHTML = action('Tentar novamente', 'reload');
      showError(failure.message);
    }
  }

  search.oninput = renderList;
  root.onclick = async event => {
    const button = event.target.closest('[data-roster]');
    if (!button || removing) return;
    const {roster: kind, id: studentId} = button.dataset;
    const student = students.find(item => String(item.id) === studentId);
    if (kind === 'reload') {
      error.hidden = true;
      button.disabled = true;
      await load();
    }
    if (kind === 'add' || (kind === 'edit' && student)) {
      modal(student ? 'Editar aluno' : 'Adicionar aluno', studentFields(student), async form => {
        const nome = form.get('nome').trim();
        const matricula = form.get('matricula').trim();
        if (!nome || !matricula) throw new Error('Informe o nome e a matrícula.');
        const path = student ? '/alunos/' + encodeURIComponent(student.id) : endpoint;
        await api(path, {method: student ? 'PUT' : 'POST', body: {nome, matricula, email: form.get('email').trim() || null}});
      });
    }
    if (kind === 'delete' && student && confirm('Remover ' + student.nome + ' da turma? Correções registradas serão preservadas sem o vínculo com o aluno.')) {
      removing = true;
      button.disabled = true;
      error.hidden = true;
      try {
        await api('/alunos/' + encodeURIComponent(student.id), {method: 'DELETE'});
        await load();
        if (!disposed) notice('Aluno removido da turma.');
      } catch (failure) {
        showError(failure.message);
      } finally {
        removing = false;
        button.disabled = false;
      }
    }
    if (kind === 'import') {
      importSpreadsheet({
        title: 'Importar alunos · ' + room.name,
        description: 'Baixe o modelo e substitua a linha de exemplo. Nome e matrícula são obrigatórios e e-mail é opcional. Envie CSV ou Excel de até 4 MB e confira a prévia antes de importar.',
        modelPath: '/api/alunos/modelo',
        uploadPath: endpoint + '/importar',
        validLabel: 'alunos válidos',
        maxBytes: 4 * 1024 * 1024,
        renderRow: importRow,
        onImported: async (imported, rejected) => {
          await load();
          if (!disposed) notice(`${imported} aluno(s) importado(s).${rejected ? ' ' + rejected + ' linha(s) inválida(s) ignorada(s).' : ''}`);
        }
      });
    }
  };
  load();
  return () => {
    disposed = true;
    root.onclick = null;
  };
}
