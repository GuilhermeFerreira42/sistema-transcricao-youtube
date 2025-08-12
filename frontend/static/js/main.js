// frontend/static/js/main.js
document.addEventListener('DOMContentLoaded', function() {
    // --- Seletores de Elementos ---
    const youtubeUrlInput = document.getElementById('youtube-url');
    const processBtn = document.getElementById('process-btn');
    const statusMessage = document.getElementById('status-message');
    
    const mainContent = document.getElementById('main-content');
    const processingIndicator = document.getElementById('processing-indicator');
    
    const videoInfoSection = document.getElementById('video-info');
    const videoThumbnail = document.getElementById('video-thumbnail');
    const videoTitle = document.getElementById('video-title');
    const transcriptionSection = document.getElementById('transcription-section');
    const transcriptionContent = document.getElementById('transcription-content');
    const downloadBtn = document.getElementById('download-btn');
    
    const historyList = document.getElementById('history-list');
    const searchHistoryInput = document.getElementById('search-history');

    const deleteModal = document.getElementById('delete-modal');
    const modalCancelBtn = document.getElementById('modal-cancel-btn');
    const modalConfirmBtn = document.getElementById('modal-confirm-btn');
    let videoIdToDelete = null;

    // --- Funções Auxiliares ---

    function showStatus(message, type = 'info') {
        statusMessage.textContent = message;
        statusMessage.className = 'status-message';
        if (type === 'success') statusMessage.classList.add('success');
        if (type === 'error') statusMessage.classList.add('error');
        statusMessage.style.display = 'block';
    }

    function hideStatus() {
        statusMessage.style.display = 'none';
        statusMessage.textContent = '';
    }

    function isValidYoutubeUrl(url) {
        const regex = /^(https?:\/\/)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)\/(watch\?v=|embed\/|v\/|.+\?v=)?([^&=%\?]{11})/;
        return regex.test(url);
    }

    // --- Lógica do Histórico (MODIFICADA) ---

    // NEW: Function to create and add a history item to the DOM
    function addHistoryItemToDOM(item, prepend = false) {
        // Remove the "empty history" message if it exists
        const emptyState = historyList.querySelector('.history-item-empty');
        if (emptyState) {
            emptyState.remove();
        }
        
        const li = document.createElement('li');
        li.className = 'history-item';
        li.dataset.videoId = item.video_id;
        li.innerHTML = `
            <span class="history-item-title" title="${item.title}">${item.title}</span>
            <button class="delete-history-btn" data-video-id="${item.video_id}" title="Excluir transcrição">&times;</button>
        `;

        li.querySelector('.history-item-title').addEventListener('click', () => {
            loadTranscription(item.video_id);
            setActiveHistoryItem(item.video_id);
        });

        li.querySelector('.delete-history-btn').addEventListener('click', (e) => {
            e.stopPropagation();
            openDeleteModal(item.video_id);
        });

        if (prepend) {
            historyList.prepend(li); // Add to the top
        } else {
            historyList.appendChild(li); // Add to the end
        }
    }

    async function loadHistory() {
        try {
            const response = await fetch('/get_history');
            const data = await response.json();
            if (data.success && data.history) {
                historyList.innerHTML = ''; // Clears the list
                if (data.history.length === 0) {
                    historyList.innerHTML = '<li class="history-item-empty">Nenhum histórico.</li>';
                    return;
                }
                data.history.forEach(item => addHistoryItemToDOM(item));
            } else {
                console.error("Erro ao carregar histórico:", data.error);
            }
        } catch (error) {
            console.error('Falha na requisição do histórico:', error);
        }
    }
    
    function setActiveHistoryItem(videoId) {
        document.querySelectorAll('.history-item').forEach(item => {
            item.classList.remove('active');
            if (item.dataset.videoId === videoId) {
                item.classList.add('active');
            }
        });
    }

    searchHistoryInput.addEventListener('input', () => {
        const searchTerm = searchHistoryInput.value.toLowerCase();
        document.querySelectorAll('.history-item').forEach(item => {
            const title = item.querySelector('.history-item-title').textContent.toLowerCase();
            item.style.display = title.includes(searchTerm) ? 'flex' : 'none';
        });
    });

    // --- Lógica de Transcrição ---

    async function processVideo() {
        const url = youtubeUrlInput.value.trim();
        if (!url || !isValidYoutubeUrl(url)) {
            showStatus('Por favor, insira uma URL do YouTube válida.', 'error');
            return;
        }
        
        mainContent.style.display = 'none';
        hideStatus();
        processingIndicator.style.display = 'flex';
        processBtn.disabled = true;
        
        try {
            const response = await fetch('/process_youtube_video', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url })
            });
            const data = await response.json();
            
            if (!data.success) {
                throw new Error(data.error || 'Erro desconhecido.');
            }
            
            showStatus('Vídeo processado com sucesso!', 'success');
            updateUIWithTranscription(data);
            youtubeUrlInput.value = '';
            
            // MODIFIED: Adds dynamically instead of reloading everything
            addHistoryItemToDOM({ video_id: data.video_id, title: data.title }, true);
            setActiveHistoryItem(data.video_id);

        } catch (error) {
            console.error('Erro no processamento:', error);
            showStatus(`Erro: ${error.message}`, 'error');
        } finally {
            processingIndicator.style.display = 'none';
            processBtn.disabled = false;
        }
    }
    
    async function loadTranscription(videoId) {
        hideStatus();
        mainContent.style.display = 'none';
        processingIndicator.style.display = 'flex';
        
        try {
            const response = await fetch(`/get_transcription/${videoId}`);
            const data = await response.json();
            if (data.error) throw new Error(data.error);
            
            // The /get_transcription response doesn't have video_id, so we get it from metadata if it exists
            const fullData = {
                video_id: videoId,
                title: data.title,
                thumbnail: data.metadata?.thumbnail || data.thumbnail,
                transcript: data.transcript
            };
            updateUIWithTranscription(fullData);

        } catch (error) {
            console.error('Erro ao carregar transcrição:', error);
            showStatus(`Erro ao carregar transcrição: ${error.message}`, 'error');
        } finally {
            processingIndicator.style.display = 'none';
        }
    }

    function updateUIWithTranscription(data) {
        videoTitle.textContent = data.title;
        videoThumbnail.src = data.thumbnail || `https://i.ytimg.com/vi/${data.video_id}/hqdefault.jpg`;
        transcriptionContent.textContent = data.transcript;
        downloadBtn.onclick = () => window.location.href = `/download_transcription/${data.video_id}`;
        mainContent.style.display = 'block';
    }

    // --- Lógica de Exclusão ---
    
    function openDeleteModal(videoId) {
        videoIdToDelete = videoId;
        deleteModal.style.display = 'flex';
    }

    function closeDeleteModal() {
        videoIdToDelete = null;
        deleteModal.style.display = 'none';
    }

    async function confirmDelete() {
        if (!videoIdToDelete) return;
        try {
            const response = await fetch(`/delete_transcription/${videoIdToDelete}`, { method: 'DELETE' });
            const data = await response.json();
            if (data.success) {
                showStatus('Transcrição excluída.', 'success');
                const itemToRemove = historyList.querySelector(`[data-video-id="${videoIdToDelete}"]`);
                if (itemToRemove) itemToRemove.remove();
                if (historyList.children.length === 0) {
                     historyList.innerHTML = '<li class="history-item-empty">Nenhum histórico.</li>';
                }
                const activeItem = document.querySelector('.history-item.active');
                if (!activeItem || activeItem.dataset.videoId === videoIdToDelete) {
                    mainContent.style.display = 'none';
                }
            } else {
                throw new Error(data.error || "Erro ao excluir.");
            }
        } catch (error) {
            console.error('Erro na exclusão:', error);
            showStatus(`Erro: ${error.message}`, 'error');
        } finally {
            closeDeleteModal();
        }
    }

    // --- Event Listeners ---
    processBtn.addEventListener('click', processVideo);
    youtubeUrlInput.addEventListener('keypress', (e) => { if (e.key === 'Enter') processVideo(); });
    modalCancelBtn.addEventListener('click', closeDeleteModal);
    modalConfirmBtn.addEventListener('click', confirmDelete);

    // --- Inicialização ---
    loadHistory();
});