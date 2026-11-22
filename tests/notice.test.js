import assert from 'node:assert/strict';
import test from 'node:test';
import { createNotice } from '../public/notice.js';

test('notices auto-dismiss, reset their timer when replaced, and can be closed', context => {
  const pending = new Map();
  let nextTimer = 0;
  context.mock.method(globalThis, 'setTimeout', (callback, delay) => {
    assert.equal(delay, 7000);
    const id = ++nextTimer;
    pending.set(id, callback);
    return id;
  });
  context.mock.method(globalThis, 'clearTimeout', id => pending.delete(id));

  const container = {hidden: true};
  const text = {textContent: ''};
  const button = new EventTarget();
  const show = createNotice(container, text, button);

  show('Salvo');
  show('Acesso negado');
  assert.equal(container.hidden, false);
  assert.equal(text.textContent, 'Acesso negado');
  assert.equal(pending.size, 1);
  assert.equal(pending.has(1), false);
  pending.get(2)();
  assert.equal(container.hidden, true);
  assert.equal(text.textContent, '');

  show('Erro');
  button.dispatchEvent(new Event('click'));
  assert.equal(container.hidden, true);
  assert.equal(pending.size, 0);
});
