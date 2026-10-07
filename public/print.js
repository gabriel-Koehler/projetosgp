import { api, evaluationQr } from './api.js';
import { escapeHtml as esc } from './html.js';
const root=document.getElementById('document-content');
const params=new URLSearchParams(location.search);
const kinds={exam:'Prova',answers:'Folha de respostas',key:'Gabarito do professor'};
try {
 const kind=params.get('type')||'exam';
 if(!kinds[kind])throw new Error('Tipo de documento inválido.');
 const evaluation=await api('/evaluations/'+encodeURIComponent(params.get('evaluation')||''));
 const version=evaluation.versions.find(v=>v.name===params.get('version'));
 if(!version)throw new Error('Versão não encontrada.');
 const classes=await api('/classes');
 const room=classes.find(c=>c.id===evaluation.classId);
 let qr=null;
 if(kind==='answers')qr=await evaluationQr(evaluation,version);
 const letters=Array.from({length:Math.max(...version.questions.map(q=>q.options.length))},(_,i)=>String.fromCharCode(65+i));
 const heading='<header class="paper-heading"><div><strong>AvaliaSystem</strong><h1>'+esc(evaluation.name)+'</h1><p>'+esc(room?.name||'')+' · '+esc(room?.code||'')+'</p><h2>'+kinds[kind]+' · Versão '+esc(version.name)+'</h2></div>'+(qr?'<img class="answer-qr" src="'+qr.image+'" alt="QR Code de identificação da avaliação e versão">':'')+'</header>';
 const identification='<div class="identification"><p>Aluno(a): <span class="write-line"></span></p><p>Matrícula: <span class="write-line"></span> Data: ____ / ____ / ______</p></div>';
 let content='';
 if(kind==='exam')content='<p class="document-instructions">Leia os enunciados e marque uma alternativa por questão na folha de respostas.</p><ol class="print-questions">'+version.questions.map(q=>'<li><h3>'+esc(q.statement)+'</h3><ol type="A">'+q.options.map(o=>'<li>'+esc(o)+'</li>').join('')+'</ol></li>').join('')+'</ol>';
 if(kind==='answers')content='<p class="document-instructions">Preencha completamente uma única bolinha por questão, com caneta azul ou preta. Não rasure nem escreva sobre o QR Code.</p><table class="answer-table"><thead><tr><th>Questão</th>'+letters.map(a=>'<th>'+a+'</th>').join('')+'</tr></thead><tbody>'+version.questions.map((q,i)=>'<tr><th scope="row">'+(i+1)+'</th>'+letters.map((a,j)=>'<td>'+(j<q.options.length?'<span class="answer-bubble" aria-label="Questão '+(i+1)+', alternativa '+a+'"></span>':'—')+'</td>').join('')+'</tr>').join('')+'</tbody></table><p class="document-reference">Identificação: '+esc(evaluation.id)+' · Versão '+esc(version.name)+'</p>';
 if(kind==='key')content='<p class="teacher-only">Uso do professor — contém respostas corretas.</p><ol class="print-questions">'+version.questions.map(q=>'<li><h3>'+esc(q.statement)+'</h3><p>Resposta: <strong>'+q.answerLetter+' · '+esc(q.correctAnswer)+'</strong></p></li>').join('')+'</ol>';
 root.innerHTML='<article class="paper">'+heading+(kind==='key'?'':identification)+content+'</article>';
 document.title=kinds[kind]+' — '+evaluation.name+' — '+version.name;
 if(qr)await root.querySelector('img').decode();
 const print=document.getElementById('print-document');print.disabled=false;print.onclick=()=>window.print();
 root.dataset.ready='true';
} catch(error) {
 root.innerHTML='<section class="panel document-error"><h1>Não foi possível abrir o documento</h1><p>'+esc(error.message)+'</p><a href="/dashboard#versions">Voltar às versões</a></section>';
}
