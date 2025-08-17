"""
Blueprint de rotas de download e detalhes de transcrição/playlist
"""
from flask import Blueprint, request, jsonify, send_file, current_app
import os
import json
from io import BytesIO
import logging
from utils import sanitize_filename

download_bp = Blueprint('download', __name__)
logger = logging.getLogger('download_routes')

@download_bp.route('/get_playlist_details/<playlist_id>', methods=['GET'])
def get_playlist_details(playlist_id):
    """Retorna os detalhes de uma playlist e o status de cada vídeo."""
    youtube_handler = current_app.youtube_handler
    details = youtube_handler.get_playlist_details(playlist_id)
    if not details:
        return jsonify({"success": False, "error": "Playlist não encontrada"}), 404
    return jsonify({"success": True, "details": details})

@download_bp.route('/download_playlist/<playlist_id>', methods=['GET'])
def download_playlist(playlist_id):
    """Cria e envia um arquivo ZIP com as transcrições da playlist."""
    youtube_handler = current_app.youtube_handler
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

@download_bp.route('/download_transcription/<video_id>', methods=['GET'])
def download_transcription(video_id):
    """
    Rota para baixar a transcrição em TXT
    """
    youtube_handler = current_app.youtube_handler
    transcriptions_dir = youtube_handler.output_dir
    filename = f"{video_id}.json"
    filepath = os.path.join(transcriptions_dir, filename)
    if not os.path.exists(filepath):
        logger.error(f"Nenhuma transcrição encontrada para o vídeo {video_id}")
        return jsonify({"success": False, "error": "Transcrição não encontrada"}), 404
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        txt_content = f"Transcrição do vídeo: {data['title']}\n"
        txt_content += f"ID do vídeo: {data['video_id']}\n"
        txt_content += f"Gerado em: {data['created_at']}\n\n"
        txt_content += "===== CONTEÚDO DO VÍDEO =====\n\n"
        txt_content += data['transcript']
        safe_title = sanitize_filename(data['title'])
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
        return jsonify({"success": False, "error": f"Erro ao gerar arquivo de transcrição: {str(e)}"}), 500

@download_bp.route('/get_transcription/<video_id>', methods=['GET'])
def get_transcription(video_id):
    """
    Rota para obter a transcrição completa em JSON ao clicar em um item do histórico
    """
    youtube_handler = current_app.youtube_handler
    transcriptions_dir = youtube_handler.output_dir
    filepath = os.path.join(transcriptions_dir, f"{video_id}.json")
    if not os.path.exists(filepath):
        return jsonify({"success": False, "error": "Transcrição não encontrada"}), 404
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        # Responde com os campos esperados pelo frontend
        return jsonify({
            "success": True,
            "video_id": data.get("video_id"),
            "title": data.get("title"),
            "transcript": data.get("transcript"),
            "metadata": data.get("metadata", {}),
            "thumbnail": data.get("metadata", {}).get("thumbnail", "")
        })
    except Exception as e:
        logger.exception(f"Erro ao enviar transcrição para {video_id}: {str(e)}")
        return jsonify({"success": False, "error": f"Erro ao enviar transcrição: {str(e)}"}), 500
