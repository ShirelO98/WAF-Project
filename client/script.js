document.addEventListener('DOMContentLoaded', () => {
  const form       = document.getElementById('contact-form');
  const logBox     = document.getElementById('log-box');
  const logContent = document.getElementById('log-content');
  const saved = sessionStorage.getItem('lastResponse');
  if (saved) {
    const { status, ok, text } = JSON.parse(saved);
    logContent.innerHTML = `
      <p><strong>Status:</strong>
         <span class="${ok ? 'success' : 'error'}">${status}</span>
      </p>
      <p><strong>Response:</strong> ${text}</p>
    `;
    logBox.style.display = 'block';
    sessionStorage.removeItem('lastResponse');
  }

  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const formData = new FormData(form);

    try {
      const response = await fetch("http://localhost:5000/submit", {
        method: "POST",
        body: formData
      });
      const text = await response.text();

      sessionStorage.setItem('lastResponse', JSON.stringify({
        status:  response.status,
        ok:      response.ok,
        text
      }));
    } catch (err) {
      sessionStorage.setItem('lastResponse', JSON.stringify({
        status:  'Network Error',
        ok:      false,
        text:    err.toString()
      }));
    }

    window.location.reload();
  });
});
