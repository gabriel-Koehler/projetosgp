import test from 'node:test';
import assert from 'node:assert/strict';
import { requestBody, responseData } from '../public/api-contract.js';

test('question edit preserves the fifth alternative and category in the persistent contract', () => {
  const raw = {id:27,enunciado:'Pergunta',alternativas:['a','b','c','d','e'],correta:'E',disciplina:'Web',categoria:'HTML',dificuldade:'media'};
  const ui = responseData('/questions/27', raw, true);
  assert.equal(ui.id,'27');
  assert.deepEqual(requestBody('/questions/27', ui, true), {
    enunciado:raw.enunciado,alternativas:raw.alternativas,correta:'E',disciplina:'Web',categoria:'HTML',dificuldade:'media'
  });
  assert.equal(responseData('/questions?pagina=1',{itens:[raw],total:1,pagina:1,por_pagina:200},true).itens[0].answer,'E');
  const preview = {validas:[],erros:[{linha:2,mensagens:['Duplicada']}],importados:0};
  assert.equal(responseData('/questions/importar?confirmar=false',preview,true),preview);
});

test('question requests map paginated URLs, send multipart unchanged and load beyond 200 records', async () => {
  globalThis.window = {APP_CONFIG:{dataMode:'real'}};
  const originalFetch = globalThis.fetch;
  const calls = [];
  globalThis.fetch = async (url, options) => {
    calls.push({url,options});
    const page = Number(new URL(url,'http://localhost').searchParams.get('pagina') || 1);
    const payload = url.includes('importar') ? {validas:[],erros:[],importados:0} : {
      itens:Array.from({length:page === 1 ? 200 : 1},(_,i)=>({id:(page-1)*200+i+1,enunciado:'Q',alternativas:['A','B','C','D'],correta:'A'})),
      total:201,pagina:page,por_pagina:200
    };
    return new Response(JSON.stringify(payload),{status:200});
  };
  try {
    const {api,allQuestions} = await import('../public/api.js?question-test');
    const items = await allQuestions();
    assert.equal(items.length,201);
    assert.equal(items.at(-1).id,'201');
    assert.equal(calls[0].url,'/api/questoes?por_pagina=200&pagina=1');
    const body = new FormData();body.append('arquivo',new Blob(['csv']),'questoes.csv');
    await api('/questions/importar?confirmar=false',{method:'POST',body});
    assert.equal(calls.at(-1).options.body,body);
    assert.deepEqual(calls.at(-1).options.headers,{});
    assert.equal(calls.at(-1).options.credentials,'include');
  } finally { globalThis.fetch = originalFetch; delete globalThis.window; }
});
