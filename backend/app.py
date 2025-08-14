# backend/app.py
from flask import Flask, request, jsonify, send_file, render_template
from flask_socketio import SocketIO
import os
import logging
import json
from datetime import datetime
from youtube_handler import YouTubeHandler
import re
from io import BytesIO

# Configuração do logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('app')

app = Flask(__name__, 
            template_folder='../frontend/templates',
            static_folder='../frontend/static')

app.config['SECRET_KEY'] = 'your_super_secret_key' 
socketio = SocketIO(app, async_mode='threading')

youtube_handler = YouTubeHandler()

def is_playlist(url: str) -> bool:
    """Verifica se uma URL do YouTube é de uma playlist."""
    playlist_pattern = r'list=([a-zA-Z0-9_-]+)'
    return bool(re.search(playlist_pattern, url))


@app.route('/')
def index():
    """Renderiza a página principal"""
    return render_template('index.html')

@app.route('/process_url', methods=['POST'])
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

    if is_playlist(url):
        socketio.start_background_task(target=process_playlist_task, url=url)
        return jsonify({"success": True, "message": "Processamento da playlist iniciado."})
    else:
        socketio.start_background_task(target=process_video_task, url=url)
        return jsonify({"success": True, "message": "Processamento do vídeo iniciado."})

def process_video_task(url: str):
    """
    Função executada em background para processar um vídeo e emitir eventos.
    """
    video_id = youtube_handler.extract_video_id(url)
    if not video_id:
        socketio.emit('video_error', {'error': 'ID do vídeo inválido.'})
        return

    try:
        socketio.emit('video_progress', {'video_id': video_id, 'status': 'processing', 'message': 'Iniciando processamento...'})
        
        transcript, metadata, json_path = youtube_handler.download_and_clean_transcript(url)

        if not transcript:
            error_msg = f"Não foi possível obter a transcrição para '{metadata.get('title', 'desconhecido')}'"
            socketio.emit('video_error', {'video_id': video_id, 'status': 'error', 'error': error_msg})
            return
        
        response = {
            "success": True,
            "video_id": metadata['video_id'],
            "title": metadata['title'],
            "thumbnail": metadata['thumbnail'],
            "transcript": transcript,
        }
        socketio.emit('video_complete', response)

    except Exception as e:
        logger.exception(f"Erro na tarefa de processamento de vídeo {url}: {e}")
        socketio.emit('video_error', {'video_id': video_id, 'status': 'error', 'error': str(e)})


def process_playlist_task(url: str):
    """
    Função executada em background para processar uma playlist inteira.
    """
    playlist_info = youtube_handler.get_playlist_info(url)
    if not playlist_info or not playlist_info.get('videos'):
        socketio.emit('playlist_error', {'error': 'Não foi possível extrair informações da playlist.'})
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
    youtube_handler.history_manager.add_entry(playlist_entry)
    
    socketio.emit('playlist_start', {
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
        
        socketio.emit('video_progress', {
            'playlist_id': playlist_id,
            'video_id': video_id,
            'title': video['title'],
            'status': 'processing',
            'message': f"Processando vídeo {i + 1} de {total_videos}...",
            'current_video': i + 1,
            'total_videos': total_videos
        })
        
        try:
            transcript, metadata, _ = youtube_handler.download_and_clean_transcript(video_url)
            if transcript:
                socketio.emit('video_complete', {
                    'playlist_id': playlist_id,
                    'video_id': video_id,
                    'status': 'success'
                })
                processed_count += 1
            else:
                raise Exception("Transcrição não encontrada.")
        except Exception as e:
            logger.error(f"Erro ao processar vídeo {video_url} da playlist: {e}")
            socketio.emit('video_error', {
                'playlist_id': playlist_id,
                'video_id': video_id,
                'status': 'error',
                'error': str(e)
            })
            error_count += 1
        
        youtube_handler._add_random_delay()

    socketio.emit('playlist_complete', {
        'playlist_id': playlist_id,
        'status': 'complete',
        'processed_count': processed_count,
        'error_count': error_count
    })
    
# --- (Rotas /get_playlist_details e /download_playlist permanecem as mesmas) ---
@app.route('/get_playlist_details/<playlist_id>', methods=['GET'])
def get_playlist_details(playlist_id):
    """Retorna os detalhes de uma playlist e o status de cada vídeo."""
    details = youtube_handler.get_playlist_details(playlist_id)
    if not details:
        return jsonify({"success": False, "error": "Playlist não encontrada"}), 404
    return jsonify({"success": True, "details": details})


@app.route('/download_playlist/<playlist_id>', methods=['GET'])
def download_playlist(playlist_id):
    """Cria e envia um arquivo ZIP com as transcrições da playlist."""
    try:
        zip_buffer, zip_filename = youtube_handler.create_playlist_zip(playlist_id)
        if not zip_buffer:
            return jsonify({"success": False, "error": "Não foi possível gerar o arquivo ZIP."}), 404
            
        return send_file(
            zip_buffer,
            mimetype='application/zip',
            as_attachment=True,
            download_name=zip_filename
        )
    except Exception as e:
        logger.exception(f"Erro ao gerar ZIP para playlist {playlist_id}: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/download_transcription/<video_id>', methods=['GET'])
def download_transcription(video_id):
    """
    Rota para baixar a transcrição em TXT
    """
    transcriptions_dir = youtube_handler.output_dir
    filename = f"{video_id}.json"
    filepath = os.path.join(transcriptions_dir, filename)

    if not os.path.exists(filepath):
        logger.error(f"Nenhuma transcrição encontrada para o vídeo {video_id}")
        return jsonify({
            "success": False,
            "error": "Transcrição não encontrada"
        }), 404
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        txt_content = f"Transcrição do vídeo: {data['title']}\n"
        txt_content += f"ID do vídeo: {data['video_id']}\n"
        txt_content += f"Gerado em: {data['created_at']}\n\n"
        txt_content += "===== CONTEÚDO DO VÍDEO =====\n\n"
        txt_content += data['transcript']
        
        safe_title = youtube_handler.sanitize_filename(data['title'])
        txt_filename = f"{safe_title[:50]}_transcricao.txt"
        
        temp_txt = BytesIO()
        temp_txt.write(txt_content.encode('utf-8'))
        temp_txt.seek(0)
        
        return send_file(
            temp_txt,
            mimetype='text/plain',
            as_attachment=True,
            download_name=txt_filename
        )
    
    except Exception as e:
        logger.exception(f"Erro ao gerar arquivo TXT para {video_id}: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"Erro ao gerar arquivo de transcrição: {str(e)}"
        }), 500

@app.route('/get_transcription/<video_id>', methods=['GET'])
def get_transcription(video_id):
    """
    Rota para obter a transcrição completa em JSON ao clicar em um item do histórico
    """
    transcriptions_dir = youtube_handler.output_dir
    filepath = os.path.join(transcriptions_dir, f"{video_id}.json")

    if not os.path.exists(filepath):
        return jsonify({"success": False, "error": "Transcrição não encontrada"}), 404
    
    try:
        return send_file(filepath, mimetype='application/json')
    except Exception as e:
        logger.exception(f"Erro ao enviar transcrição para {video_id}: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"Erro ao enviar transcrição: {str(e)}"
        }), 500

@app.route('/get_history', methods=['GET'])
def get_history():
    """
    Retorna o histórico de transcrições do arquivo history.json.
    """
    try:
        # MODIFICADO: Recarrega e sincroniza o histórico a cada chamada para refletir exclusões manuais
        history_data = youtube_handler.history_manager._load_and_sync_history()
        return jsonify({
            "success": True,
            "history": history_data
        })
    except Exception as e:
        logger.exception(f"Erro ao obter o histórico: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"Erro interno ao obter o histórico: {str(e)}"
        }), 500

# MODIFICADO: Rota unificada para exclusão de qualquer tipo de entrada
@app.route('/delete_entry/<entry_id>', methods=['DELETE'])
def delete_entry_route(entry_id):
    """
    Exclui uma entrada (vídeo ou playlist) do histórico e os arquivos JSON associados.
    """
    if not entry_id:
        return jsonify({"success": False, "error": "ID da entrada não fornecido"}), 400

    try:
        # Remove a entrada do history.json e obtém a lista de arquivos a serem deletados
        json_filenames_to_delete = youtube_handler.history_manager.remove_entry(entry_id)

        deleted_count = 0
        for filename in json_filenames_to_delete:
            filepath_to_delete = os.path.join(youtube_handler.output_dir, filename)
            if os.path.exists(filepath_to_delete):
                os.remove(filepath_to_delete)
                logger.info(f"Arquivo de transcrição {filepath_to_delete} deletado com sucesso.")
                deleted_count += 1
            else:
                logger.warning(f"Arquivo {filepath_to_delete} não encontrado para exclusão.")
        
        return jsonify({"success": True, "message": f"{deleted_count} arquivo(s) removido(s) com sucesso."})

    except Exception as e:
        logger.exception(f"Erro ao deletar a entrada {entry_id}: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"Erro interno ao deletar a entrada: {str(e)}"
        }), 500

if __name__ == '__main__':
    os.makedirs('data/transcriptions', exist_ok=True)
    logger.info("Iniciando servidor com Socket.IO na porta 5000...")
    socketio.run(app, debug=True, port=5000, allow_unsafe_werkzeug=True)