// frontend/static/js/main.js
document.addEventListener('DOMContentLoaded', function() {
    const youtubeUrlInput = document.getElementById('youtube-url');
    const processBtn = document.getElementById('process-btn');
    const statusMessage = document.getElementById('status-message');
    const videoInfoSection = document.getElementById('video-info');
    const videoThumbnail = document.getElementById('video-thumbnail');
    const videoTitle = document.getElementById('video-title');
    const processingIndicator = document.getElementById('processing-indicator');
    const transcriptionSection = document.getElementById('transcription-section');
    const transcriptionContent = document.getElementById('transcription-content');
    const downloadBtn = document.getElementById('download-btn');
    
    // Função para exibir mensagens de status
    function showStatus(message, type = 'info') {
        statusMessage.textContent = message;
        statusMessage.className = 'status-message';
        
        if (type === 'success') {
            statusMessage.classList.add('success');
        } else if (type === 'error') {
            statusMessage.classList.add('error');
        } else {
            statusMessage.style.display = 'block';
        }
    }
    
    // Função para validar URL do YouTube
    function isValidYoutubeUrl(url) {
        const regex = /^(https?:\/\/)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)\/(watch\?v=|embed\/|v\/|.+\?v=)?([^&=%\?]{11})/;
        return regex.test(url);
    }
    
    // Função para processar o vídeo
    async function processVideo() {
        const url = youtubeUrlInput.value.trim();
        
        if (!url) {
            showStatus('Por favor, insira uma URL do YouTube', 'error');
            return;
        }
        
        if (!isValidYoutubeUrl(url)) {
            showStatus('URL do YouTube inválida. Por favor, insira uma URL válida do YouTube.', 'error');
            return;
        }
        
        // Resetar interface
        videoInfoSection.style.display = 'none';
        transcriptionSection.style.display = 'none';
        showStatus('Processando vídeo...', 'info');
        processBtn.disabled = true;
        
        try {
            // Mostrar indicador de processamento
            processingIndicator.style.display = 'flex';
            
            // Enviar requisição para o backend
            const response = await fetch('/process_youtube_video', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ url: url })
            });
            
            const data = await response.json();
            
            if (!data.success) {
                throw new Error(data.error || 'Erro ao processar o vídeo');
            }
            
            // Atualizar interface com os dados do vídeo
            videoThumbnail.src = data.thumbnail || 'https://i.ytimg.com/vi/' + data.video_id + '/hqdefault.jpg';
            videoTitle.textContent = data.title;
            
            // Exibir transcrição
            transcriptionContent.textContent = data.transcript;
            
            // Atualizar elementos da interface
            videoInfoSection.style.display = 'block';
            transcriptionSection.style.display = 'block';
            processingIndicator.style.display = 'none';
            
            showStatus('Vídeo processado com sucesso!', 'success');
            
            // Configurar o botão de download
            downloadBtn.onclick = function() {
                window.location.href = `/download_transcription/${data.video_id}`;
            };
            
        } catch (error) {
            console.error('Erro:', error);
            showStatus(`Erro: ${error.message}`, 'error');
            processingIndicator.style.display = 'none';
        } finally {
            processBtn.disabled = false;
        }
    }
    
    // Event listeners
    processBtn.addEventListener('click', processVideo);
    
    youtubeUrlInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            processVideo();
        }
    });
});