/**
 * df_ocr frontend: upload, progress, preview, download.
 */
(function () {
    'use strict';

    // ── DOM refs ──────────────────────────────────────────────
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    const browseBtn = document.getElementById('browseBtn');
    const fileList = document.getElementById('fileList');
    const fileCount = document.getElementById('fileCount');
    const fileItems = document.getElementById('fileItems');
    const clearBtn = document.getElementById('clearBtn');
    const convertBtn = document.getElementById('convertBtn');
    const progressArea = document.getElementById('progressArea');
    const progressBar = document.getElementById('progressBar');
    const progressText = document.getElementById('progressText');
    const resultsSection = document.getElementById('resultsSection');
    const resultCards = document.getElementById('resultCards');
    const downloadAllBtn = document.getElementById('downloadAllBtn');
    const errorArea = document.getElementById('errorArea');

    // ── State ──────────────────────────────────────────────────
    const MAX_FILES = 10;
    const MAX_SIZE = 50 * 1024 * 1024; // 50 MB
    let selectedFiles = [];
    /** @type {{taskId: string, filename: string, status: string, markdown?: string, error?: string}[]} */
    let results = [];

    // ── File selection ─────────────────────────────────────────
    function updateFileListUI() {
        fileCount.textContent = selectedFiles.length;
        fileItems.innerHTML = '';
        selectedFiles.forEach((f, i) => {
            const li = document.createElement('li');
            li.innerHTML = `
                <span class="filename" title="${escapeHtml(f.name)}">${escapeHtml(f.name)}</span>
                <span class="filesize">${formatSize(f.size)}</span>
                <button class="remove-btn" data-index="${i}" title="移除">✕</button>
            `;
            fileItems.appendChild(li);
        });
        if (selectedFiles.length > 0) {
            fileList.classList.remove('hidden');
            dropZone.classList.add('hidden');
        } else {
            fileList.classList.add('hidden');
            dropZone.classList.remove('hidden');
        }
    }

    function addFiles(newFiles) {
        const remaining = MAX_FILES - selectedFiles.length;
        if (remaining <= 0) {
            showError(['已达到最大文件数量限制 (10 个)']);
            return;
        }
        const toAdd = Array.from(newFiles).slice(0, remaining);
        for (const f of toAdd) {
            if (f.size > MAX_SIZE) {
                showError([`"${f.name}" 超过 50MB 上限，已跳过`]);
                continue;
            }
            if (f.type && f.type !== 'application/pdf') {
                showError([`"${f.name}" 不是 PDF 文件，已跳过`]);
                continue;
            }
            selectedFiles.push(f);
        }
        updateFileListUI();
        hideError();
    }

    function removeFile(index) {
        selectedFiles.splice(index, 1);
        updateFileListUI();
    }

    function clearFiles() {
        selectedFiles = [];
        updateFileListUI();
        resultsSection.classList.add('hidden');
        results = [];
        resultCards.innerHTML = '';
        hideError();
    }

    // ── Drag & drop ────────────────────────────────────────────
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    });
    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('dragover');
    });
    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        addFiles(e.dataTransfer.files);
    });
    dropZone.addEventListener('click', () => fileInput.click());
    browseBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        fileInput.click();
    });
    fileInput.addEventListener('change', () => {
        addFiles(fileInput.files);
        fileInput.value = '';
    });

    // ── List events (delegation) ───────────────────────────────
    fileItems.addEventListener('click', (e) => {
        const btn = e.target.closest('.remove-btn');
        if (btn) {
            const idx = parseInt(btn.dataset.index, 10);
            if (!isNaN(idx)) removeFile(idx);
        }
    });
    clearBtn.addEventListener('click', clearFiles);

    // ── Upload & Convert ───────────────────────────────────────
    convertBtn.addEventListener('click', async () => {
        if (selectedFiles.length === 0) return;

        // Prepare UI
        convertBtn.disabled = true;
        clearBtn.disabled = true;
        progressArea.classList.remove('hidden');
        progressBar.style.width = '0%';
        progressText.textContent = `上传中 (0/${selectedFiles.length})...`;
        results = [];
        resultCards.innerHTML = '';
        resultsSection.classList.add('hidden');
        hideError();

        // Upload each file sequentially with progress
        for (let i = 0; i < selectedFiles.length; i++) {
            const file = selectedFiles[i];
            progressText.textContent = `处理中 (${i + 1}/${selectedFiles.length}): ${file.name}`;

            try {
                const formData = new FormData();
                formData.append('file', file);

                const resp = await fetch('/api/upload', {
                    method: 'POST',
                    body: formData,
                });

                if (!resp.ok) {
                    const errData = await resp.json().catch(() => ({}));
                    throw new Error(errData.detail || `HTTP ${resp.status}`);
                }

                const data = await resp.json();
                results.push({
                    filename: file.name,
                    status: 'success',
                    markdown: data.markdown,
                });
            } catch (err) {
                results.push({
                    filename: file.name,
                    status: 'error',
                    error: err.message,
                });
            }

            // Update progress bar
            const pct = Math.round(((i + 1) / selectedFiles.length) * 100);
            progressBar.style.width = pct + '%';
        }

        // Done
        progressText.textContent = `完成! 成功 ${results.filter(r => r.status === 'success').length} / ${results.length}`;
        convertBtn.disabled = false;
        clearBtn.disabled = false;
        renderResults();
    });

    // ── Render results ─────────────────────────────────────────
    function renderResults() {
        if (results.length === 0) return;

        resultsSection.classList.remove('hidden');
        resultCards.innerHTML = '';

        results.forEach((r, i) => {
            const card = document.createElement('div');
            card.className = 'result-card';

            const statusClass = r.status === 'success' ? 'success' : 'error';
            const statusLabel = r.status === 'success' ? '成功' : '失败';

            let bodyHtml = '';
            let footerHtml = '';
            if (r.status === 'success') {
                bodyHtml = `<div class="markdown-preview">${escapeHtml(r.markdown || '')}</div>`;
                footerHtml = `<button class="btn btn-primary btn-sm download-single" data-index="${i}">📥 下载 .md</button>`;
            } else {
                bodyHtml = `<p style="color:#dc2626;">${escapeHtml(r.error || '未知错误')}</p>`;
            }

            card.innerHTML = `
                <div class="result-card-header">
                    <span class="card-title" title="${escapeHtml(r.filename)}">${escapeHtml(r.filename)}</span>
                    <span class="card-status ${statusClass}">${statusLabel}</span>
                </div>
                <div class="result-card-body">${bodyHtml}</div>
                ${footerHtml ? `<div class="result-card-footer">${footerHtml}</div>` : ''}
            `;
            resultCards.appendChild(card);
        });

        // Bind download buttons
        resultCards.querySelectorAll('.download-single').forEach(btn => {
            btn.addEventListener('click', () => {
                const idx = parseInt(btn.dataset.index, 10);
                downloadSingle(idx);
            });
        });

        // Show "download all" only if at least one success
        const anySuccess = results.some(r => r.status === 'success');
        downloadAllBtn.classList.toggle('hidden', !anySuccess || results.length <= 1);
    }

    // ── Downloads ──────────────────────────────────────────────
    function downloadSingle(index) {
        const r = results[index];
        if (!r || !r.markdown) return;
        downloadBlob(r.markdown, 'text/markdown', r.filename.replace(/\.pdf$/i, '.md'));
    }

    downloadAllBtn.addEventListener('click', async () => {
        const successResults = results.filter(r => r.status === 'success');
        if (successResults.length === 0) return;

        // Use backend zip endpoint for multiple files
        try {
            const resp = await fetch('/api/download/zip', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    files: successResults.map(r => ({
                        filename: r.filename,
                        markdown: r.markdown,
                    })),
                }),
            });
            if (!resp.ok) throw new Error('Download failed');
            const blob = await resp.blob();
            downloadBlob(blob, 'application/zip', 'ocr_results.zip');
        } catch (err) {
            showError(['下载失败: ' + err.message]);
        }
    });

    function downloadBlob(content, mime, filename) {
        const blob = content instanceof Blob
            ? content
            : new Blob([content], { type: mime });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    // ── Utilities ──────────────────────────────────────────────
    function escapeHtml(str) {
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    }

    function formatSize(bytes) {
        if (bytes < 1024) return bytes + ' B';
        if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
        return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
    }

    function showError(messages) {
        errorArea.classList.remove('hidden');
        errorArea.innerHTML = '<ul>' + messages.map(m => `<li>${escapeHtml(m)}</li>`).join('') + '</ul>';
    }

    function hideError() {
        errorArea.classList.add('hidden');
        errorArea.innerHTML = '';
    }
})();
