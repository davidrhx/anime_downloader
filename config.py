"""
Anime Downloader - Configuración (Versión Mejorada)
Variables configurables del proyecto con manejo de rate limiting
"""

import os
from pathlib import Path

class Config:
    """Configuración principal del Anime Downloader"""
    
    # === Configuración de Descarga ===
    DEFAULT_QUALITY = '720p'  # Calidad por defecto (480p, 720p, 1080p, best)
    DOWNLOAD_PATH = str(Path.home() / 'Downloads' / 'Anime')  # Directorio de descarga por defecto
    MAX_RETRIES = 3  # Número máximo de reintentos por descarga
    CONCURRENT_DOWNLOADS = 1  # Reducido para evitar rate limiting
    RETRY_DELAY = 2  # Segundos de espera entre reintentos
    
    # === Configuración de Red ===
    TIMEOUT = 30  # Timeout para requests en segundos
    USER_AGENT = (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
        '(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    )
    MAX_CONNECTIONS = 3  # Reducido para evitar rate limiting
    
    # === Configuración de Rate Limiting ===
    RATE_LIMIT_DELAY = 1  # Delay entre requests en segundos
    MAX_DOWNLOAD_RATE = '2M'  # Velocidad máxima para evitar detección
    USE_RATE_LIMITING = True  # Activar rate limiting por defecto
    
    # === Configuración de Subtítulos (MEJORADA) ===
    DOWNLOAD_SUBTITLES = True  # Descargar subtítulos automáticamente
    SUBTITLE_LANGUAGES = ['es']  # Solo español por defecto para evitar rate limiting
    EMBED_SUBTITLES = False  # Desactivar embedding para evitar problemas
    IGNORE_SUBTITLE_ERRORS = True  # Continuar descarga aunque fallen subtítulos
    
    # === Configuración de Archivos ===
    ALLOWED_EXTENSIONS = ['.mp4', '.mkv', '.avi', '.webm', '.m4v']
    MAX_FILENAME_LENGTH = 200  # Longitud máxima para nombres de archivo
    MIN_FILE_SIZE = 10 * 1024 * 1024  # Tamaño mínimo de archivo (10MB)
    MAX_FILE_SIZE = 5 * 1024 * 1024 * 1024  # Tamaño máximo de archivo (5GB)
    
    # === Configuración de Metadatos ===
    DOWNLOAD_THUMBNAIL = False  # Desactivar para evitar rate limiting
    SAVE_INFO_JSON = False  # Guardar información en JSON
    ADD_METADATA = False  # Desactivar metadatos para simplicidad
    
    # === Configuración de GUI ===
    WINDOW_WIDTH = 800
    WINDOW_HEIGHT = 600
    THEME = 'default'  # Tema de la interfaz gráfica
    UPDATE_INTERVAL = 1000  # Intervalo más largo para evitar spam
    
    # === Configuración de Logging ===
    LOG_LEVEL = 'INFO'  # Nivel de logging (DEBUG, INFO, WARNING, ERROR)
    LOG_FILE = None  # Archivo de log (None para no guardar archivo)
    LOG_MAX_SIZE = 10 * 1024 * 1024  # Tamaño máximo del archivo de log (10MB)
    LOG_BACKUP_COUNT = 3  # Número de archivos de backup del log
    
    # === Headers mejorados para evitar detección ===
    HEADERS = {
        'User-Agent': USER_AGENT,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'DNT': '1',  # Do Not Track
        'Upgrade-Insecure-Requests': '1'
    }
    
    # === Configuración específica para YouTube ===
    YOUTUBE_CONFIG = {
        'format': 'best[height<=720]',  # Formato conservador
        'writesubtitles': False,  # Desactivar subtítulos automáticos
        'writeautomaticsub': False,  # Desactivar subtítulos auto-generados
        'subtitleslangs': [],  # Sin idiomas de subtítulos por defecto
        'embed_subs': False,  # No incrustar subtítulos
        'writethumbnail': False,  # No descargar miniaturas
        'writeinfojson': False,  # No guardar info JSON
        'ignoreerrors': True,  # Ignorar errores no críticos
        'no_warnings': True,  # Reducir warnings
        'extract_flat': False,
        'sleep_interval': 1,  # Pausa entre descargas
        'max_sleep_interval': 3,  # Pausa máxima aleatoria
        'sleep_interval_subtitles': 2,  # Pausa específica para subtítulos
    }
    
    # === Configuración de Calidad ===
    QUALITY_PREFERENCES = {
        '480p': {
            'height': 480,
            'format': 'best[height<=480][ext=mp4]/best[height<=480]',
            'description': 'Calidad estándar (480p)'
        },
        '720p': {
            'height': 720,
            'format': 'best[height<=720][ext=mp4]/best[height<=720]',
            'description': 'Alta calidad (720p HD)'
        },
        '1080p': {
            'height': 1080,
            'format': 'best[height<=1080][ext=mp4]/best[height<=1080]',
            'description': 'Muy alta calidad (1080p Full HD)'
        },
        'best': {
            'height': 9999,
            'format': 'best[ext=mp4]/best',
            'description': 'Mejor calidad disponible'
        }
    }
    
    @classmethod
    def get_ydl_config_safe(cls, quality='720p'):
        """Retorna configuración segura para yt-dlp que evita rate limiting"""
        config = {
            # Formato de video
            'format': cls.QUALITY_PREFERENCES[quality]['format'],
            'outtmpl': '%(title)s.%(ext)s',
            
            # Desactivar funciones que causan rate limiting
            'writesubtitles': False,
            'writeautomaticsub': False,
            'writethumbnail': False,
            'writeinfojson': False,
            'embed_subs': False,
            
            # Configuración de red conservadora
            'socket_timeout': cls.TIMEOUT,
            'retries': cls.MAX_RETRIES,
            'ignoreerrors': True,
            'no_warnings': False,
            
            # Rate limiting
            'sleep_interval': cls.RATE_LIMIT_DELAY,
            'max_sleep_interval': cls.RATE_LIMIT_DELAY * 3,
            
            # Headers para evitar detección
            'http_headers': cls.HEADERS,
            
            # Preferir formatos estables
            'prefer_ffmpeg': True,
            'keepvideo': False,
        }
        
        # Solo agregar rate limiting si está activado
        if cls.USE_RATE_LIMITING:
            config['ratelimit'] = cls.MAX_DOWNLOAD_RATE
        
        return config
    
    @classmethod
    def get_ydl_config_with_subtitles(cls, quality='720p', subtitle_langs=['es']):
        """Configuración con subtítulos - usar con cuidado"""
        config = cls.get_ydl_config_safe(quality)
        
        # Solo activar si se solicita explícitamente
        if subtitle_langs and cls.DOWNLOAD_SUBTITLES:
            config.update({
                'writesubtitles': True,
                'subtitleslangs': subtitle_langs,
                'ignoreerrors': cls.IGNORE_SUBTITLE_ERRORS,  # Continuar si fallan subtítulos
                'sleep_interval_subtitles': 2,  # Pausa extra para subtítulos
            })
        
        return config
    
    @classmethod
    def load_from_env(cls):
        """Carga configuración desde variables de entorno"""
        cls.DEFAULT_QUALITY = os.getenv('ANIME_QUALITY', cls.DEFAULT_QUALITY)
        cls.DOWNLOAD_PATH = os.getenv('ANIME_DOWNLOAD_PATH', cls.DOWNLOAD_PATH)
        cls.MAX_RETRIES = int(os.getenv('ANIME_MAX_RETRIES', cls.MAX_RETRIES))
        cls.CONCURRENT_DOWNLOADS = int(os.getenv('ANIME_CONCURRENT', cls.CONCURRENT_DOWNLOADS))
        
        # Configuración de subtítulos desde env
        cls.DOWNLOAD_SUBTITLES = os.getenv('ANIME_SUBTITLES', 'false').lower() == 'true'
        cls.IGNORE_SUBTITLE_ERRORS = os.getenv('ANIME_IGNORE_SUB_ERRORS', 'true').lower() == 'true'
        
        # Rate limiting
        cls.USE_RATE_LIMITING = os.getenv('ANIME_RATE_LIMIT', 'true').lower() == 'true'
        cls.MAX_DOWNLOAD_RATE = os.getenv('ANIME_MAX_RATE', cls.MAX_DOWNLOAD_RATE)

# Cargar configuración desde variables de entorno al importar
Config.load_from_env()
