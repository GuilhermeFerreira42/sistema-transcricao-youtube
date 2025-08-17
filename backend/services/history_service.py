"""
Serviço para gerenciamento do histórico de transcrições e playlists
"""
import os
import logging

class HistoryService:
    def __init__(self, history_manager, output_dir, logger=None):
        self.history_manager = history_manager
        self.output_dir = output_dir
        self.logger = logger or logging.getLogger('history_service')

    def get_history(self):
        """
        Retorna o histórico sincronizado
        """
        return self.history_manager._load_and_sync_history()

    def delete_entry(self, entry_id):
        """
        Remove uma entrada do histórico e os arquivos JSON associados
        """
        json_filenames_to_delete = self.history_manager.remove_entry(entry_id)
        deleted_count = 0
        for filename in json_filenames_to_delete:
            filepath_to_delete = os.path.join(self.output_dir, filename)
            if os.path.exists(filepath_to_delete):
                os.remove(filepath_to_delete)
                self.logger.info(f"Arquivo de transcrição {filepath_to_delete} deletado com sucesso.")
                deleted_count += 1
            else:
                self.logger.warning(f"Arquivo {filepath_to_delete} não encontrado para exclusão.")
        return deleted_count
