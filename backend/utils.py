# backend/utils.py
import re
import os
import uuid
import logging

logger = logging.getLogger('utils')

def sanitize_filename(filename):
    """
    Sanitiza o nome do arquivo para evitar caracteres inválidos
    
    Args:
        filename (str): Nome do arquivo original
        
    Returns:
        str: Nome do arquivo sanitizado
    """
    # Remover caracteres inválidos para nomes de arquivo
    sanitized = re.sub(r'[\\/*?:"<>|]', "", filename)
    # Substituir espaços por underscores
    sanitized = re.sub(r'\s+', '_', sanitized)
    # Limitar o tamanho do nome do arquivo
    return sanitized[:200]

def generate_unique_id():
    """
    Gera um ID único usando UUID
    
    Returns:
        str: ID único
    """
    return str(uuid.uuid4())

def validate_youtube_url(url):
    """
    Valida se a URL fornecida é um link válido do YouTube
    
    Args:
        url (str): URL a ser validada
        
    Returns:
        bool: True se for uma URL válida do YouTube, False caso contrário
    """
    youtube_regex = (
        r'(https?://)?(www\.)?'
        '(youtube|youtu|youtube-nocookie)\.(com|be)/'
        '(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'
    )
    
    return bool(re.match(youtube_regex, url))

def extract_video_id(url):
    """
    Extrai o ID do vídeo da URL do YouTube
    
    Args:
        url (str): URL do vídeo do YouTube
        
    Returns:
        Optional[str]: ID do vídeo se encontrado, None caso contrário
    """
    patterns = [
        r'(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=))([^"&?\/\s]{11})',
        r'(?:youtu\.be\/|v\/|vi\/|u\/\w\/|embed\/)([^"&?\/\s]{11})'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None