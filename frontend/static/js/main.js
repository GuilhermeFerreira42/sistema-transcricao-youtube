// frontend/static/js/main.js (Atualizado para Fase 4)
document.addEventListener('DOMContentLoaded', function() {
    // --- Conexão com o Socket.IO ---
    const socket = io();

    // --- Seletores de elementos ---
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
    const playlistViewSection = document.getElementById('playlist-view-section');
    const playlistViewTitle = document.getElementById('playlist-view-title');
    const playlistViewVideoList = document.getElementById('playlist-view-video-list');
    const downloadPlaylistZipBtn = document.getElementById('download-playlist-zip-btn');
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

    // --- Funções auxiliares ---
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

    function isValidYoutubeUrl(url) {
        const youtubeRegex = /^(https?:\/\/)?(www\.)?(youtube\.com|youtu\.be)\/(watch\?v=[\w-]+|playlist\?list=[\w-]+|[\w-]+)/;
        return youtubeRegex.test(url);
    }

    // --- Lógica de Histórico (MODIFICADA PARA FASE 4) ---

    /**
     * Adiciona um item de vídeo standalone (não em playlist) ao DOM do histórico.
     */
    function addVideoItemToDOM(item) {
        const li = document.createElement('li');
        li.className = 'history-item history-video-item'; // Classe específica para vídeos
        li.dataset.id = item.id;
        li.dataset.type = item.type;
        
        li.innerHTML = `
            <span class="history-item-icon"><i class="fab fa-youtube"></i></span>
            <span class="history-item-title" title="${item.title}">${item.title}</span>
            <button class="delete-history-btn" data-id="${item.id}" title="Excluir item">×</button>
        `;

        li.addEventListener('click', () => {
            loadTranscription(item.id);
            setActiveHistoryItem(item.id);
        });

        li.querySelector('.delete-history-btn').addEventListener('click', (e) => {
            e.stopPropagation();
            openDeleteModal(item.id);
        });

        historyList.appendChild(li);
    }

    /**
     * Adiciona um item de playlist ao DOM, com seus vídeos aninhados.
     */
    function addPlaylistItemToDOM(playlist, videoDetailsMap) {
        const li = document.createElement('li');
        li.className = 'history-item history-playlist-item'; // Classe específica para playlists
        li.dataset.id = playlist.id;
        li.dataset.type = playlist.type;

        li.innerHTML = `
            <div class="history-item-header">
                <span class="expand-btn"><i class="fas fa-chevron-right"></i></span>
                <span class="history-item-icon"><i class="fas fa-list-ol"></i></span>
                <span class="history-item-title" title="${playlist.title}">${playlist.title}</span>
                <button class="delete-history-btn" data-id="${playlist.id}" title="Excluir playlist">×</button>
            </div>
            <ul class="video-sublist" style="display: none;"></ul>
        `;

        const sublist = li.querySelector('.video-sublist');
        if (playlist.video_ids && playlist.video_ids.length > 0) {
            playlist.video_ids.forEach(videoId => {
                const video = videoDetailsMap.get(videoId);
                if (video) {
                    const subLi = document.createElement('li');
                    subLi.className = 'history-sub-item';
                    subLi.dataset.id = video.id;
                    subLi.innerHTML = `
                        <span class="history-item-icon sub-icon"><i class="fab fa-youtube"></i></span>
                        <span class="history-item-title">${video.title}</span>`;
                    
                    // Comportamento de clique para sub-item: carrega transcrição mas mantém a playlist ativa
                    subLi.addEventListener('click', (e) => {
                        e.stopPropagation();
                        loadTranscription(video.id);
                        setActiveHistoryItem(playlist.id); // Mantém a playlist como item ativo
                    });
                    sublist.appendChild(subLi);
                }
            });
        } else {
            sublist.innerHTML = `<li class="history-sub-item-empty">Playlist vazia.</li>`;
        }

        // Evento para abrir a visualização da playlist
        li.querySelector('.history-item-header').addEventListener('click', () => {
            loadPlaylistView(playlist.id);
            setActiveHistoryItem(playlist.id);
        });
        
        // Evento para expandir/recolher a sublista
        const expandBtn = li.querySelector('.expand-btn');
        expandBtn.addEventListener('click', (e) => {
            e.stopPropagation(); // Impede que o clique dispare o evento do header
            const isExpanded = sublist.style.display === 'block';
            sublist.style.display = isExpanded ? 'none' : 'block';
            expandBtn.querySelector('i').classList.toggle('fa-chevron-right', isExpanded);
            expandBtn.querySelector('i').classList.toggle('fa-chevron-down', !isExpanded);
        });

        li.querySelector('.delete-history-btn').addEventListener('click', (e) => {
            e.stopPropagation();
            openDeleteModal(playlist.id);
        });

        historyList.appendChild(li);
    }
    
    /**
     * Carrega e organiza o histórico em playlists e vídeos independentes.
     */
    async function loadHistory() {
        try {
            const response = await fetch('/get_history');
            const data = await response.json();
            historyList.innerHTML = ''; 

            if (!data.success || !data.history || data.history.length === 0) {
                historyList.innerHTML = '<li class="history-item-empty">Nenhum histórico.</li>';
                return;
            }

            const allItems = data.history;
            const videoDetailsMap = new Map(allItems.map(item => [item.id, item]));
            const playlistVideoIds = new Set();
            
            // Separa playlists e encontra todos os IDs de vídeos que pertencem a elas
            const playlists = allItems.filter(item => {
                if (item.type === 'playlist') {
                    item.video_ids.forEach(vid => playlistVideoIds.add(vid));
                    return true;
                }
                return false;
            });
            
            // Filtra vídeos que não pertencem a nenhuma playlist
            const standaloneVideos = allItems.filter(
                item => item.type === 'video' && !playlistVideoIds.has(item.id)
            );

            // Renderiza as playlists com seus vídeos aninhados
            playlists.forEach(playlist => addPlaylistItemToDOM(playlist, videoDetailsMap));
            
            // Renderiza os vídeos independentes
            standaloneVideos.forEach(video => addVideoItemToDOM(video));

        } catch (error) {
            console.error('Falha na requisição do histórico:', error);
            historyList.innerHTML = '<li class="history-item-empty">Falha ao conectar com o servidor.</li>';
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
            item.style.display = title.includes(searchTerm) ? 'block' : 'none'; // 'block' para li
        });
    });

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
            const response = await fetch('/process_url', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url })
            });
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
    
    async function loadPlaylistView(playlistId) {
        hideStatus();
        hideAllViews();
        processingIndicator.style.display = 'flex';
        processingIndicatorText.textContent = 'Carregando detalhes da playlist...';
        try {
            const response = await fetch(`/get_playlist_details/${playlistId}`);
            const data = await response.json();
            if (!data.success) throw new Error(data.error);

            const details = data.details;
            playlistViewTitle.textContent = `Vídeos em: ${details.title}`;
            playlistViewVideoList.innerHTML = '';

            if (details.videos.length > 0) {
                details.videos.forEach(video => {
                    const li = document.createElement('li');
                    li.className = 'playlist-video-item';
                    const iconClass = video.status === 'success' ? 'fas fa-check-circle success' : 'fas fa-times-circle error';
                    li.innerHTML = `
                        <span class="icon"><i class="${iconClass}"></i></span>
                        <span class="playlist-video-title">${video.title}</span>
                    `;
                    li.addEventListener('click', () => {
                        if (video.status === 'success') {
                            loadTranscription(video.id);
                            setActiveHistoryItem(playlistId); // Mantém a playlist ativa
                        }
                    });
                    playlistViewVideoList.appendChild(li);
                });
            } else {
                playlistViewVideoList.innerHTML = '<li class="history-item-empty">Nenhum vídeo nesta playlist.</li>';
            }
            
            downloadPlaylistZipBtn.onclick = () => {
                window.location.href = `/download_playlist/${playlistId}`;
            };

            playlistViewSection.style.display = 'block';

        } catch (error) {
            console.error('Erro ao carregar detalhes da playlist:', error);
            showStatus(`Erro: ${error.message}`, 'error');
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
    
    function openDeleteModal(id) {
        itemToDelete = id;
        deleteModal.style.display = 'flex';
    }

    function closeDeleteModal() {
        itemToDelete = null;
        deleteModal.style.display = 'none';
    }

    async function confirmDelete() {
        if (!itemToDelete) return;
        try {
            const response = await fetch(`/delete_entry/${itemToDelete}`, { method: 'DELETE' });
            const data = await response.json();

            if (data.success) {
                showStatus('Item excluído com sucesso.', 'success');
                // A maneira mais simples e robusta de atualizar a UI hierárquica é recarregar o histórico
                loadHistory(); 

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

    // --- Listeners de Socket.IO ---
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
            const progressPercentage = (data.current_video / data.total_videos) * 100;
            playlistProgressBar.style.width = `${progressPercentage}%`;

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
            loadHistory(); // Recarrega o histórico para adicionar o novo vídeo
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
        playlistViewSection.style.display = 'none';
    }

    // --- Event Listeners ---
    processBtn.addEventListener('click', processUrl);
    youtubeUrlInput.addEventListener('keypress', (e) => { if (e.key === 'Enter') processUrl(); });
    modalCancelBtn.addEventListener('click', closeDeleteModal);
    modalConfirmBtn.addEventListener('click', confirmDelete);
    
    // --- Inicialização ---
    loadHistory();
});