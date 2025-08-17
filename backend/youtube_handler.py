# backend/youtube_handler.py
import os
import re
import json
import yt_dlp
import uuid
import logging
import requests
import time
import random
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from io import BytesIO
import zipfile

import utils
from youtube_transcript_api import YouTubeTranscriptApi

# Configuração do logger
logger = logging.getLogger('youtube_handler')
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# MODIFICADO: Classe HistoryManager com lógica de sincronização e exclusão em cascata
class HistoryManager:
    """Gerencia o arquivo de índice do histórico (history.json) com validação de arquivos."""
    def __init__(self, history_path, transcriptions_dir):
        self.history_path = history_path
        self.transcriptions_dir = transcriptions_dir
        self.history_data = self._load_and_sync_history()

    def _load_and_sync_history(self) -> List[Dict[str, Any]]:
        """Carrega o histórico e o sincroniza com os arquivos físicos existentes."""
        if not os.path.exists(self.history_path):
            return []
        
        try:
            with open(self.history_path, 'r', encoding='utf-8') as f:
                history = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []

        synced_history = []
        history_changed = False
        for entry in history:
            entry_id = entry.get('id') or entry.get('video_id')
            if not entry_id:
                history_changed = True
                continue

            # Garante a padronização para 'id'
            if 'video_id' in entry and 'id' not in entry:
                entry['id'] = entry['video_id']
                del entry['video_id']
                history_changed = True

            # Verifica se os arquivos físicos existem
            if entry.get('type') == 'video':
                json_path = entry.get('json_path')
                if json_path and os.path.exists(os.path.join(self.transcriptions_dir, json_path)):
                    synced_history.append(entry)
                else:
                    logger.warning(f"Removendo entrada do histórico para vídeo não encontrado: {entry['id']}")
                    history_changed = True
            elif entry.get('type') == 'playlist':
                video_ids = entry.get('video_ids', [])
                # Verifica se ao menos um vídeo da playlist existe
                valid_videos = [vid for vid in video_ids if os.path.exists(os.path.join(self.transcriptions_dir, f"{vid}.json"))]
                if valid_videos:
                    # Atualiza a lista de vídeos válidos
                    entry['video_ids'] = valid_videos
                    synced_history.append(entry)
                else:
                    logger.warning(f"Removendo playlist do histórico sem vídeos válidos: {entry['id']}")
                    history_changed = True
            else:
                synced_history.append(entry)

        if history_changed:
            self.history_data = synced_history
            # Salva o histórico limpo para evitar checagens repetidas
            with open(self.history_path, 'w', encoding='utf-8') as f:
                json.dump(self.history_data, f, ensure_ascii=False, indent=2)
        return synced_history

    def _save_history(self):
        """Salva os dados do histórico no arquivo JSON."""
        with open(self.history_path, 'w', encoding='utf-8') as f:
            json.dump(self.history_data, f, ensure_ascii=False, indent=2)

    def add_entry(self, entry_data: Dict[str, Any]):
        """Adiciona uma nova entrada (vídeo ou playlist) ao histórico."""
        required_keys = ['id', 'title', 'type', 'created_at']
        if not all(key in entry_data for key in required_keys):
            logger.error(f"Tentativa de adicionar entrada de histórico inválida: {entry_data}")
            return

        self.history_data.insert(0, entry_data)
        self._save_history()
        logger.info(f"Entrada do tipo '{entry_data['type']}' adicionada ao histórico: {entry_data['id']}")

    def remove_entry(self, entry_id: str) -> List[str]:
        """Remove uma entrada do histórico e retorna uma lista de arquivos JSON para deletar."""
        # Sempre recarrega o histórico do disco para garantir consistência
        self.history_data = self._load_and_sync_history()
        entry_to_remove = next((entry for entry in self.history_data if (entry.get('id') or entry.get('video_id')) == entry_id), None)
        files_to_delete = []
        if entry_to_remove:
            entry_type = entry_to_remove.get('type')
            if entry_type == 'video':
                if entry_to_remove.get('json_path'):
                    files_to_delete.append(entry_to_remove['json_path'])
            elif entry_type == 'playlist':
                video_ids = entry_to_remove.get('video_ids', [])
                for video_id in video_ids:
                    files_to_delete.append(f"{video_id}.json")
            self.history_data.remove(entry_to_remove)
            self._save_history()
            logger.info(f"Entrada '{entry_id}' removida do histórico.")
        return files_to_delete

    def get_history(self) -> List[Dict[str, Any]]:
        """Retorna todos os dados do histórico já sincronizado."""
        return self.history_data


class YouTubeHandler:
    """Classe responsável por todas as operações relacionadas ao YouTube."""
    
    def __init__(self):
        """
        Inicializa o handler com diretório de saída para armazenar transcrições.
        Calcula o caminho absoluto para a pasta 'data' para evitar erros.
        """
        backend_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(backend_dir)
        output_dir_path = os.path.join(project_root, 'data', 'transcriptions')

        self.output_dir = os.path.normpath(output_dir_path)
        os.makedirs(self.output_dir, exist_ok=True)
        logger.info(f"Diretório de transcrições configurado: {self.output_dir}")
        
        self.headers = self._get_realistic_headers()
        self.history_manager = HistoryManager(
            history_path=os.path.join(self.output_dir, 'history.json'),
            transcriptions_dir=self.output_dir
        )

    def get_playlist_info(self, url: str) -> Optional[Dict[str, Any]]:
        """Extrai informações de uma playlist, incluindo os vídeos contidos."""
        logger.info(f"Extraindo informações da playlist: {url}")
        ydl_opts = {
            'extract_flat': 'in_playlist', # Extrai informações dos vídeos sem processá-los
            'quiet': True,
            'no_warnings': True,
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if info and 'entries' in info:
                    playlist_info = {
                        'id': info.get('id'),
                        'title': info.get('title', 'Playlist sem título'),
                        'uploader': info.get('uploader'),
                        'type': 'playlist',
                        'videos': []
                    }
                    for video_entry in info['entries']:
                        if video_entry:
                            playlist_info['videos'].append({
                                'id': video_entry.get('id'),
                                'title': video_entry.get('title'),
                                'url': video_entry.get('url'),
                            })
                    return playlist_info
        except Exception as e:
            logger.error(f"Erro ao extrair informações da playlist {url}: {e}")
            return None
        return None
    
    def get_playlist_details(self, playlist_id: str) -> Optional[Dict[str, Any]]:
        """Obtém os detalhes de uma playlist e o status de cada vídeo nela."""
        playlist_entry = next((p for p in self.history_manager.get_history() if p['id'] == playlist_id and p['type'] == 'playlist'), None)
        if not playlist_entry:
            return None

        videos_details = []
        for video_id in playlist_entry.get('video_ids', []):
            video_filepath = os.path.join(self.output_dir, f"{video_id}.json")
            if os.path.exists(video_filepath):
                try:
                    with open(video_filepath, 'r', encoding='utf-8') as f:
                        video_data = json.load(f)
                        videos_details.append({
                            'id': video_id,
                            'title': video_data.get('title', 'Título desconhecido'),
                            'status': 'success'
                        })
                except Exception as e:
                    logger.error(f"Erro ao ler o arquivo JSON do vídeo {video_id}: {e}")
                    videos_details.append({'id': video_id, 'title': 'Erro ao ler dados', 'status': 'error'})
            else:
                # Se o arquivo JSON não existe, o vídeo falhou no processamento
                videos_details.append({'id': video_id, 'title': f'Vídeo {video_id}', 'status': 'error'})
        
        playlist_details = {
            "id": playlist_entry['id'],
            "title": playlist_entry['title'],
            "videos": videos_details
        }
        return playlist_details

    # --- FUNÇÃO MODIFICADA PARA FASE 4 ---
    def create_playlist_zip(self, playlist_id: str) -> Optional[Tuple[BytesIO, str]]:
        """
        Cria um arquivo ZIP em memória com as transcrições de uma playlist.
        O ZIP conterá arquivos .txt individuais para cada vídeo e um .txt consolidado.
        """
        playlist_details = self.get_playlist_details(playlist_id)
        if not playlist_details:
            return None

        zip_buffer = BytesIO()
        consolidated_txt_content = f"Transcrição consolidada da playlist: {playlist_details['title']}\n\n"
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for video in playlist_details.get('videos', []):
                if video['status'] == 'success':
                    json_filename = f"{video['id']}.json"
                    json_filepath = os.path.join(self.output_dir, json_filename)
                    
                    if os.path.exists(json_filepath):
                        try:
                            with open(json_filepath, 'r', encoding='utf-8') as f:
                                data = json.load(f)
                            
                            transcript_text = data.get('transcript', '')
                            video_title = data.get('title', 'Título desconhecido')
                            
                            # Adiciona o arquivo .txt individual ao ZIP
                            individual_txt_filename = f"{utils.sanitize_filename(video_title)[:100]}.txt"
                            zip_file.writestr(individual_txt_filename, transcript_text.encode('utf-8'))
                            
                            # Adiciona o conteúdo ao TXT consolidado
                            consolidated_txt_content += "="*80 + "\n"
                            consolidated_txt_content += f"VÍDEO: {video_title}\n"
                            consolidated_txt_content += f"ID: {data['video_id']}\n"
                            consolidated_txt_content += "="*80 + "\n\n"
                            consolidated_txt_content += transcript_text + "\n\n"

                        except Exception as e:
                            logger.error(f"Erro ao processar o arquivo {json_filename} para o ZIP: {e}")

            # Adiciona o arquivo TXT consolidado ao ZIP
            zip_file.writestr('transcricao_consolidada.txt', consolidated_txt_content.encode('utf-8'))

        zip_buffer.seek(0)
        safe_playlist_title = utils.sanitize_filename(playlist_details['title'])
        zip_filename = f"{safe_playlist_title[:50]}_transcricoes.zip"
        
        return zip_buffer, zip_filename

    def _get_realistic_headers(self) -> Dict[str, str]:
        """Gera headers HTTP que imitam um navegador real para evitar bloqueios"""
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0'
        ]
        user_agent = random.choice(user_agents)
        headers = {
            'User-Agent': user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        }
        return headers

    def _add_random_delay(self):
        """Adiciona um delay aleatório entre requisições para evitar detecção como bot"""
        delay = random.uniform(1.0, 3.0)
        logger.debug(f"Aguardando {delay:.2f} segundos antes da próxima requisição")
        time.sleep(delay)

    def _is_google_block(self, content: str) -> bool:
        """Verifica se o conteúdo indica que o Google bloqueou a requisição"""
        block_indicators = [
            "unusual traffic from your computer network",
            "Our systems have detected unusual traffic from your computer network",
            "sending automated queries"
        ]
        content_lower = content.lower()
        return any(indicator.lower() in content_lower for indicator in block_indicators)

    def _get_video_metadata(self, url, video_id):
        """
        Obtém metadados do vídeo usando yt_dlp.
        """
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'skip_download': True,
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return {
                    'video_id': video_id,
                    'title': info.get('title', 'Vídeo sem título'),
                    'thumbnail': info.get('thumbnail', ''),
                    'author': info.get('uploader', ''),
                    'duration': info.get('duration', 0),
                    'url': url
                }
        except Exception as e:
            logger.error(f"Erro ao obter metadados do vídeo {url}: {e}")
            return {
                'video_id': video_id,
                'title': 'Título desconhecido',
                'thumbnail': '',
                'author': '',
                'duration': 0,
                'url': url
            }

    def download_subtitles_fallback(self, url: str, video_id: str) -> Tuple[Optional[str], Dict]:
        """Tenta baixar legendas usando yt-dlp (MÉTODO FALLBACK)."""
        logger.info(f"Método fallback (yt-dlp) iniciado para o vídeo: {video_id}")
        
        ydl_opts = {
            'skip_download': True,
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitleslangs': ["pt", "pt-BR", "en"],
            'subformat': 'srt',
            'quiet': True,
            'no_warnings': True,
            'http_headers': self.headers,
            'retries': 3,
            'fragment_retries': 10,
            'sleep_interval': 2,
            'max_sleep_interval': 5,
            'verbose': False
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                metadata = {
                    'video_id': video_id,
                    'title': info.get('title', 'Vídeo sem título'),
                    'thumbnail': info.get('thumbnail', ''),
                    'duration': info.get('duration', 0),
                    'view_count': info.get('view_count', 0),
                    'uploader': info.get('uploader', ''),
                    'upload_date': info.get('upload_date', '')
                }

                for lang in ["pt", "pt-BR", "en"]:
                    sub_info = info.get('subtitles', {}).get(lang)
                    if not sub_info:
                        sub_info = info.get('automatic_captions', {}).get(lang)
                    
                    if sub_info:
                        for sub_format in sub_info:
                            if 'url' in sub_format:
                                self._add_random_delay()
                                response = requests.get(sub_format['url'], headers=self.headers, timeout=10)
                                if not self._is_google_block(response.text) and response.text.strip():
                                    logger.info(f"Legendas baixadas com sucesso via fallback para o idioma {lang}")
                                    return response.text, metadata
                
                logger.warning(f"Fallback yt-dlp não encontrou legendas para {video_id}")
                return None, metadata
        except Exception as e:
            logger.error(f"Erro crítico no fallback yt-dlp para {url}: {e}")
            return None, {}

    def clean_subtitles(self, raw_subtitles: str) -> str:
        """Limpa e formata o texto das legendas, tratando tanto JSON quanto VTT/SRT."""
        if self._is_google_block(raw_subtitles):
            logger.error("Conteúdo bloqueado pelo Google detectado.")
            return "Erro: O Google bloqueou a requisição."
        try:
            data = json.loads(raw_subtitles)
            if 'events' in data:
                transcript_parts = [seg['utf8'] for event in data['events'] if 'segs' in event for seg in event['segs'] if 'utf8' in seg]
                full_transcript = "".join(transcript_parts).replace('\n', ' ').strip()
                cleaned = re.sub(r'\s{2,}', ' ', full_transcript)
                logger.info("Transcrição limpa a partir do formato JSON.")
                return cleaned
        except (json.JSONDecodeError, TypeError):
            logger.info("Formato não é JSON, limpando como VTT/SRT.")
        
        cleaned = re.sub(r'WEBVTT.*\n', '', raw_subtitles)
        cleaned = re.sub(r'\d{2}:\d{2}:\d{2}[,.]\d{3} --> \d{2}:\d{2}:\d{2}[,.]\d{3}.*\n', '', cleaned)
        cleaned = re.sub(r'<\d{2}:\d{2}:\d{2}[,.]\d{3}>', '', cleaned)
        cleaned = re.sub(r'<c[^>]*>', '', cleaned)
        cleaned = re.sub(r'</c>', '', cleaned)
        cleaned = re.sub(r'<[^>]+>', '', cleaned)
        
        cleaned = re.sub(r'\[.*?\]', '', cleaned)
        cleaned = re.sub(r'\n\s*\n', '\n\n', cleaned)
        cleaned = re.sub(r'\s{2,}', ' ', cleaned)
        return cleaned.strip()

    def split_transcript_into_chunks(self, transcript: str, words_per_chunk: int = 300) -> List[str]:
        """Divide a transcrição em blocos menores."""
        words = transcript.split()
        return [' '.join(words[i:i + words_per_chunk]) for i in range(0, len(words), words_per_chunk)]

    def save_transcription_to_json(self, video_id: str, title: str, transcript: str, 
                                   chunks: List[str], metadata: Dict) -> str:
        """Salva a transcrição em um arquivo JSON e atualiza o histórico."""
        transcription_id = str(uuid.uuid4())
        data = {
            "transcription_id": transcription_id,
            "video_id": video_id,
            "title": title,
            "transcript": transcript,
            "chunks": chunks,
            "metadata": metadata,
            "created_at": datetime.now().isoformat(),
            "format_version": "2.0"
        }
        
        filename = f"{video_id}.json"
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Transcrição salva em: {filepath}")

        # MODIFICADO: Cria a entrada para o histórico usando a chave 'id' padronizada.
        history_entry = {
            "id": video_id,
            "type": "video",
            "title": title,
            "json_path": os.path.basename(filepath),
            "created_at": data["created_at"]
        }
        self.history_manager.add_entry(history_entry)

        return filepath

    def download_and_clean_transcript(self, url: str) -> Tuple[Optional[str], Dict, Optional[str]]:
        """Função principal que coordena o download e limpeza da transcrição."""
        if not utils.validate_youtube_url(url):
            logger.error(f"URL inválida: {url}")
            return None, {}, None

        video_id = utils.extract_video_id(url)
        if not video_id:
            logger.error(f"ID do vídeo não encontrado na URL: {url}")
            return None, {}, None
            
        logger.info(f"Iniciando processamento do vídeo: {url}")

        metadata = self._get_video_metadata(url, video_id)
        
        try:
            logger.info(f"Tentando extrair com 'youtube-transcript-api' para {video_id}...")
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['pt', 'pt-BR', 'en'])
            
            raw_transcript = " ".join([item['text'] for item in transcript_list])
            
            cleaned_transcript = re.sub(r'\s+', ' ', raw_transcript).strip()
            
            logger.info(f"Transcrição obtida com sucesso via 'youtube-transcript-api' para {video_id}")

            chunks = self.split_transcript_into_chunks(cleaned_transcript)
            json_path = self.save_transcription_to_json(
                video_id, metadata['title'], cleaned_transcript, chunks, metadata
            )
            return cleaned_transcript, metadata, json_path

        except Exception as api_error:
            logger.warning(f"Falha ao usar 'youtube-transcript-api': {api_error}. Ativando método fallback com yt-dlp.")

        raw_transcript, fallback_metadata = self.download_subtitles_fallback(url, video_id)
        
        if fallback_metadata and fallback_metadata.get('title'):
            metadata = fallback_metadata
        
        if not raw_transcript:
            logger.error(f"Todos os métodos falharam. Não foi possível obter legendas para: {url}")
            return None, metadata, None

        cleaned_transcript = self.clean_subtitles(raw_transcript)
        
        if not cleaned_transcript.strip() or "Erro: O Google bloqueou" in cleaned_transcript:
            logger.error(f"A transcrição limpa está vazia ou bloqueada para o vídeo: {url}")
            return None, metadata, None
        
        chunks = self.split_transcript_into_chunks(cleaned_transcript)
        json_path = self.save_transcription_to_json(
            video_id, metadata['title'], cleaned_transcript, chunks, metadata
        )
        
        return cleaned_transcript, metadata, json_path