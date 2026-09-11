import test from 'node:test';
import assert from 'node:assert/strict';

import { buildVersions, buildStudentView } from '../src/core.js';

test('buildVersions gera versões com gabarito próprio e sem duplicar questão correta', () => {
  const questions = [
    { id: 'q1', statement: 'Q1', options: ['A', 'B', 'C', 'D'], answer: 'B' },
    { id: 'q2', statement: 'Q2', options: ['A', 'B', 'C', 'D'], answer: 'C' },
    { id: 'q3', statement: 'Q3', options: ['A', 'B', 'C', 'D'], answer: 'D' }
  ];

  const result = buildVersions({
    questions,
    versionCount: 3,
    naming: 'A,B,C',
    sameSet: true,
    shuffleQuestions: true,
    shuffleAlternatives: true
  });

  assert.equal(result.length, 3);
  result.forEach((version) => {
    assert.equal(version.questions.length, 3);
    assert.equal(version.answerKey.length, 3);
    assert.deepEqual(
      version.questions.map((q) => q.id).sort(),
      ['q1', 'q2', 'q3']
    );
    assert.ok(version.answerKey.every((item) => item.correct !== undefined));
  });
});

test('buildStudentView exibe somente alternativas corretas e não resposta do aluno', () => {
  const view = buildStudentView({
    versionName: 'Versão A',
    questions: [
      { id: 'q1', statement: 'Q1', options: ['A', 'B', 'C', 'D'], answer: 'B' },
      { id: 'q2', statement: 'Q2', options: ['A', 'B', 'C', 'D'], answer: 'C' }
    ],
    studentAnswers: ['B', 'A'],
    showOnlyCorrect: true
  });

  assert.equal(view.title, 'Versão A');
  assert.deepEqual(view.items[0].correctAnswer, 'B');
  assert.deepEqual(view.items[0].selectedAnswer, undefined);
  assert.equal(view.items[1].correctAnswer, 'C');
});
