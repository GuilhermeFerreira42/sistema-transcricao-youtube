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
    transcriptions_dir = youtube_handler.output_dir
    
    # Encontrar o arquivo JSON com este video_id
    filename = f"{video_id}.json"
    filepath = os.path.join(transcriptions_dir, filename)

    if not os.path.exists(filepath):
        logger.error(f"Nenhuma transcrição encontrada para o vídeo {video_id}")
        return jsonify({
            "success": False,
            "error": "Transcrição não encontrada"
        }), 404
    
    try:
        # Carregar o arquivo JSON
        with open(filepath, 'r', encoding='utf-8') as f:
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
    Rota para obter a transcrição completa em JSON ao clicar em um item do histórico
    """
    transcriptions_dir = youtube_handler.output_dir
    filepath = os.path.join(transcriptions_dir, f"{video_id}.json")

    if not os.path.exists(filepath):
        return jsonify({"success": False, "error": "Transcrição não encontrada"}), 404
    
    try:
        # Envia o arquivo JSON
        return send_file(filepath, mimetype='application/json')
    except Exception as e:
        logger.exception(f"Erro ao enviar transcrição para {video_id}: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"Erro ao enviar transcrição: {str(e)}"
        }), 500

# --- NOVAS ROTAS ADICIONADAS ---

@app.route('/get_history', methods=['GET'])
def get_history():
    """
    NOVA ROTA: Retorna o histórico de transcrições do arquivo history.json.
    """
    try:
        history_data = youtube_handler.history_manager.get_history()
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

@app.route('/delete_transcription/<video_id>', methods=['DELETE'])
def delete_transcription_route(video_id):
    """
    NOVA ROTA: Exclui uma transcrição do histórico e o arquivo JSON associado.
    """
    if not video_id:
        return jsonify({"success": False, "error": "ID do vídeo não fornecido"}), 400

    try:
        # Remove a entrada do history.json e obtém o nome do arquivo a ser deletado
        json_filename_to_delete = youtube_handler.history_manager.remove_entry(video_id)

        if json_filename_to_delete:
            # Monta o caminho completo para o arquivo JSON
            filepath_to_delete = os.path.join(youtube_handler.output_dir, json_filename_to_delete)
            
            # Tenta deletar o arquivo físico
            if os.path.exists(filepath_to_delete):
                os.remove(filepath_to_delete)
                logger.info(f"Arquivo de transcrição {filepath_to_delete} deletado com sucesso.")
            else:
                logger.warning(f"Arquivo {filepath_to_delete} não encontrado para exclusão, mas a entrada do histórico foi removida.")
        
        return jsonify({"success": True, "message": "Transcrição removida com sucesso."})

    except Exception as e:
        logger.exception(f"Erro ao deletar a transcrição para {video_id}: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"Erro interno ao deletar a transcrição: {str(e)}"
        }), 500

# --------------------------------

if __name__ == '__main__':
    # Certifique-se de que o diretório de transcrições existe
    os.makedirs('data/transcriptions', exist_ok=True)
    
    logger.info("Iniciando servidor na porta 5000...")
    app.run(debug=True, port=5000)