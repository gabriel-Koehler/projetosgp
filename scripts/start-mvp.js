import {
  spawn
} from 'node:child_process';
import {
  existsSync
} from 'node:fs';
import path from 'node:path';
import {
  fileURLToPath
} from 'node:url';
const root = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const envFile = path.join(root, '.env');
if (existsSync(envFile)) process.loadEnvFile(envFile);
const localPython = path.join(root, '.venv', process.platform === 'win32' ? 'Scripts/python.exe' : 'bin/python');
const python = existsSync(localPython) ? localPython : (process.platform === 'win32' ? 'python' : 'python3');
const real = process.argv.includes('--real');
const env = {...process.env, DATA_MODE:real?'real':'mock', API_TARGET:process.env.API_TARGET || 'http://127.0.0.1:'+(process.env.API_PORT || '8000')};
const children = [
  spawn(python, ['-m', 'uvicorn', ...(real?['app.persistent:create_app','--factory']:['app.main:app']), '--host', '127.0.0.1', '--port', process.env.API_PORT || '8000'], {
    cwd: root,
    env,
    stdio: 'inherit',
    windowsHide: true
  }),
  spawn(process.execPath, ['--preserve-symlinks', '--preserve-symlinks-main', 'server.js'], {
    cwd: root,
    env,
    stdio: 'inherit',
    windowsHide: true
  })
];
let stopping = false;

function stop(code = 0) {
  if (stopping) return;
  stopping = true;
  for (const child of children) child.kill();
  process.exitCode = code;
}
for (const child of children) {
  child.on('error', error => {
    console.error(error.message);
    stop(1);
  });
  child.on('exit', code => stop(code || 0));
}
process.on('SIGINT', () => stop());
process.on('SIGTERM', () => stop());
