const maxImageSize = 4 * 1024 * 1024;

export function attachCameraCapture({openButton, panel, video, captureButton, retakeButton, closeButton, status, onCapture, onError, isBusy = () => false}) {
  let stream = null, request = 0, disposed = false;
  const stopStream = () => {
    request++;
    if (stream) stream.getTracks().forEach(track => track.stop());
    stream = null;
    video.pause();
    video.srcObject = null;
    video.hidden = true;
  };
  const close = () => {
    stopStream();
    panel.hidden = true;
    openButton.hidden = false;
    status.textContent = '';
  };
  const start = async () => {
    if (disposed || isBusy()) return;
    if (!window.isSecureContext || !navigator.mediaDevices?.getUserMedia) {
      onError('A câmera exige acesso por HTTPS ou localhost e suporte do navegador.');
      return;
    }
    stopStream();
    const current = request;
    panel.hidden = false;
    openButton.hidden = true;
    video.hidden = false;
    captureButton.hidden = false;
    captureButton.disabled = true;
    retakeButton.hidden = true;
    status.textContent = 'Aguardando permissão para acessar a câmera…';
    try {
      const activeStream = await navigator.mediaDevices.getUserMedia({video:{facingMode:{ideal:'environment'}},audio:false});
      if (disposed || current !== request) {
        activeStream.getTracks().forEach(track => track.stop());
        return;
      }
      stream = activeStream;
      video.srcObject = activeStream;
      await video.play();
      if (disposed || current !== request) return;
      captureButton.disabled = false;
      status.textContent = 'Câmera pronta. Posicione a folha e tire a foto.';
    } catch (error) {
      if (current === request) {
        close();
        const message = error.name === 'NotAllowedError' ? 'Permita o acesso à câmera nas configurações do navegador e tente novamente.'
          : error.name === 'NotFoundError' ? 'Nenhuma câmera foi encontrada neste dispositivo.'
          : error.message || 'Não foi possível iniciar a câmera.';
        onError(message);
      }
    }
  };
  openButton.onclick = start;
  retakeButton.onclick = start;
  closeButton.onclick = close;
  captureButton.onclick = () => {
    if (!stream || isBusy()) return;
    const width = video.videoWidth, height = video.videoHeight;
    if (!width || !height) {
      onError('A câmera ainda não está pronta. Aguarde a imagem aparecer e tente novamente.');
      return;
    }
    const canvas = document.createElement('canvas');
    const scale = Math.min(1, 1920 / Math.max(width, height));
    canvas.width = Math.round(width * scale);
    canvas.height = Math.round(height * scale);
    const drawing = canvas.getContext('2d');
    if (!drawing) {
      onError('Não foi possível preparar a foto. Tente novamente.');
      return;
    }
    drawing.drawImage(video, 0, 0, canvas.width, canvas.height);
    const current = request;
    const encode = quality => canvas.toBlob(blob => {
      if (disposed || current !== request) return;
      if (!blob) {
        onError('Não foi possível capturar a foto. Tente novamente.');
        return;
      }
      if (blob.size > maxImageSize && quality > 0.5) {
        encode(quality - 0.12);
        return;
      }
      if (blob.size > maxImageSize) {
        onError('A foto excede o limite de 4 MB. Aproxime a câmera da folha e tente novamente.');
        return;
      }
      const file = new File([blob], 'folha-capturada.jpg', {type:'image/jpeg',lastModified:Date.now()});
      stopStream();
      captureButton.hidden = true;
      retakeButton.hidden = false;
      status.textContent = 'Foto capturada. Você pode refazê-la ou continuar.';
      onCapture(file);
    }, 'image/jpeg', quality);
    encode(0.84);
  };
  return {
    close,
    dispose() {
      disposed = true;
      close();
      openButton.onclick = null;
      retakeButton.onclick = null;
      closeButton.onclick = null;
      captureButton.onclick = null;
    }
  };
}
