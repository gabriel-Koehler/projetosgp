import test from 'node:test';
import assert from 'node:assert/strict';
import {requestBody,responseData,errorMessage} from '../public/api-contract.js';
test('persistent contracts translate login, dates, semester and class relations',()=>{
 assert.deepEqual(requestBody('/auth/login',{email:' professor ',password:'x'},true),{username:'professor',password:'x'});
 assert.deepEqual(requestBody('/semesters',{name:'2027',startDate:'',endDate:''},true),{nome:'2027',data_inicio:null,data_fim:null});
 assert.deepEqual(requestBody('/classes/8',{name:'A',semesterId:'12',subject:'Física'},true),{nome:'A',semestre_id:12,disciplina:'Física'});
 assert.deepEqual(responseData('/classes',[{id:8,nome:'A',semestre_id:12,disciplina:'Física'}],true),[{id:'8',name:'A',semesterId:'12',subject:'Física',code:'Física'}]);
 assert.equal(responseData('/auth/me',{username:'prof',nome:'Professor'},true).id,'prof');
});
test('mock envelope and payload stay compatible',()=>{
 const body={name:'N1'};assert.equal(requestBody('/semesters',body,false),body);
 assert.deepEqual(responseData('/semesters',{data:[body]},false),[body]);
});
test('validation arrays, unavailable backend and duplicate errors have readable messages',()=>{
 assert.match(errorMessage({detail:[{loc:['body','nome'],input:'private'}]},422),/campos/);
 assert.equal(errorMessage({detail:'Já existe'},409),'Já existe');
 assert.match(errorMessage(null,502),/indisponível/);
});
