import {
  api
} from './api.js';
const $ = id => document.getElementById(id);
const real = window.APP_CONFIG?.dataMode === 'real';
let mode = 'login';
const password = $('password');
const confirmation = document.querySelector('[name=passwordConfirmation]');
const code = document.querySelector('[name=code]');

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
  const register = mode === 'register';
  const verify = mode === 'confirm-email';
  const showPassword = register || mode === 'login';
  $('auth-title').textContent = ({
    register: 'Crie sua conta', 'confirm-email': 'Confirme seu e-mail', recovery: 'Recuperar acesso'
  })[mode] || 'Entrar na conta';
  $('auth-subtitle').textContent = ({
    register: 'Cadastre-se como professor',
    'confirm-email': 'Informe o código enviado para a sua caixa de entrada',
    recovery: 'Recuperação simulada no MVP'
  })[mode] || 'Acesse sua conta de professor';
  $('email-code-field').hidden = !verify;
  code.disabled = !verify;
  code.required = verify;
  code.value = '';
  $('resume-verification').hidden = !real || !register;
  const email = document.querySelector('[name=email]');
  email.type = mode === 'login' ? 'text' : 'email';
  email.placeholder = mode === 'login' ? 'Seu usuário ou e-mail' : 'seu@email.com';
  email.autocomplete = mode === 'login' ? 'username' : 'email';
  email.parentElement.firstChild.textContent = mode === 'login' ? 'Usuário ou e-mail' : 'E-mail';
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
  $('password-field').hidden = !showPassword;
  password.disabled = !showPassword;
  password.required = showPassword;
  password.autocomplete = register ? 'new-password' : 'current-password';
  $('submit-auth').textContent = ({
    register: 'Criar conta', 'confirm-email': 'Confirmar e-mail', recovery: 'Solicitar recuperação'
  })[mode] || 'Entrar';
  $('switch-label').textContent = mode === 'login' ? 'Não tem uma conta?' :
    verify ? 'Precisa de outro código?' : 'Já tem uma conta?';
  $('switch-mode').textContent = mode === 'login' ? 'Crie uma!' : verify ? 'Voltar ao cadastro' : 'Entrar';
  $('auth-feedback').hidden = true;
}
$('switch-mode').onclick = () => setMode(['login', 'confirm-email'].includes(mode) ? 'register' : 'login');
$('resume-verification').onclick = () => {
  setMode('confirm-email');
  code.focus();
};
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
  $('resume-verification').disabled = true;
  button.textContent = 'Aguarde…';
  $('auth-feedback').hidden = true;
  try {
    const body = Object.fromEntries(new FormData(event.target));
    const data = await api('/auth/' + mode, {
      method: 'POST',
      body
    });
    if (mode === 'register' && real) {
      password.value = '';
      setMode('confirm-email');
      feedback(data.message);
      code.focus();
    } else if (mode === 'recovery') {
      feedback(data.message);
    } else {
      location.assign('/dashboard');
    }
  } catch (e) {
    feedback(e.message);
  } finally {
    button.disabled = false;
    $('switch-mode').disabled = false;
    $('recover').disabled = false;
    $('resume-verification').disabled = false;
    if (button.textContent === 'Aguarde…') button.textContent = label;
  }
};

setMode('login');
if ($('auth-feedback').textContent) $('auth-feedback').hidden = false;
