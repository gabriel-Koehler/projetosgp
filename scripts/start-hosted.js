import { spawn } from 'node:child_process';

const children = [
  spawn(process.env.PYTHON_BIN || 'python', ['-m', 'uvicorn', 'app.main:app', '--host', '127.0.0.1', '--port', '8000', '--workers', '1'], { stdio: 'inherit', windowsHide: true }),
  spawn(process.execPath, ['server.js'], { stdio: 'inherit', windowsHide: true, env: { ...process.env, HOST: process.env.HOST || '0.0.0.0', API_TARGET: 'http://127.0.0.1:8000' } })
];
let stopping = false;
function stop(code = 0) {
  if (stopping) return;
  stopping = true;
  for (const child of children) child.kill();
  process.exitCode = code;
}
for (const child of children) {
  child.on('error', error => { console.error(error.message); stop(1); });
  child.on('exit', code => stop(code ?? 1));
}
process.on('SIGINT', () => stop());
process.on('SIGTERM', () => stop());
