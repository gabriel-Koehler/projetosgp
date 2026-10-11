import { api } from './api.js';
import { escapeHtml as esc } from './html.js';

const options = items => items.map(i => `<option value="${esc(i.id)}">${esc(i.name)}</option>`).join('');
const heading = title => `<header class="section-heading"><h1>${title}</h1></header>`;

export function realCorrection(root, state, notice) {
  let disposed = false, revision = 0, evaluation, busy = false;
  root.innerHTML = heading('Correção de provas') + (!state.evaluations.length
    ? '<section class="panel"><p>Crie uma avaliação antes de corrigir.</p><a href="#create">Criar avaliação</a></section>'
    : `<form class="panel"><label>Avaliação<select name="evaluation">${options(state.evaluations)}</select></label>
      <div id="correction-context"></div><p role="alert" id="correction-error"></p></form>`);
  if (!state.evaluations.length) return () => {};
  const form = root.querySelector('form'), context = root.querySelector('#correction-context');
  const error = message => { if (!disposed) root.querySelector('#correction-error').textContent = message; };
  const version = () => evaluation?.versions.find(v => v.id === form.elements.version?.value);
  const review = (answers = {}) => {
    const selected = version();
    if (!selected) return;
    context.querySelector('#answers').innerHTML = selected.questions.map(q => `<label>Questão ${q.position}
      <select name="answer-${q.position}"><option value="">Em branco</option><option value="*">Múltiplas marcações</option>${q.options.map((_, i) => {
        const letter = String.fromCharCode(65 + i);
        return `<option value="${letter}">${letter}</option>`;
      }).join('')}</select></label>`).join('');
    for (const q of selected.questions) form.elements['answer-' + q.position].value = answers[q.position] || '';
    form.elements.confirm.checked = false;
  };
  const load = async () => {
    const current = ++revision;
    context.innerHTML = '<p role="status">Carregando avaliação…</p>'; error('');
    try {
      const selected = await api('/evaluations/' + encodeURIComponent(form.elements.evaluation.value));
      const students = selected.classId ? await api('/turmas/' + encodeURIComponent(selected.classId) + '/alunos') : [];
      if (disposed || current !== revision) return;
      evaluation = selected;
      context.innerHTML = `<label>Versão<select name="version">${options(selected.versions)}</select></label>
        <label>Aluno<select name="student"><option value="">Sem identificação</option>${students.map(s => `<option value="${s.id}">${esc(s.nome)} · ${esc(s.matricula)}</option>`).join('')}</select></label>
        <h2>Leitura da folha</h2><p>Use a folha gerada pelo sistema. Envie PNG ou JPEG de até 4 MB, ou informe as respostas manualmente.</p>
        <label>Imagem<input type="file" name="image" accept="image/png,image/jpeg"></label>
        <button type="button" id="read-sheet">Ler folha</button><p id="reading-status" role="status"></p>
        <h2>Confira as respostas</h2><div class="review-grid" id="answers"></div>
        <label><input type="checkbox" name="confirm" required> Conferi o aluno, a versão e as respostas.</label>
        <button type="submit">Corrigir e salvar</button>`;
      review();
      form.elements.version.onchange = () => { review(); context.querySelector('#reading-status').textContent = ''; };
      context.querySelector('#read-sheet').onclick = async () => {
        if (busy) return;
        const file = form.elements.image.files[0];
        if (!file || !['image/png', 'image/jpeg'].includes(file.type) || file.size > 4 * 1024 * 1024) {
          error('Selecione uma imagem PNG ou JPEG de até 4 MB.'); return;
        }
        busy = true; error('');
        form.elements.evaluation.disabled = form.elements.version.disabled = true;
        context.querySelector('#read-sheet').disabled = true;
        try {
          const body = new FormData(); body.append('imagem', file);
          const reading = await api('/correcoes/leitura', {method:'POST', body});
          if (disposed) return;
          const found = evaluation.versions.find(v => v.code === reading.codigo);
          if (!found) throw new Error('A folha pertence a outra avaliação. Selecione a avaliação correspondente.');
          form.elements.version.value = found.id; review(reading.respostas);
          context.querySelector('#reading-status').textContent = reading.mensagem;
        } catch (e) { error(e.message); }
        finally {
          busy = false;
          if (!disposed) { form.elements.evaluation.disabled = form.elements.version.disabled = false; context.querySelector('#read-sheet').disabled = false; }
        }
      };
    } catch (e) { if (current === revision) { context.replaceChildren(); error(e.message); } }
  };
  form.elements.evaluation.onchange = load;
  form.onsubmit = async event => {
    event.preventDefault();
    if (busy || !version() || !form.reportValidity()) return;
    busy = true; error('');
    const selected = version();
    const body = {codigo:selected.code, aluno_id:form.elements.student.value ? Number(form.elements.student.value) : null,
      respostas:Object.fromEntries(selected.questions.map(q => [q.position, form.elements['answer-' + q.position].value || null]))};
    const controls = [...form.querySelectorAll('button,input,select')]; controls.forEach(el => el.disabled = true);
    try {
      const result = await api('/correcoes/manual', {method:'POST', body});
      if (!disposed) { notice(`Correção salva. Nota: ${result.nota} / ${result.nota_maxima}`); location.hash = '#results'; }
    } catch (e) { error(e.message); }
    finally { busy = false; if (!disposed) controls.forEach(el => el.disabled = false); }
  };
  load();
  return () => { disposed = true; revision++; };
}

export function realResults(root, state) {
  let disposed = false, revision = 0;
  root.innerHTML = heading('Resultados e estatísticas') + `<section class="panel"><label>Avaliação<select id="result-evaluation">${options(state.evaluations)}</select></label><div id="real-results"></div></section>`;
  const select = root.querySelector('select'), content = root.querySelector('#real-results');
  const load = async () => {
    const current = ++revision;
    if (!select.value) { content.textContent = 'Nenhuma avaliação cadastrada.'; return; }
    content.innerHTML = '<p role="status">Carregando resultados…</p>';
    try {
      const base = '/avaliacoes/' + encodeURIComponent(select.value);
      const [results, stats] = await Promise.all([api(base + '/resultados'), api(base + '/estatisticas')]);
      if (disposed || current !== revision) return;
      content.innerHTML = `<div class="actions"><a class="btn secondary" href="/api${base}/resultados.xlsx">Exportar Excel</a><a class="btn" href="#correction">Corrigir prova</a></div>
        <p>${stats.provas_corrigidas} provas corrigidas · Média: ${stats.media ?? '—'} · Maior nota: ${stats.maior_nota ?? '—'} · Menor nota: ${stats.menor_nota ?? '—'}</p>
        ${results.length ? results.map(r => `<details class="panel"><summary>${esc(r.aluno_nome || 'Sem identificação')} · Versão ${esc(r.versao_nome)} · Nota ${r.nota} / ${r.nota_maxima}</summary><p>Acertos: ${r.acertos} · Erros: ${r.erros} · Em branco: ${r.em_branco} · Anuladas: ${r.anuladas}</p>
        <div class="table-wrap"><table><thead><tr><th>Questão</th><th>Marcada</th><th>Correta</th><th>Situação</th></tr></thead><tbody>${r.questoes.map(q => `<tr><td>${q.numero}</td><td>${esc(q.marcada || '—')}</td><td>${esc(q.correta)}</td><td>${esc(q.situacao)}</td></tr>`).join('')}</tbody></table></div></details>`).join('') : '<p>Nenhuma prova corrigida nesta avaliação.</p>'}
        <h2>Desempenho por questão</h2><div class="table-wrap"><table><thead><tr><th>Questão</th><th>Acertos</th><th>Percentual</th><th>Mais escolhida</th></tr></thead><tbody>${stats.por_questao.map(q => `<tr><td>${esc(q.enunciado)}</td><td>${q.acertos}/${q.respondentes}</td><td>${q.percentual_acerto}%</td><td>${esc(q.mais_escolhida || '—')}</td></tr>`).join('')}</tbody></table></div>`;
    } catch (e) { if (!disposed && current === revision) content.textContent = e.message; }
  };
  select.onchange = load; load();
  return () => { disposed = true; revision++; };
}
