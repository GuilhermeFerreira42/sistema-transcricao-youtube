# backend/app.py
from flask import Flask, request, jsonify, send_file, render_template
import os
import logging
import json
from youtube_handler import YouTubeHandler

# Configuração do logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('app')

app = Flask(__name__, 
            template_folder='../frontend/templates',
            static_folder='../frontend/static')

# Inicializar o handler do YouTube
youtube_handler = YouTubeHandler()

@app.route('/')
def index():
    """Renderiza a página principal"""
    return render_template('index.html')

@app.route('/process_youtube_video', methods=['POST'])
def process_youtube_video():
    """
    Rota para processar um vídeo do YouTube
    Espera um JSON com {"url": "URL_DO_VIDEO"}
    """
    data = request.get_json()
    
    if not data or 'url' not in data:
        logger.error("Requisição inválida: URL não fornecida")
        return jsonify({
            "success": False,
            "error": "URL do vídeo não fornecida"
        }), 400
    
    url = data['url']
    logger.info(f"Processando vídeo do YouTube: {url}")
    
    try:
        # Processar o vídeo
        transcript, metadata, json_path = youtube_handler.download_and_clean_transcript(url)
        
        if not transcript:
            error_msg = f"Não foi possível processar as legendas do vídeo '{metadata.get('title', 'desconhecido')}'"
            logger.error(error_msg)
            return jsonify({
                "success": False,
                "error": error_msg
            }), 400
        
        # Preparar resposta
        response = {
            "success": True,
            "video_id": metadata['video_id'],
            "title": metadata['title'],
            "thumbnail": metadata['thumbnail'],
            "transcript": transcript,
            "chunks": youtube_handler.split_transcript_into_chunks(transcript),
            "metadata": metadata
        }
        
        return jsonify(response)
    
    except Exception as e:
        logger.exception(f"Erro ao processar vídeo {url}: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"Erro interno ao processar o vídeo: {str(e)}"
        }), 500

@app.route('/download_transcription/<video_id>', methods=['GET'])
def download_transcription(video_id):
    """
    Rota para baixar a transcrição em TXT
    """
    # Garantir que o diretório de transcrições exista
    transcriptions_dir = youtube_handler.output_dir
    os.makedirs(transcriptions_dir, exist_ok=True)
    
    # Encontrar o arquivo JSON mais recente com este video_id
    matching_files = []
    
    for filename in os.listdir(transcriptions_dir):
        if filename.startswith(video_id) and filename.endswith('.json'):
            filepath = os.path.join(transcriptions_dir, filename)
            matching_files.append((filepath, os.path.getctime(filepath)))
    
    if not matching_files:
        logger.error(f"Nenhuma transcrição encontrada para o vídeo {video_id}")
        return jsonify({
            "success": False,
            "error": "Transcrição não encontrada"
        }), 404
    
    # Pegar o arquivo mais recente
    latest_file = max(matching_files, key=lambda x: x[1])[0]
    
    try:
        # Carregar o arquivo JSON
        with open(latest_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Criar conteúdo TXT
        txt_content = f"Transcrição do vídeo: {data['title']}\n"
        txt_content += f"ID do vídeo: {data['video_id']}\n"
        txt_content += f"Gerado em: {data['created_at']}\n\n"
        txt_content += "===== CONTEÚDO DO VÍDEO =====\n\n"
        txt_content += data['transcript']
        
        # Sanitizar o título para o nome do arquivo
        safe_title = youtube_handler.sanitize_filename(data['title'])
        txt_filename = f"{safe_title[:50]}_transcricao.txt"
        
        # Criar um objeto BytesIO para evitar criar arquivo temporário no disco
        from io import BytesIO
        temp_txt = BytesIO()
        temp_txt.write(txt_content.encode('utf-8'))
        temp_txt.seek(0)
        
        # Enviar o arquivo para download diretamente da memória
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
    Rota para obter a transcrição completa em JSON
    """
    # Encontrar o arquivo JSON mais recente com este video_id
    transcriptions_dir = youtube_handler.output_dir
    matching_files = []
    
    for filename in os.listdir(transcriptions_dir):
        if filename.startswith(video_id) and filename.endswith('.json'):
            filepath = os.path.join(transcriptions_dir, filename)
            matching_files.append((filepath, os.path.getctime(filepath)))
    
    if not matching_files:
        logger.error(f"Nenhuma transcrição encontrada para o vídeo {video_id}")
        return jsonify({
            "success": False,
            "error": "Transcrição não encontrada"
        }), 404
    
    # Pegar o arquivo mais recente
    latest_file = max(matching_files, key=lambda x: x[1])[0]
    
    try:
        # Enviar o arquivo JSON
        return send_file(latest_file, mimetype='application/json')
    except Exception as e:
        logger.exception(f"Erro ao enviar transcrição para {video_id}: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"Erro ao enviar transcrição: {str(e)}"
        }), 500

if __name__ == '__main__':
    # Certifique-se de que o diretório de transcrições existe
    os.makedirs('data/transcriptions', exist_ok=True)
    
    logger.info("Iniciando servidor na porta 5000...")
    app.run(debug=True, port=5000)