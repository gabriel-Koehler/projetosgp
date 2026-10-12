import test from 'node:test';
import assert from 'node:assert/strict';
import { backendTarget } from '../backend-target.js';

test('local development keeps local Python', () => {
  assert.equal(backendTarget({}).origin, 'http://127.0.0.1:8000');
});
test('production without binding uses configured public API route', () => {
  assert.deepEqual(backendTarget({VERCEL:'1', VERCEL_ENV:'production', PUBLIC_BASE_URL:'https://example.com/'}), {origin:'https://example.com',publicRoute:true});
});
test('binding is resolved again after injection and takes precedence', () => {
  const env={VERCEL:'1',PUBLIC_BASE_URL:'https://example.com'};
  assert.equal(backendTarget(env).publicRoute,true);
  env.PYTHON_API_URL='https://python.internal';
  assert.equal(backendTarget(env).origin,'https://python.internal');
  assert.equal(backendTarget(env).publicRoute,false);
});
test('preview never falls back to production database endpoint', () => {
  assert.equal(backendTarget({VERCEL:'1',VERCEL_ENV:'preview',VERCEL_URL:'preview.vercel.app',PUBLIC_BASE_URL:'https://production.com'}).origin,'https://preview.vercel.app');
});
test('cloud never silently falls back to localhost', () => {
  assert.throws(()=>backendTarget({VERCEL:'1'}),/API_ORIGIN_MISSING/);
  assert.throws(()=>backendTarget({VERCEL:'1',API_TARGET:'http://127.0.0.1:8000'}),/API_ORIGIN_INVALID/);
});

test('web renders login for API 401 and protects dashboard using public fallback', async () => {
  const {get} = await import('node:http');
  const saved={...process.env}, originalFetch=globalThis.fetch;
  process.env.VERCEL='1';process.env.VERCEL_ENV='production';process.env.PUBLIC_BASE_URL='https://example.com';process.env.DATA_MODE='real';
  delete process.env.PYTHON_API_URL;delete process.env.API_TARGET;
  let received;
  globalThis.fetch=async (url, init)=>{received={url,init};return new Response(JSON.stringify({detail:'Faça login'}),{status:401});};
  let server;
  try {
    const {default:app}=await import('../server.js');
    server=app.listen(0,'127.0.0.1');
    await new Promise(resolve=>server.once('listening',resolve));
    const request=path=>new Promise((resolve,reject)=>get({hostname:'127.0.0.1',port:server.address().port,path,headers:{cookie:'session=test'}},res=>{let body='';res.on('data',c=>body+=c);res.on('end',()=>resolve({status:res.statusCode,body,location:res.headers.location}));}).on('error',reject));
    assert.equal((await request('/')).status,200);
    assert.equal(received.url,'https://example.com/api/auth/me');
    assert.equal(received.init.headers.Cookie,'session=test');
    const dashboard=await request('/dashboard');
    assert.equal(dashboard.status,302);assert.equal(dashboard.location,'/');
    assert.equal((await request('/api/auth/me')).status,503); // prevents recursive proxy
    globalThis.fetch=async()=>{throw new TypeError('network unavailable');};
    assert.equal((await request('/')).status,503);
  } finally {
    if(server)await new Promise(resolve=>server.close(resolve));
    globalThis.fetch=originalFetch;
    for(const key of Object.keys(process.env))if(!(key in saved))delete process.env[key];
    Object.assign(process.env,saved);
  }
});
