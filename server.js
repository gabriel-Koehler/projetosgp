import express from 'express';
import http from 'node:http';
import https from 'node:https';
import path from 'node:path';
import {
  fileURLToPath
} from 'node:url';

const app = express();
const root = path.dirname(fileURLToPath(import.meta.url));
const backend = (process.env.API_TARGET || 'http://127.0.0.1:8000').replace(/\/$/, '');
const dataMode = process.env.DATA_MODE === 'real' ? 'real' : 'mock';
app.set('view engine', 'ejs');
app.set('views', path.join(root, 'views'));
app.use(express.static(path.join(root, 'public')));

// Same-origin proxy: the browser only talks to /api, including session cookies.
// Keep the request streaming so methods, query strings and bodies are preserved.
app.use('/api', (req, res) => {
  const target = new URL(req.originalUrl, backend);
  const transport = target.protocol === 'https:' ? https : http;
  const upstream = transport.request(target, {
    method: req.method,
    headers: {
      ...req.headers,
      host: target.host,
      'x-forwarded-host': req.get('host'),
      'x-forwarded-proto': req.protocol
    },
    timeout: 12000
  }, response => {
    res.writeHead(response.statusCode, response.headers);
    response.pipe(res);
    response.on('error', () => res.destroy());
  });
  upstream.on('timeout', () => upstream.destroy(new Error('API timeout')));
  upstream.on('error', () => {
    if (!res.headersSent) res.status(502).json({
      error: {
        message: 'API indisponível. Verifique se o serviço Python está rodando e tente novamente.'
      }
    });
    else res.destroy();
  });
  req.on('aborted', () => upstream.destroy());
  req.pipe(upstream);
});

app.get('/config.js', (req, res) => res.type('application/javascript').send('window.APP_CONFIG = ' + JSON.stringify({apiBaseUrl:'/api',dataMode}) + ';'));
async function sessionUser(req) {
  try {
    const response = await fetch(backend + '/api/auth/me', {
      headers: {
        Cookie: req.headers.cookie || ''
      },
      signal: AbortSignal.timeout(4000)
    });
    if (response.status === 401) return null;
    if (!response.ok) throw new Error('API unavailable');
    const payload = await response.json();
    return dataMode === 'real' ? {name:payload.nome} : payload.data;
  } catch {
    throw new Error("Serviço indisponível");
  }
}
const pageRoute = handler => (req,res) => Promise.resolve(handler(req,res)).catch(()=>res.status(503).render('unavailable'));
app.get('/', pageRoute(async (req, res) => (await sessionUser(req)) ? res.redirect('/dashboard') : res.render('login')));
app.get('/dashboard', pageRoute(async (req, res) => {
  const user = await sessionUser(req);
  if (!user) return res.redirect('/');
  res.render('dashboard', {
    username: user.name
  });
}));
app.get('/print', pageRoute(async (req, res) => {
  if (!(await sessionUser(req))) return res.redirect('/');
  res.render('print');
}));
app.get('/student', (req, res) => res.render('student'));
const port = process.env.PORT || 3000;
app.get('/health', async (req, res) => {
  try {
    const response = await fetch(backend + '/health', { signal: AbortSignal.timeout(4000) });
    if (!response.ok) return res.status(503).json({ status: 'unavailable' });
    res.json({ status: 'ok', api: await response.json() });
  } catch {
    res.status(503).json({ status: 'unavailable' });
  }
});
app.listen(port, process.env.HOST || '127.0.0.1', () => console.log('AvaliaSystem em http://localhost:' + port + ' → API Python ' + backend));
