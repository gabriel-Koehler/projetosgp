import express from 'express';
import {
  randomUUID,
  scryptSync,
  timingSafeEqual
} from 'node:crypto';
import QRCode from 'qrcode';
import {
  buildVersions
} from './core.js';

const hash = value => scryptSync(value, 'avali mock only', 64);
const userView = u => ({
  id: u.id,
  name: u.name,
  email: u.email
});
export function createMockApi() {
  const router = express.Router();
  const users = [{
    id: 'professor',
    name: 'Prof. Dr. Carlos Silva',
    email: 'professor@avaliasystem.com',
    password: hash('123456')
  }];
  const initial = () => ({
    semesters: [{
      id: 's1',
      name: '2026.1',
      active: true
    }, {
      id: 's2',
      name: '2025.2',
      active: false
    }],
    classes: [{
      id: 'c1',
      semesterId: 's1',
      name: 'Direito Civil I',
      code: 'DC-2026A'
    }, {
      id: 'c2',
      semesterId: 's1',
      name: 'Direito Constitucional',
      code: 'DCON-2026A'
    }],
    students: [{
      id: 'a1',
      classId: 'c1',
      name: 'Ana Clara Ferreira',
      registration: '2024001'
    }, {
      id: 'a2',
      classId: 'c1',
      name: 'Bruno Alves Costa',
      registration: '2024002'
    }],
    questions: [{
      id: 'Q-047',
      subject: 'Direito Civil',
      difficulty: 'Médio',
      statement: 'Qual dos seguintes elementos é essencial para a validade de um contrato conforme o Código Civil Brasileiro?',
      options: ['Forma escrita', 'Agente capaz, objeto lícito e forma prescrita ou não defesa em lei', 'Testemunhas', 'Registro em cartório'],
      answer: 'B'
    }, {
      id: 'Q-046',
      subject: 'Direito Civil',
      difficulty: 'Fácil',
      statement: 'O que caracteriza a obrigação de dar coisa certa no Direito Civil?',
      options: ['Entrega de coisa individuada e determinada', 'Entrega de qualquer bem fungível', 'Prestação de serviço específico', 'Pagamento em dinheiro'],
      answer: 'A'
    }],
    evaluations: [],
    results: []
  });
  const stores = new Map();
  const fail = (res, message, status = 400) => res.status(status).json({
    error: {
      message
    }
  });
  const text = (v, max = 200) => typeof v === 'string' && v.trim().length > 0 && v.trim().length <= max;

  function signIn(req, res, user) {
    req.session.regenerate(error => {
      if (error) return fail(res, 'Não foi possível iniciar a sessão.', 500);
      req.session.userId = user.id;
      req.session.loggedIn = true;
      req.session.username = user.name;
      req.session.save(error => error ? fail(res, 'Não foi possível salvar a sessão.', 500) : res.json({
        data: userView(user)
      }));
    });
  }
  router.post('/auth/login', (req, res) => {
    const {
      email,
      password
    } = req.body;
    const user = users.find(u => u.email === String(email).trim().toLowerCase() || (email === 'professor' && u.id === 'professor'));
    if (!text(password, 128) || !user || !timingSafeEqual(user.password, hash(password))) return fail(res, 'E-mail ou senha inválidos.', 401);
    signIn(req, res, user);
  });
  router.post('/auth/register', (req, res) => {
    const {
      name,
      email,
      password
    } = req.body;
    if (!text(name, 100) || !text(email) || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email) || !text(password, 128) || password.length < 6) return fail(res, 'Informe nome, e-mail válido e senha com pelo menos 6 caracteres.');
    if (users.some(u => u.email === email.trim().toLowerCase())) return fail(res, 'Já existe uma conta com esse e-mail.', 409);
    const user = {
      id: randomUUID(),
      name: name.trim(),
      email: email.trim().toLowerCase(),
      password: hash(password)
    };
    users.push(user);
    signIn(req, res, user);
  });
  router.post('/auth/recovery', (req, res) => {
    if (!text(req.body.email) || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(req.body.email)) return fail(res, 'Informe um e-mail válido.');
    res.json({
      data: {
        message: 'Solicitação simulada. Este MVP não envia e-mails; use a conta de demonstração ou crie uma conta.'
      }
    });
  });
  router.post('/auth/logout', (req, res) => req.session.destroy(error => error ? fail(res, 'Não foi possível sair.', 500) : res.clearCookie('connect.sid').json({
    data: null
  })));
  router.use((req, res, next) => {
    const user = users.find(u => u.id === req.session.userId);
    if (!user) return fail(res, 'Sua sessão expirou. Entre novamente.', 401);
    req.user = user;
    if (!stores.has(user.id)) stores.set(user.id, initial());
    req.store = stores.get(user.id);
    next();
  });
  router.get('/auth/me', (req, res) => res.json({
    data: userView(req.user)
  }));
  router.get('/workspace', (req, res) => res.json({
    data: req.store
  }));
  for (const collection of ['semesters', 'classes', 'students', 'questions', 'evaluations', 'results']) router.get('/' + collection, (req, res) => res.json({
    data: req.store[collection]
  }));
  for (const collection of ['semesters', 'classes', 'students', 'questions']) {
    router.post('/' + collection, (req, res) => {
      const b = req.body,
        s = req.store;
      let item;
      if (collection === 'semesters' && text(b.name, 30)) item = {
        name: b.name.trim(),
        active: false
      };
      if (collection === 'classes' && text(b.name) && text(b.code, 30) && s.semesters.some(x => x.id === b.semesterId)) item = {
        name: b.name.trim(),
        code: b.code.trim(),
        semesterId: b.semesterId
      };
      if (collection === 'students' && text(b.name) && text(b.registration, 30) && s.classes.some(x => x.id === b.classId)) {
        if (s.students.some(x => x.registration === b.registration.trim())) return fail(res, 'Matrícula já cadastrada.', 409);
        item = {
          name: b.name.trim(),
          registration: b.registration.trim(),
          classId: b.classId
        };
      }
      if (collection === 'questions' && text(b.statement, 2000) && text(b.subject, 100) && ['Fácil', 'Médio', 'Difícil'].includes(b.difficulty) && Array.isArray(b.options) && b.options.length === 4 && b.options.every(x => text(x, 500)) && /^[A-D]$/.test(b.answer)) item = {
        statement: b.statement.trim(),
        subject: b.subject.trim(),
        difficulty: b.difficulty,
        options: b.options.map(x => x.trim()),
        answer: b.answer
      };
      if (!item) return fail(res, 'Preencha os campos obrigatórios com valores válidos.');
      item.id = randomUUID();
      s[collection].push(item);
      res.status(201).json({
        data: item
      });
    });
  }
  router.delete('/questions/:id', (req, res) => {
    const index = req.store.questions.findIndex(q => q.id === req.params.id);
    if (index < 0) return fail(res, 'Questão não encontrada.', 404);
    req.store.questions.splice(index, 1);
    res.json({
      data: null
    });
  });
  router.post('/evaluations', (req, res) => {
    const b = req.body,
      s = req.store;
    if (!text(b.name) || !s.classes.some(x => x.id === b.classId) || !Array.isArray(b.questionIds) || !b.questionIds.length || new Set(b.questionIds).size !== b.questionIds.length || !Number.isInteger(b.versionCount) || b.versionCount < 1 || b.versionCount > 5) return fail(res, 'Informe nome, turma, questões e entre 1 e 5 versões.');
    const questions = b.questionIds.map(id => s.questions.find(q => q.id === id));
    if (questions.some(q => !q)) return fail(res, 'Uma questão selecionada não existe mais.');
    const item = {
      id: randomUUID(),
      name: b.name.trim(),
      classId: b.classId,
      createdAt: new Date().toISOString(),
      versions: buildVersions({
        questions,
        versionCount: b.versionCount,
        naming: 'A,B,C,D,E',
        shuffleQuestions: b.shuffleQuestions === true,
        shuffleAlternatives: b.shuffleAlternatives === true
      })
    };
    s.evaluations.push(item);
    res.status(201).json({
      data: item
    });
  });
  router.get('/evaluations/:id/qr/:version', async (req, res, next) => {
    try {
      const evaluation = req.store.evaluations.find(e => e.id === req.params.id);
      if (!evaluation?.versions.some(v => v.name === req.params.version)) return fail(res, 'Versão não encontrada.', 404);
      const payload = JSON.stringify({
        evaluationId: evaluation.id,
        version: req.params.version
      });
      res.json({
        data: {
          image: await QRCode.toDataURL(payload),
          payload
        }
      });
    } catch (e) {
      next(e);
    }
  });
  router.post('/results', (req, res) => {
    const b = req.body,
      s = req.store,
      evaluation = s.evaluations.find(e => e.id === b.evaluationId);
    const version = evaluation?.versions.find(v => v.name === b.version);
    if (!version || !s.students.some(a => a.id === b.studentId && a.classId === evaluation.classId) || !Array.isArray(b.answers) || b.answers.length !== version.questions.length || !b.answers.every(a => /^[A-D]$/.test(a))) return fail(res, 'Selecione avaliação, versão, aluno da turma e todas as respostas.');
    if (s.results.some(r => r.evaluationId === b.evaluationId && r.studentId === b.studentId)) return fail(res, 'Este aluno já possui resultado nesta avaliação.', 409);
    const correct = version.questions.reduce((n, q, i) => n + Number(q.answerLetter === b.answers[i]), 0);
    const item = {
      id: randomUUID(),
      evaluationId: b.evaluationId,
      studentId: b.studentId,
      version: b.version,
      answers: b.answers,
      correct,
      total: version.questions.length,
      grade: Math.round(correct / version.questions.length * 100) / 10,
      createdAt: new Date().toISOString()
    };
    s.results.push(item);
    res.status(201).json({
      data: item
    });
  });
  router.use((req, res) => fail(res, 'Rota não encontrada.', 404));
  return router;
}
