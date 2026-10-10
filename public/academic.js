import {
  api
} from './api.js';
import {
  escapeHtml as esc
} from './html.js';
const field = (label, name, value = '', type = 'text', required = true, max = 100) => `<label>${label}<input name="${name}" type="${type}" value="${esc(value)}" ${required?'required':''} maxlength="${max}"></label>`;
const action = (label, kind, id = '', css = 'secondary') => `<button type="button" class="${css}" data-academic="${kind}" data-id="${esc(id)}">${label}</button>`;
export function academic(root, state, {
  modal,
  refresh,
  render,
  notice
}) {
  const params = new URLSearchParams(location.hash.split('?')[1] || '');
  const current = state.semesters.find(s => s.id === params.get('semester')) || state.semesters[0];
  const rooms = state.classes.filter(c => c.semesterId === current?.id);
  root.innerHTML = `<header class="section-heading"><div><h1>Semestres & Turmas</h1><p>Organize os períodos letivos e as turmas da sua conta.</p></div><div class="actions">${action('Atualizar','reload')}${action('+ Novo semestre','semester')}${current?action('+ Nova turma','class','',''):''}</div></header><p id="academic-error" class="form-error" role="alert" hidden></p>
  <div class="semester-layout"><aside class="panel semester-list" aria-label="Semestres"><h2>Semestres</h2>${state.semesters.map(s=>`<a class="semester-card ${s.id===current?.id?'selected':''}" href="#classes?semester=${encodeURIComponent(s.id)}" ${s.id===current?.id?'aria-current="true"':''}><strong>${esc(s.name)}</strong><span class="badge">${s.active?'Ativo':'Inativo'}</span><small>${state.classes.filter(c=>c.semesterId===s.id).length} turmas</small></a>`).join('') || '<p>Nenhum semestre cadastrado.</p>'}</aside>
  <section aria-label="Turmas do semestre">${current?`<section class="panel"><div class="section-heading"><div><h2>${esc(current.name)}</h2><p>${current.startDate?esc(date(current.startDate)):'Início não informado'} · ${current.endDate?esc(date(current.endDate)):'Fim não informado'}</p></div><div class="actions">${action('Editar semestre','edit-semester',current.id)}${action(current.active?'Desativar':'Ativar','toggle-semester',current.id)}</div></div></section><div class="class-grid">${rooms.map(c=>`<article class="panel class-card"><span class="badge">${esc(c.subject||'Sem disciplina')}</span><h3>${esc(c.name)}</h3><p>${esc(current.name)}</p><div class="actions">${action('Editar turma','edit-class',c.id)}${action('Excluir turma','delete-class',c.id,'danger')}</div></article>`).join('')}</div>${rooms.length?'':'<section class="panel empty"><h2>Nenhuma turma neste semestre</h2><p>Use Nova turma para cadastrar a primeira turma.</p></section>'}`:'<section class="panel empty"><h2>Cadastre seu primeiro semestre</h2><p>Depois, adicione as turmas do período letivo.</p></section>'}</section></div>`;
  const semesterFields = s => field('Nome do semestre', 'name', s?.name || '') + '<div class="grid-two">' + field('Data de início', 'startDate', s?.startDate || '', 'date', false) + field('Data de fim', 'endDate', s?.endDate || '', 'date', false) + '</div>';
  const classFields = c => field('Nome da turma', 'name', c?.name || '') + field('Disciplina (opcional)', 'subject', c?.subject || '', 'text', false, 200) + `<label>Semestre<select name="semesterId" required>${state.semesters.map(s=>`<option value="${esc(s.id)}" ${s.id===(c?.semesterId||current?.id)?'selected':''}>${esc(s.name)}</option>`).join('')}</select></label>`;
  let disposed = false,
    busy = false;
  root.onclick = async event => {
    const button = event.target.closest('[data-academic]');
    if (!button || busy) return;
    const {
      academic: kind,
      id
    } = button.dataset;
    if (kind === 'semester' || kind === 'edit-semester') {
      const semester = state.semesters.find(s => s.id === id);
      modal(semester ? 'Editar semestre' : 'Novo semestre', semesterFields(semester), async f => {
        const body = Object.fromEntries(f);
        body.name = body.name.trim();
        if (!body.name) throw new Error('Informe o nome do semestre.');
        if (body.startDate && body.endDate && body.endDate < body.startDate) throw new Error('A data de fim deve ser igual ou posterior à data de início.');
        const saved = await api('/semesters' + (semester ? '/' + id : ''), {
          method: semester ? 'PUT' : 'POST',
          body
        });
        history.replaceState(null, '', '#classes?semester=' + encodeURIComponent(saved.id));
      });
      return;
    }
    if (kind === 'class' || kind === 'edit-class') {
      const room = state.classes.find(c => c.id === id);
      modal(room ? 'Editar turma' : 'Nova turma', classFields(room), async f => {
        const body = Object.fromEntries(f);
        body.name = body.name.trim();
        body.subject = body.subject.trim();
        if (!body.name) throw new Error('Informe o nome da turma.');
        await api('/classes' + (room ? '/' + id : ''), {
          method: room ? 'PUT' : 'POST',
          body
        });
        history.replaceState(null, '', '#classes?semester=' + encodeURIComponent(body.semesterId));
      });
      return;
    }
    if (kind === 'delete-class' && !confirm('Excluir a turma ' + state.classes.find(c => c.id === id)?.name + '?')) return;
    busy = true;
    button.disabled = true;
    root.setAttribute('aria-busy', 'true');
    const error = root.querySelector('#academic-error');
    error.hidden = true;
    try {
      if (kind === 'delete-class') await api('/classes/' + id, {
        method: 'DELETE'
      });
      if (kind === 'toggle-semester') await api('/semesters/' + id + '/ativo', {
        method: 'PATCH',
        body: {
          active: !current.active
        }
      });
      await refresh();
      if (!disposed) {
        render();
        notice(kind === 'reload' ? 'Dados atualizados.' : 'Alteração salva.');
      }
    } catch (err) {
      if (!disposed) {
        error.hidden = false;
        error.textContent = err.message;
      }
    } finally {
      if (!disposed) {
        busy = false;
        button.disabled = false;
        root.removeAttribute('aria-busy');
      }
    }
  };
  return () => {
    disposed = true;
    root.onclick = null;
    root.removeAttribute('aria-busy');
  };
}

function date(value) {
  return value.split('-').reverse().join('/');
}
