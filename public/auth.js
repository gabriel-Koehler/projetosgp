import {
  api
} from './api.js';
const $ = id => document.getElementById(id);
const real = window.APP_CONFIG?.dataMode === 'real';
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
  $('auth-subtitle').textContent = register ? 'Cadastre-se como professor' :
    recovery ? 'Recuperação simulada no MVP' : 'Acesse sua conta de professor';
  const email = document.querySelector('[name=email]');
  email.type = real && !register ? 'text' : 'email';
  email.placeholder = real && !register ? 'Seu usuário ou e-mail' : 'seu@email.com';
  email.autocomplete = register ? 'email' : 'username';
  email.parentElement.firstChild.textContent = real && !register ? 'Usuário ou e-mail' : 'E-mail';
  $('password').minLength = register && real ? 8 : 0;
  $('password').placeholder = register && real ? 'Pelo menos 8 caracteres' : 'Sua senha';
  $('recover').hidden = real || register;
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
$('google').onclick = () => location.assign('/api/auth/google');
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
    if (mode !== 'register') delete body.name;
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
if (real) {
  api('/auth/options').then(({google}) => {
    $('google').hidden = !google;
    document.querySelector('.divider').hidden = !google;
  }).catch(() => {});
}
const params = new URLSearchParams(location.search);
if (params.has('expired')) feedback('Sua sessão expirou. Entre novamente.');
if (params.has('google')) {
  feedback(params.get('google') === 'unavailable'
    ? 'O acesso com Google está indisponível.'
    : 'Não foi possível entrar com o Google. Tente novamente.');
}
