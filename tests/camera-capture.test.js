import test from 'node:test';
import assert from 'node:assert/strict';
import {attachCameraCapture} from '../public/camera-capture.js';

const setGlobals = values => {
  const previous = Object.fromEntries(Object.keys(values).map(name => [name, Object.getOwnPropertyDescriptor(globalThis, name)]));
  for (const [name, value] of Object.entries(values)) Object.defineProperty(globalThis, name, {configurable:true,writable:true,value});
  return () => {
    for (const [name, descriptor] of Object.entries(previous)) {
      if (descriptor) Object.defineProperty(globalThis, name, descriptor);
      else delete globalThis[name];
    }
  };
};

const makeCaptureControls = () => ({
  openButton:{hidden:false}, panel:{hidden:true}, video:{hidden:true,videoWidth:1200,videoHeight:800,pause(){},play:async()=>{}},
  captureButton:{hidden:false,disabled:false}, retakeButton:{hidden:true}, closeButton:{}, status:{textContent:''}
});

test('camera capture prefers the rear camera, emits a JPEG and releases the stream',async()=>{
  let constraints, stopped = 0, captured;
  const stream = {getTracks:()=>[{stop:()=>stopped++}]};
  const restore = setGlobals({
    window:{isSecureContext:true},
    navigator:{mediaDevices:{getUserMedia:async options => {constraints=options;return stream;}}},
    document:{createElement:()=>({width:0,height:0,getContext:()=>({drawImage(){}}),toBlob:callback=>callback(new Blob(['photo'],{type:'image/jpeg'}))})}
  });
  try {
    const controls = makeCaptureControls();
    const camera = attachCameraCapture({...controls,onCapture:file=>captured=file,onError:message=>assert.fail(message)});
    await controls.openButton.onclick();
    assert.deepEqual(constraints.video.facingMode,{ideal:'environment'});
    assert.equal(controls.captureButton.disabled,false);
    controls.captureButton.onclick();
    assert.equal(captured.type,'image/jpeg');
    assert.equal(captured.name,'folha-capturada.jpg');
    assert.equal(stopped,1);
    assert.equal(controls.retakeButton.hidden,false);
    camera.dispose();
  } finally {restore();}
});

test('camera access is stopped if the correction screen closes while permission is pending',async()=>{
  let resolveStream, stopped = 0, captures = 0;
  const restore = setGlobals({
    window:{isSecureContext:true},
    navigator:{mediaDevices:{getUserMedia:()=>new Promise(resolve=>{resolveStream=resolve;})}},
    document:{createElement:()=>assert.fail('No photo should be captured')}
  });
  try {
    const controls = makeCaptureControls();
    const camera = attachCameraCapture({...controls,onCapture:()=>captures++,onError:message=>assert.fail(message)});
    const starting = controls.openButton.onclick();
    camera.dispose();
    resolveStream({getTracks:()=>[{stop:()=>stopped++}]});
    await starting;
    assert.equal(stopped,1);
    assert.equal(captures,0);
  } finally {restore();}
});
