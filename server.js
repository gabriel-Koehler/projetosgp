import express from 'express';
import session from 'express-session';
import path from 'node:path';
import {
  fileURLToPath
} from 'node:url';
import {
  createMockApi
} from './src/mock-api.js';

const app = express();
const root = path.dirname(fileURLToPath(import.meta.url));
app.set('view engine', 'ejs');
app.set('views', path.join(root, 'views'));
app.use(express.json({
  limit: '100kb'
}));
app.use(express.static(path.join(root, 'public')));
app.use(session({
  secret: process.env.SESSION_SECRET || 'local-demo-only-change-for-production',
  resave: false,
  saveUninitialized: false,
  cookie: {
    maxAge: 60 * 60 * 1000,
    httpOnly: true,
    sameSite: 'lax'
  }
}));
app.use('/api', createMockApi());
app.get('/config.js', (req, res) => res.type('application/javascript').send(
  'window.APP_CONFIG = ' + JSON.stringify({
    apiBaseUrl: process.env.API_BASE_URL || '/api'
  }) + ';'
));
app.get('/', (req, res) => req.session.userId ? res.redirect('/dashboard') : res.render('login'));
app.get('/dashboard', (req, res) => req.session.userId ? res.render('dashboard', {
  username: req.session.username
}) : res.redirect('/'));
app.use((error, req, res, next) => {
  console.error(error.message);
  res.status(error.status === 400 ? 400 : 500).json({
    error: {
      message: error.status === 400 ? 'JSON inválido.' : 'Erro inesperado. Tente novamente.'
    }
  });
});
const port = process.env.PORT || 3000;
app.listen(port, '127.0.0.1', () => console.log('AvaliaSystem em http://localhost:' + port));
