import test from 'node:test';
import assert from 'node:assert/strict';
import {requestBody,responseData} from '../public/api-contract.js';
import {versionNames} from '../public/evaluation-settings.js';

const raw = {
  id: 12, nome:'Prova', turma_id:3, nota_maxima:20, gabarito_liberado:false,
  versoes:[{id:9,nome:'Azul 1',codigo:'persistido',url_qrcode:'/api/avaliacoes/12/versoes/persistido/qrcode.png',
    url_aluno:'http://localhost:3000/student?token=persistido',
    questoes:[{numero:1,questao_id:'77',enunciado:'Snapshot',alternativas:['a','b','c','d','e'],correta:'E',ordem_original:['A','B','C','D','E']}]}]
};

test('version names remain valid beyond Z and repeated color palettes',()=>{
  assert.deepEqual(versionNames('letters',28).slice(-3),['Z','AA','AB']);
  assert.deepEqual(versionNames('numbers',3),['1','2','3']);
  assert.deepEqual(versionNames('colors',12).slice(-2),['Azul 2','Verde 2']);
  assert.equal(new Set(versionNames('letters',500)).size,500);
});

test('evaluation request sends selected IDs, answer overrides and real version configuration',()=>{
  const draft={name:'Prova',classId:'3',questionIds:['77'],versionCount:2,versionNames:['Azul','Verde'],
    shuffleQuestions:true,shuffleAlternatives:true,sameQuestions:false,questionsPerVersion:1,maxGrade:20,answerOverrides:{77:'B'}};
  const body=requestBody('/evaluations',draft,true);
  assert.deepEqual(body,{nome:'Prova',turma_id:3,questao_ids:[77],nota_maxima:20,gabaritos:{77:'B'},
    configuracao:{quantidade:2,nomenclatura:'personalizada',nomes_personalizados:['Azul','Verde'],mesmas_questoes:false,
      questoes_por_versao:1,embaralhar_questoes:true,embaralhar_alternativas:true}});
  assert.equal(requestBody('/evaluations',draft,false),draft);
});

test('stored snapshot and version code feed the UI independently of the question bank',()=>{
  const result=responseData('/evaluations/12',raw,true);
  assert.equal(result.id,'12'); assert.equal(result.classId,'3');
  assert.equal(result.versions[0].questions[0].correctAnswer,'e');
  assert.equal(result.versions[0].questions[0].statement,'Snapshot');
  assert.equal(result.versions[0].code,'persistido');
  const summary=responseData('/evaluations',[{id:12,nome:'Prova',quantidade_versoes:2,quantidade_questoes:7}],true)[0];
  assert.equal(summary.versionCount,2); assert.equal(summary.questionCount,7);
  assert.equal(summary.versions,undefined);
  const publicKey=responseData('/public/gabaritos/persistido',{avaliacao:'Prova',versao:'Azul',gabarito:[{questao:1,alternativa:'E'}]},true);
  assert.deepEqual(publicKey,{name:'Prova',version:'Azul',questions:[{position:1,answerLetter:'E'}]});
});

test('detail, publication and QR use persistent endpoints without requesting the mock QR route',async()=>{
  globalThis.window={APP_CONFIG:{dataMode:'real'}};
  const originalFetch=globalThis.fetch, calls=[];
  globalThis.fetch=async(url,options)=>{
    calls.push({url,options});return new Response(JSON.stringify(raw),{status:200});
  };
  try {
    const {api,evaluationQr}=await import('../public/api.js?evaluation-test');
    const evaluation=await api('/evaluations/12');
    assert.equal(calls[0].url,'/api/avaliacoes/12');
    assert.deepEqual(await evaluationQr(evaluation,evaluation.versions[0]),{image:raw.versoes[0].url_qrcode});
    assert.equal(calls.length,1);
    await api('/evaluations/12/gabarito',{method:'PATCH',body:{liberado:true}});
    assert.equal(calls[1].url,'/api/avaliacoes/12/gabarito');
    assert.equal(calls[1].options.body,'{"liberado":true}');
    assert.equal(calls[1].options.credentials,'include');
  } finally {globalThis.fetch=originalFetch; delete globalThis.window;}
});
