import test from 'node:test';
import assert from 'node:assert/strict';
import express from 'express';
import session from 'express-session';
import {
  createMockApi
} from '../src/mock-api.js';

test('API mock: sessão, validação, isolamento, versões e correção', async () => {
  const app = express();
  app.use(express.json());
  app.use(session({
    secret: 'test-only',
    resave: false,
    saveUninitialized: false
  }));
  app.use('/api', createMockApi());
  const server = app.listen(0, '127.0.0.1');
  await new Promise(resolve => server.once('listening', resolve));
  let cookie = '';
  const call = async (path, method = 'GET', body) => {
    const response = await fetch('http://127.0.0.1:' + server.address().port + '/api' + path, {
      method,
      headers: {
        'Content-Type': 'application/json',
        Cookie: cookie
      },
      body: body === undefined ? undefined : JSON.stringify(body)
    });
    if (response.headers.get('set-cookie')) cookie = response.headers.get('set-cookie').split(';')[0];
    return {
      status: response.status,
      ...await response.json()
    };
  };
  try {
    assert.equal((await call('/questions')).status, 401);
    assert.equal((await call('/auth/login', 'POST', {
      email: 'professor',
      password: 'bad'
    })).status, 401);
    assert.equal((await call('/auth/login', 'POST', {
      email: 'professor',
      password: '123456'
    })).status, 200);
    const initial = (await call('/workspace')).data;
    assert.equal((await call('/questions', 'POST', {
      statement: 'Incomplete'
    })).status, 400);
    assert.equal((await call('/evaluations', 'POST', {
      name: 'Teste',
      classId: 'c1',
      questionIds: ['Q-047'],
      versionCount: 100
    })).status, 400);
    const evaluation = (await call('/evaluations', 'POST', {
      name: 'Teste',
      classId: 'c1',
      questionIds: initial.questions.map(q => q.id),
      versionCount: 3,
      shuffleAlternatives: true,
      shuffleQuestions: true
    })).data;
    assert.equal(evaluation.versions.length, 3);
    for (const v of evaluation.versions)
      for (const q of v.questions) assert.equal(q.options[q.answerLetter.charCodeAt(0) - 65], q.correctAnswer);
    const body = {
      evaluationId: evaluation.id,
      studentId: 'a1',
      version: 'A',
      answers: evaluation.versions[0].questions.map(q => q.answerLetter)
    };
    assert.equal((await call('/results', 'POST', {
      ...body,
      studentId: 'unknown'
    })).status, 400);
    assert.equal((await call('/results', 'POST', body)).data.grade, 10);
    assert.equal((await call('/results', 'POST', body)).status, 409);
    assert.match((await call('/evaluations/' + evaluation.id + '/qr/A')).data.image, /^data:image\/png/);
    await call('/auth/logout', 'POST');
    assert.equal((await call('/auth/me')).status, 401);
    await call('/auth/register', 'POST', {
      name: 'Outra conta',
      email: 'other@example.com',
      password: '123456'
    });
    assert.equal((await call('/workspace')).data.evaluations.length, 0);
  } finally {
    server.closeAllConnections();
    await new Promise(resolve => server.close(resolve));
  }
});
