import test from 'node:test';
import assert from 'node:assert/strict';
import { parseStudentsCsv } from '../public/student-csv.js';
test('CSV supports BOM, CRLF, quoted delimiters and leading zero registrations', () => {
 const rows=parseStudentsCsv('\uFEFFnome;matricula\r\n"Ana; Maria";00123\r\nBruno;00234\r\n');
 assert.equal(rows[0].name,'Ana; Maria');assert.equal(rows[0].registration,'00123');assert.ok(rows.every(r=>!r.error));
});
test('CSV previews invalid/duplicate rows without admitting them', () => {
 const rows=parseStudentsCsv('nome,matricula\nAna,01\nBruno,01\n,02\nCarlos,03', [{registration:'03'}]);
 assert.equal(rows.filter(r=>!r.error).length,1);assert.match(rows[1].error,/duplicada/);assert.ok(rows[2].error);assert.ok(rows[3].error);
});
test('CSV rejects malformed headers, quotes, empty and oversized batches', () => {
 for(const content of ['nome,email\nAna,x','nome;matricula\n"Ana;1','nome;matricula','nome;matricula\n'+Array.from({length:501},(_,i)=>'Aluno;'+i).join('\n')])assert.throws(()=>parseStudentsCsv(content));
});

