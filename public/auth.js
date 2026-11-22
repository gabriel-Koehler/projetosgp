import {
  api
} from './api.js';
const $ = id => document.getElementById(id);
const real = window.APP_CONFIG?.dataMode === 'real';
let mode = 'login';
const password = $('password');
const confirmation = document.querySelector('[name=passwordConfirmation]');

function updatePasswordFeedback() {
  const value = password.value;
  const varieties = [/[a-z]/, /[A-Z]/, /[0-9]/, /[^A-Za-z0-9\s]/]
    .filter(pattern => pattern.test(value)).length;
  let strength = 0;
  if (value) {
    strength = 1;
    if (value.length >= 8 && (varieties >= 2 || value.length >= 12)) strength = 2;
    if (value.length >= 12 && varieties >= 3 && new Set(value).size >= 6) strength = 3;
  }
  $('password-strength').value = strength;
  const label = ['Força da senha', 'Força da senha: fraca', 'Força da senha: média', 'Força da senha: forte'][strength];
  if ($('password-strength-label').textContent !== label) $('password-strength-label').textContent = label;
  confirmation.setCustomValidity(confirmation.value && confirmation.value !== value ? 'As senhas não coincidem.' : '');
}
password.addEventListener('input', updatePasswordFeedback);
confirmation.addEventListener('input', updatePasswordFeedback);
const feedback = message => {
  $('auth-feedback').hidden = false;
  $('auth-feedback').textContent = message;
};

function setMode(next) {
  mode = next;
  const register = mode === 'register',
    recovery = mode === 'recovery';
  $('auth-title').textContent = register ? 'Crie sua conta' : recovery ? 'Recuperar acesso' : 'Entrar na conta';
  $('auth-subtitle').textContent = register ? 'Cadastre-se como professor' :
    recovery ? 'Recuperação simulada no MVP' : 'Acesse sua conta de professor';
  const identifierField = $('identifier-field');
  const identifier = identifierField.querySelector('input');
  identifierField.hidden = register;
  identifier.disabled = register;
  identifier.required = !register;
  identifier.type = recovery ? 'email' : 'text';
  identifier.placeholder = recovery ? 'seu@email.com' : 'Seu usuário ou e-mail';
  identifier.autocomplete = recovery ? 'email' : 'username';
  identifierField.firstChild.textContent = recovery ? 'E-mail' : 'Usuário ou e-mail';
  $('auth-divider').textContent = register ? 'ou crie uma conta com senha' : 'ou entre com sua senha';
  password.minLength = register ? 8 : 0;
  password.placeholder = register ? 'Pelo menos 8 caracteres' : 'Sua senha';
  if (register) password.setAttribute('aria-describedby', 'password-hint');
  else password.removeAttribute('aria-describedby');
  $('password-guidance').hidden = !register;
  $('confirmation-field').hidden = !register;
  confirmation.disabled = !register;
  confirmation.required = register;
  confirmation.value = '';
  updatePasswordFeedback();
  $('recover').hidden = real || register;
  for (const field of ['name-field', 'username-field']) {
    $(field).hidden = !register;
    const input = $(field).querySelector('input');
    input.required = register;
    input.disabled = !register;
  }
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
  $('switch-mode').disabled = true;
  $('recover').disabled = true;
  button.textContent = 'Aguarde…';
  $('auth-feedback').hidden = true;
  try {
    const body = Object.fromEntries(new FormData(event.target));
    if (mode === 'recovery') delete body.password;
    const data = await api('/auth/' + mode, {
      method: 'POST',
      body
    });
    if (mode === 'recovery') feedback(data.message);
    else location.assign('/dashboard');
  } catch (e) {
    feedback(e.message);
  } finally {
    button.disabled = false;
    $('switch-mode').disabled = false;
    $('recover').disabled = false;
    button.textContent = label;
  }
};

setMode('login');
if ($('auth-feedback').textContent) $('auth-feedback').hidden = false;
