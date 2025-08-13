// frontend/static/js/main.js (Corrigido e Atualizado para Fase 3)
document.addEventListener('DOMContentLoaded', function() {
    // --- Conexão com o Socket.IO ---
    const socket = io();

    // --- Seletores de Elementos ---
    const youtubeUrlInput = document.getElementById('youtube-url');
    const processBtn = document.getElementById('process-btn');
    const statusMessage = document.getElementById('status-message');
    
    const mainContent = document.getElementById('main-content');
    const processingIndicator = document.getElementById('processing-indicator');
    const processingIndicatorText = document.getElementById('processing-indicator-text');
    
    const playlistProgressSection = document.getElementById('playlist-progress-section');
    const playlistProgressTitle = document.getElementById('playlist-progress-title');
    const playlistProgressBar = document.getElementById('playlist-progress-bar');
    const playlistProgressStatus = document.getElementById('playlist-progress-status');
    const playlistVideoList = document.getElementById('playlist-video-list');

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
    let itemToDelete = null;

    // --- Funções Auxiliares ---

    function showStatus(message, type = 'info') {
        statusMessage.textContent = message;
        statusMessage.className = 'status-message';
        if (type === 'success') {
            statusMessage.classList.add('success');
        } else if (type === 'error') {
            statusMessage.classList.add('error');
        }
        statusMessage.style.display = 'block';
    }
    
    function hideStatus() {
        statusMessage.style.display = 'none';
    }

    // --- CORREÇÃO: Função de validação de URL para aceitar vídeos e playlists ---
    function isValidYoutubeUrl(url) {
        const youtubeRegex = /^(https?:\/\/)?(www\.)?(youtube\.com|youtu\.be)\/(watch\?v=[\w-]+|playlist\?list=[\w-]+|[\w-]+)/;
        return youtubeRegex.test(url);
    }

    // --- Lógica de Histórico ---

    function addHistoryItemToDOM(item, prepend = false) {
        const emptyState = historyList.querySelector('.history-item-empty');
        if (emptyState) emptyState.remove();
        
        const li = document.createElement('li');
        li.className = 'history-item';
        li.dataset.id = item.id;
        li.dataset.type = item.type;
        
        const icon = item.type === 'playlist' 
            ? '<i class="fas fa-list-ol"></i>' 
            : '<i class="fab fa-youtube"></i>';

        li.innerHTML = `
            <span class="history-item-icon">${icon}</span>
            <span class="history-item-title" title="${item.title}">${item.title}</span>
            <button class="delete-history-btn" data-id="${item.id}" title="Excluir item">&times;</button>
        `;

        li.querySelector('.history-item-title').addEventListener('click', () => {
            if (item.type === 'video') {
                loadTranscription(item.id);
            }
            // Futuramente, adicionar lógica para visualizar playlists
            setActiveHistoryItem(item.id);
        });

        li.querySelector('.delete-history-btn').addEventListener('click', (e) => {
            e.stopPropagation();
            openDeleteModal(item.id);
        });

        if (prepend) {
            historyList.prepend(li);
        } else {
            historyList.appendChild(li);
        }
    }

    async function loadHistory() {
        try {
            const response = await fetch('/get_history');
            const data = await response.json();
            if (data.success && data.history) {
                historyList.innerHTML = '';
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
    
    function setActiveHistoryItem(id) {
        document.querySelectorAll('.history-item').forEach(item => {
            item.classList.remove('active');
            if (item.dataset.id === id) {
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

    // --- Lógica de Processamento (Corrigida) ---

    // --- CORREÇÃO: Função unificada para processar URL, apontando para a rota correta `/process_url` ---
    async function processUrl() {
        const url = youtubeUrlInput.value.trim();
        if (!isValidYoutubeUrl(url)) {
            showStatus('Por favor, insira uma URL do YouTube válida.', 'error');
            return;
        }
        
        hideStatus();
        hideAllViews();
        processingIndicator.style.display = 'flex';
        processingIndicatorText.textContent = 'Enviando URL para o servidor...';
        processBtn.disabled = true;

        try {
            // --- CORREÇÃO: A requisição agora é enviada para `/process_url` ---
            const response = await fetch('/process_url', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url })
            });

            // O erro `SyntaxError` acontecia aqui, pois a resposta era um HTML de erro 404.
            const data = await response.json();

            if (data.success) {
                showStatus(data.message, 'success');
                youtubeUrlInput.value = '';
            } else {
                throw new Error(data.error || 'Ocorreu um erro no servidor.');
            }
        } catch (error) {
            console.error('Erro no processamento:', error);
            showStatus(`Erro: ${error.message}`, 'error');
            processingIndicator.style.display = 'none';
            processBtn.disabled = false;
        }
    }
    
    async function loadTranscription(videoId) {
        hideStatus();
        hideAllViews();
        processingIndicator.style.display = 'flex';
        processingIndicatorText.textContent = 'Carregando transcrição...';
        
        try {
            const response = await fetch(`/get_transcription/${videoId}`);
            const data = await response.json();
            if (data.error) throw new Error(data.error);
            
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
        hideAllViews();
        videoTitle.textContent = data.title;
        videoThumbnail.src = data.thumbnail || `https://i.ytimg.com/vi/${data.video_id}/hqdefault.jpg`;
        transcriptionContent.textContent = data.transcript;
        downloadBtn.onclick = () => window.location.href = `/download_transcription/${data.video_id}`;
        mainContent.style.display = 'block';
    }

    // --- Lógica de Exclusão (Corrigida) ---
    
    function openDeleteModal(id) {
        itemToDelete = id;
        deleteModal.style.display = 'flex';
    }

    function closeDeleteModal() {
        itemToDelete = null;
        deleteModal.style.display = 'none';
    }

    // --- CORREÇÃO: Lógica de exclusão revisada para garantir a remoção da UI ---
    async function confirmDelete() {
        if (!itemToDelete) return;

        try {
            const response = await fetch(`/delete_transcription/${itemToDelete}`, { method: 'DELETE' });
            const data = await response.json();

            if (data.success) {
                showStatus('Item excluído com sucesso.', 'success');
                const itemToRemove = historyList.querySelector(`[data-id="${itemToDelete}"]`);
                if (itemToRemove) {
                    itemToRemove.remove();
                }

                // Verifica se a lista de histórico ficou vazia
                if (historyList.children.length === 0) {
                     historyList.innerHTML = '<li class="history-item-empty">Nenhum histórico.</li>';
                }

                // Limpa a tela principal se o item ativo foi excluído
                const activeItem = document.querySelector('.history-item.active');
                if (!activeItem || (activeItem && activeItem.dataset.id === itemToDelete)) {
                    hideAllViews();
                }

            } else {
                throw new Error(data.error || "Erro desconhecido ao excluir.");
            }
        } catch (error) {
            console.error('Erro na exclusão:', error);
            showStatus(`Erro: ${error.message}`, 'error');
        } finally {
            closeDeleteModal();
        }
    }

    // --- Listeners para eventos do Socket.IO ---
    
    socket.on('connect', () => {
        console.log('Conectado ao servidor via Socket.IO');
    });

    socket.on('playlist_start', (data) => {
        hideAllViews();
        playlistProgressSection.style.display = 'block';
        playlistProgressTitle.textContent = `Processando Playlist: ${data.title}`;
        playlistProgressStatus.textContent = `0 de ${data.total_videos} vídeos processados.`;
        playlistProgressBar.style.width = '0%';
        playlistVideoList.innerHTML = '';

        data.videos.forEach(video => {
            const li = document.createElement('li');
            li.id = `video-item-${video.id}`;
            li.className = 'playlist-video-item';
            li.innerHTML = `
                <span class="icon"><i class="far fa-clock"></i></span>
                <span class="playlist-video-title">${video.title}</span>
            `;
            playlistVideoList.appendChild(li);
        });
    });

    socket.on('video_progress', (data) => {
        processBtn.disabled = true;
        
        if(data.playlist_id) {
            const videoItem = document.getElementById(`video-item-${data.video_id}`);
            if(videoItem) {
                videoItem.querySelector('.icon').innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
                videoItem.querySelector('.icon').className = 'icon processing';
            }
            playlistProgressStatus.textContent = data.message;
        } else {
            hideAllViews();
            processingIndicator.style.display = 'flex';
            processingIndicatorText.textContent = data.message;
        }
    });

    socket.on('video_complete', (data) => {
        if(data.playlist_id) {
            const videoItem = document.getElementById(`video-item-${data.video_id}`);
            if(videoItem) {
                videoItem.querySelector('.icon').innerHTML = '<i class="fas fa-check-circle"></i>';
                videoItem.querySelector('.icon').className = 'icon success';
            }
        } else {
            hideAllViews();
            updateUIWithTranscription(data);
            showStatus('Vídeo processado com sucesso!', 'success');
            processBtn.disabled = false;
        }
        
        const existingItem = historyList.querySelector(`[data-id="${data.video_id}"]`);
        if (!existingItem) {
            addHistoryItemToDOM({ id: data.video_id, title: data.title, type: 'video' }, true);
            setActiveHistoryItem(data.video_id);
        }
    });

    socket.on('video_error', (data) => {
        if(data.playlist_id) {
            const videoItem = document.getElementById(`video-item-${data.video_id}`);
            if(videoItem) {
                videoItem.querySelector('.icon').innerHTML = '<i class="fas fa-times-circle"></i>';
                videoItem.querySelector('.icon').className = 'icon error';
                videoItem.title = data.error;
            }
        } else {
            hideAllViews();
            showStatus(`Erro: ${data.error}`, 'error');
            processBtn.disabled = false;
        }
    });

    socket.on('playlist_complete', (data) => {
        playlistProgressStatus.textContent = `Concluído! ${data.processed_count} vídeos processados, ${data.error_count} falhas.`;
        playlistProgressBar.style.width = '100%';
        processBtn.disabled = false;
        loadHistory(); 
    });

    function hideAllViews() {
        mainContent.style.display = 'none';
        processingIndicator.style.display = 'none';
        playlistProgressSection.style.display = 'none';
    }

    // --- Event Listeners ---
    processBtn.addEventListener('click', processUrl);
    youtubeUrlInput.addEventListener('keypress', (e) => { if (e.key === 'Enter') processUrl(); });
    modalCancelBtn.addEventListener('click', closeDeleteModal);
    modalConfirmBtn.addEventListener('click', confirmDelete);

    // --- Inicialização ---
    loadHistory();
});
