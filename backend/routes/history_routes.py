"""
Blueprint de rotas de histórico
"""
from flask import Blueprint, request, jsonify, current_app
import logging
import os
from services.history_service import HistoryService

history_bp = Blueprint('history', __name__)

@history_bp.route('/get_history', methods=['GET'])
def get_history():
    """
    Retorna o histórico de transcrições do arquivo history.json.
    """
    history_service = HistoryService(current_app.youtube_handler.history_manager, current_app.youtube_handler.output_dir, logging.getLogger('history_routes'))
    try:
        history_data = history_service.get_history()
        return jsonify({"success": True, "history": history_data})
    except Exception as e:
        history_service.logger.exception(f"Erro ao obter o histórico: {str(e)}")
        return jsonify({"success": False, "error": f"Erro interno ao obter o histórico: {str(e)}"}), 500

@history_bp.route('/delete_entry/<entry_id>', methods=['DELETE'])
def delete_entry_route(entry_id):
    """
    Exclui uma entrada (vídeo ou playlist) do histórico e os arquivos JSON associados.
    """
    history_service = HistoryService(current_app.youtube_handler.history_manager, current_app.youtube_handler.output_dir, logging.getLogger('history_routes'))
    if not entry_id:
        return jsonify({"success": False, "error": "ID da entrada não fornecido"}), 400
    try:
        deleted_count = history_service.delete_entry(entry_id)
        return jsonify({"success": True, "message": f"{deleted_count} arquivo(s) removido(s) com sucesso."})
    except Exception as e:
        history_service.logger.exception(f"Erro ao deletar a entrada {entry_id}: {str(e)}")
        return jsonify({"success": False, "error": f"Erro interno ao deletar a entrada: {str(e)}"}), 500
