document.addEventListener('DOMContentLoaded', () => {
    const userIdInput = document.getElementById('user-id');
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const selectFileBtn = document.getElementById('select-file');
    const checkFileBtn = document.getElementById('check-file');
    const checkTextBtn = document.getElementById('check-text');
    const textInput = document.getElementById('text-input');
    const resultSection = document.querySelector('.result-section');
    const statusIndicator = document.querySelector('.status-indicator');
    const resultText = document.querySelector('.result-text');

    // Обработка drag and drop
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => {
            dropZone.classList.add('drag-over');
        });
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => {
            dropZone.classList.remove('drag-over');
        });
    });

    dropZone.addEventListener('drop', handleDrop);
    selectFileBtn.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', handleFileSelect);
    checkFileBtn.addEventListener('click', handleFileUpload);
    checkTextBtn.addEventListener('click', handleTextCheck);

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const file = dt.files[0];
        handleFile(file);
    }

    function handleFileSelect(e) {
        const file = e.target.files[0];
        handleFile(file);
    }

    function handleFile(file) {
        if (!file) return;

        const validTypes = [
            'image/png', 'image/jpeg', 'text/plain',
            'application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        ];

        if (!validTypes.includes(file.type)) {
            showResult(false, 'Неподдерживаемый тип файла');
            return;
        }

        dropZone.querySelector('.drop-zone-text').textContent = `Выбран файл: ${file.name}`;
        checkFileBtn.disabled = false;
    }

    // Добавляем валидацию для user ID
    userIdInput.addEventListener('input', (e) => {
        e.target.value = e.target.value.replace(/[^0-9]/g, '').slice(0, 7);
    });

    async function handleFileUpload() {
        const file = fileInput.files[0];
        const userId = userIdInput.value.trim();
        
        if (!file) return;
        if (!userId || userId.length !== 7) {
            showResult(false, 'Пожалуйста, введите 7-значный ID пользователя');
            return;
        }

        const formData = new FormData();
        formData.append('file', file);
        formData.append('user_id', userId);

        try {
            const response = await fetch('/upload-file/', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();
            const isSuccess = result.success; 
            const messageText = result.message && result.message.text ? result.message.text : result.processed_text;
            showResult(isSuccess, messageText);
        } catch (error) {
            showResult(false, 'Ошибка при проверке файла');
        }
    }

    async function handleTextCheck() {
        const text = textInput.value.trim();
        const userId = userIdInput.value.trim();
        
        if (!text) return;
        if (!userId || userId.length !== 7) {
            showResult(false, 'Пожалуйста, введите 7-значный ID пользователя');
            return;
        }

        try {
            const response = await fetch('/process-text/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    text: text,
                    user_id: userId
                })
            });

            const result = await response.json();
            const isSuccess = !result.success; // Invert the success flag
            const messageText = result.message && result.message.text ? result.message.text : result.processed_text;
            showResult(isSuccess, messageText);
        } catch (error) {
            showResult(false, 'Ошибка при проверке текста');
        }
    }

    function showResult(isConfidential, message) {
        resultSection.style.display = 'block';
        // Если текст конфиденциальный (true) - красный, если нет (false) - зеленый
        statusIndicator.className = 'status-indicator ' + (isConfidential ? 'success' : 'error');
        
        const resultStatus = document.querySelector('.result-status');
        resultStatus.textContent = isConfidential ? 'Запрос прошел проверку' : 'Запрос не прошел проверку';
        resultStatus.className = 'result-status ' + (isConfidential ? 'success-text' : 'error-text');
        
        resultText.textContent = message || 'Нет сообщения';
    }
});