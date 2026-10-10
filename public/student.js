import { api } from './api.js';
import { escapeHtml as esc } from './html.js';
const root=document.getElementById('public-answer-key');
try {
 const token=new URLSearchParams(location.search).get('token');
 if(!token)throw new Error('Solicite ao professor o link do gabarito.');
 const view=await api('/public/gabaritos/'+encodeURIComponent(token));
 root.innerHTML='<header><span class="badge">Gabarito liberado pelo professor</span><h1>'+esc(view.name)+'</h1><p>Versão '+esc(view.version)+' · '+view.questions.length+' questões</p></header><ol class="student-questions">'+view.questions.map(q=>'<li class="panel"><h2>Questão '+q.position+'</h2>'+(q.statement ? '<p>'+esc(q.statement)+'</p>' : '')+'<p class="correct">Resposta correta: '+esc(q.answerLetter)+(q.correctAnswer ? ' · '+esc(q.correctAnswer) : '')+'</p></li>').join('')+'</ol>';
} catch(error) {
 root.innerHTML='<section class="panel"><h1>Gabarito não disponível</h1><p>'+esc(error.message)+'</p><p>Confira com seu professor se o link foi liberado.</p></section>';
}
