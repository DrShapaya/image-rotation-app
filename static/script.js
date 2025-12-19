async function refreshCaptcha() {
    try {
        const response = await fetch('/');
        const text = await response.text();
        const parser = new DOMParser();
        const doc = parser.parseFromString(text, 'text/html');
        const newCaptcha = doc.getElementById('captchaImage').src;
        const newSessionId = doc.getElementById('session_id').value;

        document.getElementById('captchaImage').src = newCaptcha;
        document.getElementById('session_id').value = newSessionId;
        document.getElementById('captcha').value = '';
    } catch (error) {
        console.error('Error refreshing CAPTCHA:', error);
    }
}

async function displayHistogram(canvasId, histogramData) {
    const ctx = document.getElementById(canvasId).getContext('2d');

    // Создаем изображение из base64
    const img = new Image();
    img.src = 'data:image/png;base64,' + histogramData;

    img.onload = function() {
        ctx.drawImage(img, 0, 0, 1100, 800);
    };
}

document.getElementById('uploadForm').addEventListener('submit', async function(e) {
    e.preventDefault();

    const formData = new FormData(this);

    try {
        const response = await fetch('/process', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (response.ok) {
            // Отображаем результаты
            document.getElementById('rotatedImage').src = result.rotated_image;
            document.getElementById('angleValue').textContent = result.angle;
            document.getElementById('classificationResult').textContent =
                `Класс: ${result.classification}`;

            // Отображаем гистограммы
            await displayHistogram('originalHistogram', result.original_histogram);

            document.getElementById('results').style.display = 'block';
            document.getElementById('error').style.display = 'none';

            // Обновляем капчу
            await refreshCaptcha();
        } else {
            throw new Error(result.error || 'Ошибка обработки');
        }
    } catch (error) {
        document.getElementById('error').textContent = 'Ошибка: ' + error.message;
        document.getElementById('error').style.display = 'block';
        document.getElementById('results').style.display = 'none';

        // Обновляем капчу при ошибке
        await refreshCaptcha();
    }
});