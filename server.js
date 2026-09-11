import express from 'express';
import session from 'express-session';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import QRCode from 'qrcode';
import { buildVersions, buildStudentView } from './src/core.js';

const app = express();
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));

app.use(express.urlencoded({ extended: true }));
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));
app.use(session({
  secret: 'n1-evaluation-system',
  resave: false,
  saveUninitialized: false,
  cookie: { maxAge: 60 * 60 * 1000 }
}));

const professorCredentials = { username: 'professor', password: '123456' };

const state = {
  questions: [
    { id: 'Q1', statement: 'Qual linguagem de marcação define a estrutura de uma página web?', options: ['HTML', 'CSS', 'JS', 'SQL'], answer: 'A' },
    { id: 'Q2', statement: 'Qual tecnologia é usada para estilizar a interface?', options: ['HTML', 'CSS', 'Python', 'MySQL'], answer: 'B' },
    { id: 'Q3', statement: 'Qual comando cria uma variável em JavaScript?', options: ['var', 'const', 'let', 'Todas as anteriores'], answer: 'D' },
    { id: 'Q4', statement: 'Qual é o papel principal de um banco de dados?', options: ['Exibir layout', 'Armazenar e consultar dados', 'Executar scripts do navegador', 'Gerar QR Code'], answer: 'B' }
  ],
  versions: []
};

function ensureAuth(req, res, next) {
  if (!req.session.loggedIn) {
    res.redirect('/');
    return;
  }
  next();
}

app.get('/', (req, res) => {
  if (req.session && req.session.loggedIn) {
    res.redirect('/dashboard');
    return;
  }
  res.render('login', { error: null });
});

app.post('/login', (req, res) => {
  const { username, password } = req.body;
  if (username === professorCredentials.username && password === professorCredentials.password) {
    req.session.loggedIn = true;
    req.session.username = username;
    res.redirect('/dashboard');
    return;
  }
  res.render('login', { error: 'Credenciais inválidas.' });
});

app.get('/logout', (req, res) => {
  req.session.destroy(() => {
    res.redirect('/');
  });
});

app.get('/dashboard', ensureAuth, (req, res) => {
  res.render('dashboard', {
    username: req.session.username,
    questions: state.questions,
    versions: state.versions,
    success: null
  });
});

app.post('/questions', ensureAuth, (req, res) => {
  const { statement, optionA, optionB, optionC, optionD, answer } = req.body;
  if (!statement || !optionA || !optionB || !optionC || !optionD || !answer) {
    return res.redirect('/dashboard');
  }

  const options = [optionA, optionB, optionC, optionD];
  const normalizedAnswer = /^[A-D]$/i.test(answer) ? answer.toUpperCase() : answer;

  state.questions.push({
    id: `Q${state.questions.length + 1}`,
    statement,
    options,
    answer: normalizedAnswer
  });

  res.redirect('/dashboard');
});

app.post('/versions', ensureAuth, (req, res) => {
  const { versionCount, naming } = req.body;
  const total = Number(versionCount) || 3;
  const versions = buildVersions({
    questions: state.questions,
    versionCount: total,
    naming: naming || 'A,B,C',
    sameSet: true,
    shuffleQuestions: true,
    shuffleAlternatives: true
  });

  state.versions = versions;
  res.redirect('/dashboard');
});

app.get('/student', async (req, res) => {
  const { version } = req.query;
  const selectedVersion = state.versions.find((item) => item.name === version) || state.versions[0];

  if (!selectedVersion) {
    res.redirect('/dashboard');
    return;
  }

  const view = buildStudentView({
    versionName: selectedVersion.name,
    questions: selectedVersion.questions,
    studentAnswers: Array(selectedVersion.questions.length).fill(undefined),
    showOnlyCorrect: true
  });

  const qr = await QRCode.toDataURL(`versao=${selectedVersion.name}`);
  res.render('student', { view, qr });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Sistema N1 rodando em http://localhost:${PORT}`);
});
