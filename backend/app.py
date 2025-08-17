# backend/app.py
from flask import Flask, request, jsonify, render_template, current_app
from flask_socketio import SocketIO
import os
import logging
import json
from datetime import datetime
from youtube_handler import YouTubeHandler
import re
from io import BytesIO
from routes.transcription_routes import transcription_bp
from services.processing_service import ProcessingService
from routes.history_routes import history_bp
from routes.download_routes import download_bp

# Configuração do logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('app')

def is_playlist(url: str) -> bool:
    """Verifica se uma URL do YouTube é de uma playlist."""
    playlist_pattern = r'list=([a-zA-Z0-9_-]+)'
    return bool(re.search(playlist_pattern, url))

def create_app():
    app = Flask(__name__, 
                template_folder='../frontend/templates',
                static_folder='../frontend/static')

    app.config['SECRET_KEY'] = 'your_super_secret_key' 
    
    # Instância única dos serviços
    youtube_handler = YouTubeHandler()
    socketio = SocketIO(app, async_mode='threading')
    processing_service = ProcessingService(youtube_handler, socketio, logger)

    # Anexa ao app
    app.youtube_handler = youtube_handler
    app.socketio = socketio
    app.processing_service = processing_service

    # Rotas principais
    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/process_url', methods=['POST'])
    def process_url():
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

    # Registro dos Blueprints
    app.register_blueprint(transcription_bp)
    app.register_blueprint(history_bp)
    app.register_blueprint(download_bp)

    return app, socketio

if __name__ == '__main__':
    app, socketio = create_app()
    os.makedirs('data/transcriptions', exist_ok=True)
    logger.info("Iniciando servidor com Socket.IO na porta 5000...")
    socketio.run(app, debug=True, port=5000, allow_unsafe_werkzeug=True)