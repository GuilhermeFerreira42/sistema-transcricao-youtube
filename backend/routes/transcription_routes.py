"""
Blueprint de rotas de transcrição
"""
from flask import Blueprint, request, jsonify, current_app
import logging
import re
from services.processing_service import ProcessingService

transcription_bp = Blueprint('transcription', __name__)
logger = logging.getLogger('transcription_routes')

def is_playlist(url: str) -> bool:
    """Verifica se uma URL do YouTube é de uma playlist."""
    playlist_pattern = r'list=([a-zA-Z0-9_-]+)'
    return bool(re.search(playlist_pattern, url))

@transcription_bp.route('/process_url', methods=['POST'])
def process_url():
    """
    Rota para processar uma URL do YouTube (vídeo ou playlist).
    Inicia o processamento em background e retorna uma resposta imediata.
    """
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({"success": False, "error": "URL não fornecida"}), 400
    url = data['url']
    logger.info(f"Recebida URL para processamento: {url}")
    ps = current_app.processing_service
    sio = current_app.socketio
    if is_playlist(url):
        sio.start_background_task(target=ps.process_playlist_task, url=url)
        return jsonify({"success": True, "message": "Processamento da playlist iniciado."})
    else:
        sio.start_background_task(target=ps.process_video_task, url=url)
        return jsonify({"success": True, "message": "Processamento do vídeo iniciado."})
