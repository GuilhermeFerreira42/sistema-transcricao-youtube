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

# ==============================================================================
# NOVA IMPORTAÇÃO: Adicionamos a biblioteca especializada em transcrições
# ==============================================================================
from youtube_transcript_api import YouTubeTranscriptApi


# Configuração do logger
logger = logging.getLogger('youtube_handler')
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# NOVO: Classe para gerenciar o índice do histórico
class HistoryManager:
    """Gerencia o arquivo de índice do histórico (history.json)."""
    def __init__(self, history_path):
        self.history_path = history_path
        self.history_data = self._load_history()

    def _load_history(self) -> List[Dict[str, Any]]:
        """Carrega o arquivo de histórico ou cria um novo se não existir."""
        if not os.path.exists(self.history_path):
            return []
        try:
            with open(self.history_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def _save_history(self):
        """Salva os dados do histórico no arquivo JSON."""
        with open(self.history_path, 'w', encoding='utf-8') as f:
            json.dump(self.history_data, f, ensure_ascii=False, indent=2)

    def add_entry(self, video_id: str, title: str, json_path: str):
        """Adiciona uma nova entrada ao histórico."""
        entry = {
            "video_id": video_id,
            "title": title,
            "json_path": os.path.basename(json_path), # Salva apenas o nome do arquivo
            "created_at": datetime.now().isoformat()
        }
        # Adiciona a entrada mais recente no topo da lista
        self.history_data.insert(0, entry)
        self._save_history()
        logger.info(f"Entrada adicionada ao histórico para o vídeo: {video_id}")

    def remove_entry(self, video_id: str) -> Optional[str]:
        """Remove uma entrada do histórico e retorna o caminho do arquivo JSON a ser deletado."""
        entry_to_remove = next((entry for entry in self.history_data if entry['video_id'] == video_id), None)
        
        if entry_to_remove:
            self.history_data.remove(entry_to_remove)
            self._save_history()
            logger.info(f"Entrada removida do histórico para o vídeo: {video_id}")
            return entry_to_remove.get('json_path')
        return None

    def get_history(self) -> List[Dict[str, Any]]:
        """Retorna todos os dados do histórico."""
        return self.history_data

class YouTubeHandler:
    """Classe responsável por todas as operações relacionadas ao YouTube."""
    
    # MODIFICADO: A função __init__ agora calcula o caminho absoluto
    def __init__(self):
        """
        Inicializa o handler com diretório de saída para armazenar transcrições.
        Calcula o caminho absoluto para a pasta 'data' para evitar erros.
        """
        # Caminho para o diretório atual do script (backend)
        backend_dir = os.path.dirname(os.path.abspath(__file__))
        # Caminho para o diretório raiz do projeto (um nível acima do backend)
        project_root = os.path.dirname(backend_dir)
        # Caminho para o diretório de transcrições
        output_dir_path = os.path.join(project_root, 'data', 'transcriptions')

        self.output_dir = os.path.normpath(output_dir_path)
        os.makedirs(self.output_dir, exist_ok=True)
        logger.info(f"Diretório de transcrições configurado: {self.output_dir}")
        
        self.headers = self._get_realistic_headers()
        self.history_manager = HistoryManager(os.path.join(self.output_dir, 'history.json'))

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

    def validate_youtube_url(self, url: str) -> bool:
        """Valida se a URL fornecida é um link válido do YouTube"""
        youtube_regex = (
            r'(https?://)?(www\.)?'
            '(youtube|youtu|youtube-nocookie)\.(com|be)/'
            '(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'
        )
        return bool(re.match(youtube_regex, url))

    def extract_video_id(self, url: str) -> Optional[str]:
        """Extrai o ID do vídeo da URL do YouTube"""
        patterns = [
            r'(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=))([^"&?\/\s]{11})',
            r'(?:youtu\.be\/|v\/|vi\/|u\/\w\/|embed\/)([^"&?\/\s]{11})'
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None

    def _get_video_metadata(self, url: str, video_id: str) -> Dict:
        """Obtém apenas os metadados do vídeo usando yt-dlp."""
        logger.info(f"Buscando metadados para o vídeo: {video_id}")
        try:
            ydl_opts = {
                'skip_download': True,
                'quiet': True,
                'no_warnings': True,
                'force_generic_extractor': False
            }
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
                return metadata
        except Exception as e:
            logger.error(f"Não foi possível obter metadados com yt-dlp para {video_id}: {e}")
            return {
                'video_id': video_id,
                'title': 'Título indisponível',
                'thumbnail': '',
                'duration': 0,
                'view_count': 0,
                'uploader': '',
                'upload_date': ''
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

    def sanitize_filename(self, filename: str) -> str:
        """Sanitiza o nome do arquivo para evitar caracteres inválidos."""
        sanitized = re.sub(r'[\\/*?:"<>|]', "", filename)
        sanitized = re.sub(r'\s+', '_', sanitized)
        return sanitized[:200]

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

        # NOVO: Adiciona a entrada ao histórico
        self.history_manager.add_entry(video_id, title, filepath)

        return filepath

    def download_and_clean_transcript(self, url: str) -> Tuple[Optional[str], Dict, Optional[str]]:
        """Função principal que coordena o download e limpeza da transcrição."""
        if not self.validate_youtube_url(url):
            logger.error(f"URL inválida: {url}")
            return None, {}, None

        # MODIFICADO: Usa a função de extração da própria classe
        video_id = self.extract_video_id(url)
        if not video_id:
            logger.error(f"ID do vídeo não encontrado na URL: {url}")
            return None, {}, None
            
        logger.info(f"Iniciando processamento do vídeo: {url}")

        metadata = self._get_video_metadata(url, video_id)
        
        # --- MÉTODO 1: API Especializada (youtube-transcript-api) ---
        try:
            logger.info(f"Tentando extrair com 'youtube-transcript-api' para {video_id}...")
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['pt', 'pt-BR', 'en'])
            
            raw_transcript = " ".join([item['text'] for item in transcript_list])
            
            cleaned_transcript = re.sub(r'\s+', ' ', raw_transcript).strip()
            
            logger.info(f"Transcrição obtida com sucesso via 'youtube-transcript-api' para {video_id}")

            chunks = self.split_transcript_into_chunks(cleaned_transcript)
            # MODIFICADO: Usa o video_id extraído consistentemente
            json_path = self.save_transcription_to_json(
                video_id, metadata['title'], cleaned_transcript, chunks, metadata
            )
            return cleaned_transcript, metadata, json_path

        except Exception as api_error:
            logger.warning(f"Falha ao usar 'youtube-transcript-api': {api_error}. Ativando método fallback com yt-dlp.")

        # --- MÉTODO 2: Fallback com yt-dlp (se o primeiro falhar) ---
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