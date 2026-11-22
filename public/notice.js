const DISPLAY_TIME_MS = 7000;

export function createNotice(container, text, dismissButton) {
  let timeout;

  function dismiss() {
    clearTimeout(timeout);
    container.hidden = true;
    text.textContent = '';
  }

  dismissButton.addEventListener('click', dismiss);

  return function show(message) {
    clearTimeout(timeout);
    container.hidden = false;
    text.textContent = message;
    timeout = setTimeout(dismiss, DISPLAY_TIME_MS);
  };
}
