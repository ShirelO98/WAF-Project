const form = document.getElementById('contact-form');
const logBox = document.getElementById('log-box');
const logContent = document.getElementById('log-content');

form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const formData = new FormData(form);
    const data = new URLSearchParams();
    for (const pair of formData) {
        data.append(pair[0], pair[1]);
    }

    const requestBody = data.toString();

    try {
        const response = await fetch("http://localhost:5000/submit", {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded"
            },
            body: requestBody
        });

        const resultText = await response.text();

        logContent.innerHTML = `
            <p><strong>Status:</strong> <span class="${response.ok ? 'success' : 'error'}">${response.status}</span></p>
            <p><strong>Request:</strong> ${requestBody}</p>
            <p><strong>Response:</strong> ${resultText}</p>
        `;
        logBox.style.display = "block";
    } catch (err) {
        logContent.innerHTML = `
            <p><strong>Status:</strong> <span class="error">Network Error</span></p>
            <p><strong>Details:</strong> ${err}</p>
        `;
        logBox.style.display = "block";
    }
});
