import {
  api
} from './api.js';
const $ = id => document.getElementById(id);
let mode = 'login';
const feedback = message => {
  $('auth-feedback').hidden = false;
  $('auth-feedback').textContent = message;
};

function setMode(next) {
  mode = next;
  const register = mode === 'register',
    recovery = mode === 'recovery';
  $('auth-title').textContent = register ? 'Crie sua conta' : recovery ? 'Recuperar acesso' : 'Entrar na conta';
  $('auth-subtitle').textContent = recovery ? 'Recuperação simulada no MVP' : 'Acesse sua conta de professor';
  $('name-field').hidden = !register;
  $('name-field').querySelector('input').required = register;
  $('password-field').hidden = recovery;
  $('password').required = !recovery;
  $('password').autocomplete = register ? 'new-password' : 'current-password';
  $('submit-auth').textContent = register ? 'Criar conta' : recovery ? 'Solicitar recuperação' : 'Entrar';
  $('switch-label').textContent = mode === 'login' ? 'Não tem uma conta?' : 'Já tem uma conta?';
  $('switch-mode').textContent = mode === 'login' ? 'Crie uma!' : 'Entrar';
  $('auth-feedback').hidden = true;
}
$('switch-mode').onclick = () => setMode(mode === 'login' ? 'register' : 'login');
$('recover').onclick = () => setMode('recovery');
$('google').onclick = () => feedback('Login com Google não está conectado neste MVP. Use o acesso de demonstração ou crie uma conta.');
$('toggle-password').onclick = () => {
  const show = $('password').type === 'password';
  $('password').type = show ? 'text' : 'password';
  $('toggle-password').textContent = show ? 'Ocultar' : 'Mostrar';
  $('toggle-password').setAttribute('aria-pressed', String(show));
};
$('auth-form').onsubmit = async event => {
  event.preventDefault();
  const button = $('submit-auth'),
    label = button.textContent;
  button.disabled = true;
  button.textContent = 'Aguarde…';
  $('auth-feedback').hidden = true;
  try {
    const data = await api('/auth/' + mode, {
      method: 'POST',
      body: Object.fromEntries(new FormData(event.target))
    });
    if (mode === 'recovery') feedback(data.message);
    else location.assign('/dashboard');
  } catch (e) {
    feedback(e.message);
  } finally {
    button.disabled = false;
    button.textContent = label;
  }
};
