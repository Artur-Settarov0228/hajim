document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const progressContainer = document.getElementById('progress-container');
    const resultContainer = document.getElementById('result-container');
    const fileNameEl = document.getElementById('file-name');
    const fileStatusEl = document.getElementById('file-status');
    const progressBar = document.getElementById('progress');
    
    const origSizeEl = document.getElementById('orig-size');
    const compSizeEl = document.getElementById('comp-size');
    const savingsEl = document.getElementById('savings');
    const downloadBtn = document.getElementById('download-btn');
    const resetBtn = document.getElementById('reset-btn');

    if (!dropZone) return; // Exit if we are on the home page where there is no drop zone

    // Utility: Format bytes to human readable
    function formatBytes(bytes, decimals = 2) {
        if (!+bytes) return '0 Bytes';
        const k = 1024;
        const dm = decimals < 0 ? 0 : decimals;
        const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return `${parseFloat((bytes / Math.pow(k, i)).toFixed(dm))} ${sizes[i]}`;
    }

    // Drag and Drop Events
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => dropZone.classList.add('dragover'), false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => dropZone.classList.remove('dragover'), false);
    });

    dropZone.addEventListener('drop', handleDrop, false);
    dropZone.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', function() {
        if (this.files.length) handleFiles(this.files);
    });

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        if (files.length) handleFiles(files);
    }

    function handleFiles(files) {
        const file = files[0];
        uploadFile(file);
    }

    function uploadFile(file) {
        // UI Reset
        dropZone.classList.add('hidden');
        resultContainer.classList.add('hidden');
        progressContainer.classList.remove('hidden');
        
        fileNameEl.textContent = file.name;
        fileStatusEl.textContent = "Yuklanmoqda...";
        progressBar.style.width = '0%';
        progressBar.style.background = 'linear-gradient(90deg, var(--primary), #8b5cf6)';

        const formData = new FormData();
        formData.append('file', file);

        const xhr = new XMLHttpRequest();
        xhr.open('POST', '/upload/', true);

        xhr.upload.onprogress = (e) => {
            if (e.lengthComputable) {
                const percent = (e.loaded / e.total) * 100;
                progressBar.style.width = percent + '%';
                if (percent === 100) {
                    fileStatusEl.textContent = "Siqilmoqda... (bu biroz vaqt olishi mumkin)";
                    progressBar.style.background = 'linear-gradient(90deg, var(--highlight), #ef4444)';
                }
            }
        };

        xhr.onload = function() {
            if (xhr.status === 200) {
                const response = JSON.parse(xhr.responseText);
                if (response.success) {
                    showResult(response);
                } else {
                    showError(response.error || "Xatolik yuz berdi");
                }
            } else {
                showError("Server bilan ulanishda xatolik");
            }
        };

        xhr.onerror = function() {
            showError("Tarmoq xatosi");
        };

        xhr.send(formData);
    }

    function showResult(data) {
        progressContainer.classList.add('hidden');
        resultContainer.classList.remove('hidden');

        origSizeEl.textContent = formatBytes(data.original_size);
        compSizeEl.textContent = formatBytes(data.compressed_size);
        savingsEl.textContent = data.savings_percentage + '%';
        
        downloadBtn.href = data.download_url;
        downloadBtn.download = data.filename;
    }

    function showError(msg) {
        fileStatusEl.textContent = "Xatolik: " + msg;
        fileStatusEl.style.color = "var(--highlight)";
        progressBar.style.background = "var(--highlight)";
        
        setTimeout(() => {
            resetUI();
        }, 3000);
    }

    function resetUI() {
        dropZone.classList.remove('hidden');
        progressContainer.classList.add('hidden');
        resultContainer.classList.add('hidden');
        fileInput.value = '';
    }

    resetBtn.addEventListener('click', resetUI);
});
