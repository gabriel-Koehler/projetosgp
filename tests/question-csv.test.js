import test from 'node:test';
import assert from 'node:assert/strict';
import { parseQuestionsCsv } from '../public/question-csv.js';
const header='enunciado;disciplina;dificuldade;alternativa_a;alternativa_b;alternativa_c;alternativa_d;gabarito\n';
test('question import preserves quoted text and normalizes difficulty/answer',()=>{
 const rows=parseQuestionsCsv(header+'"Quanto; vale?";Matemática;facil;Um;Dois;Três;Quatro;c');
 assert.equal(rows[0].question.statement,'Quanto; vale?');assert.equal(rows[0].question.answer,'C');assert.equal(rows[0].error,'');
});
test('question import flags duplicates, missing alternatives and invalid keys',()=>{
 const row='Q;Disciplina;Médio;A1;B1;C1;D1;A';
 const rows=parseQuestionsCsv(header+row+'\n'+row+'\nQ2;D;Fácil;;B;C;D;A\nQ3;D;Fácil;A;B;C;D;Z');
 assert.equal(rows.filter(r=>!r.error).length,1);
 assert.ok(rows.slice(1).every(r=>r.error));
 assert.ok(parseQuestionsCsv(header+row,[rows[0].question])[0].error);
});
test('question import rejects malformed csv and missing headers',()=>{
 assert.throws(()=>parseQuestionsCsv('nome;matricula\nA;1'));
 assert.throws(()=>parseQuestionsCsv(header+'"Unclosed'));
 assert.throws(()=>parseQuestionsCsv(header+'Bad"quote;D;Fácil;A;B;C;D;A'));
});

