"""
Serviço de processamento de vídeos e playlists do YouTube
"""
from datetime import datetime
import logging
from utils import extract_video_id

class ProcessingService:
    def __init__(self, youtube_handler, socketio, logger=None):
        self.youtube_handler = youtube_handler
        self.socketio = socketio
        self.logger = logger or logging.getLogger('processing_service')

    def process_video_task(self, url: str):
        """
        Processa um vídeo do YouTube e emite eventos via Socket.IO
        """
        video_id = extract_video_id(url)
        if not video_id:
            self.socketio.emit('video_error', {'error': 'ID do vídeo inválido.'})
            return
        try:
            self.socketio.emit('video_progress', {'video_id': video_id, 'status': 'processing', 'message': 'Iniciando processamento...'})
            transcript, metadata, json_path = self.youtube_handler.download_and_clean_transcript(url)
            if not transcript:
                error_msg = f"Não foi possível obter a transcrição para '{metadata.get('title', 'desconhecido')}'"
                self.socketio.emit('video_error', {'video_id': video_id, 'status': 'error', 'error': error_msg})
                return
            response = {
                "success": True,
                "video_id": metadata['video_id'],
                "title": metadata['title'],
                "thumbnail": metadata['thumbnail'],
                "transcript": transcript,
            }
            self.socketio.emit('video_complete', response)
        except Exception as e:
            self.logger.exception(f"Erro na tarefa de processamento de vídeo {url}: {e}")
            self.socketio.emit('video_error', {'video_id': video_id, 'status': 'error', 'error': str(e)})

    def process_playlist_task(self, url: str):
        """
        Processa uma playlist do YouTube e emite eventos via Socket.IO
        """
        playlist_info = self.youtube_handler.get_playlist_info(url)
        if not playlist_info or not playlist_info.get('videos'):
            self.socketio.emit('playlist_error', {'error': 'Não foi possível extrair informações da playlist.'})
            return
        playlist_id = playlist_info['id']
        videos = playlist_info['videos']
        total_videos = len(videos)
        playlist_entry = {
            "id": playlist_id,
            "type": "playlist",
            "title": playlist_info['title'],
            "status": "processing",
            "video_ids": [v['id'] for v in videos],
            "created_at": datetime.now().isoformat()
        }
        self.youtube_handler.history_manager.add_entry(playlist_entry)
        self.socketio.emit('playlist_start', {
            'playlist_id': playlist_id,
            'title': playlist_info['title'],
            'total_videos': total_videos,
            'videos': videos
        })
        processed_count = 0
        error_count = 0
        for i, video in enumerate(videos):
            video_id = video['id']
            video_url = video['url']
            self.socketio.emit('video_progress', {
                'playlist_id': playlist_id,
                'video_id': video_id,
                'title': video['title'],
                'status': 'processing',
                'message': f"Processando vídeo {i + 1} de {total_videos}...",
                'current_video': i + 1,
                'total_videos': total_videos
            })
            try:
                transcript, metadata, _ = self.youtube_handler.download_and_clean_transcript(video_url)
                if transcript:
                    self.socketio.emit('video_complete', {
                        'playlist_id': playlist_id,
                        'video_id': video_id,
                        'status': 'success'
                    })
                    processed_count += 1
                else:
                    raise Exception("Transcrição não encontrada.")
            except Exception as e:
                self.logger.error(f"Erro ao processar vídeo {video_url} da playlist: {e}")
                self.socketio.emit('video_error', {
                    'playlist_id': playlist_id,
                    'video_id': video_id,
                    'status': 'error',
                    'error': str(e)
                })
                error_count += 1
        # Atualiza status da playlist ao final do processamento
        playlist_entry = next((entry for entry in self.youtube_handler.history_manager.get_history() if entry.get('id') == playlist_id and entry.get('type') == 'playlist'), None)
        if playlist_entry:
            playlist_entry['status'] = 'success'
            self.youtube_handler.history_manager._save_history()
        self.socketio.emit('playlist_complete', {
            'playlist_id': playlist_id,
            'processed_count': processed_count,
            'error_count': error_count
        })
