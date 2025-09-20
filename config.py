"""
Anime Downloader - Configuración
Variables configurables del proyecto
"""

import os
from pathlib import Path

class Config:
    """Configuración principal del Anime Downloader"""
    
    # === Configuración de Descarga ===
    DEFAULT_QUALITY = '720p'  # Calidad por defecto (480p, 720p, 1080p, best)
    DOWNLOAD_PATH = str(Path.home() / 'Downloads' / 'Anime')  # Directorio de descarga por defecto
    MAX_RETRIES = 3  # Número máximo de reintentos por descarga
    CONCURRENT_DOWNLOADS = 2  # Número de descargas simultáneas
    RETRY_DELAY = 2  # Segundos de espera entre reintentos
    
    # === Configuración de Red ===
    TIMEOUT = 30  # Timeout para requests en segundos
    USER_AGENT = (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
        '(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    )
    MAX_CONNECTIONS = 5  # Máximo de conexiones simultáneas
    
    # === Configuración de Archivos ===
    ALLOWED_EXTENSIONS = ['.mp4', '.mkv', '.avi', '.webm', '.m4v']
    MAX_FILENAME_LENGTH = 200  # Longitud máxima para nombres de archivo
    MIN_FILE_SIZE = 10 * 1024 * 1024  # Tamaño mínimo de archivo (10MB)
    MAX_FILE_SIZE = 5 * 1024 * 1024 * 1024  # Tamaño máximo de archivo (5GB)
    
    # === Configuración de Subtítulos ===
    DOWNLOAD_SUBTITLES = True  # Descargar subtítulos automáticamente
    SUBTITLE_LANGUAGES = ['es', 'en', 'ja']  # Idiomas de subtítulos preferidos
    EMBED_SUBTITLES = True  # Incrustar subtítulos en el video
    
    # === Configuración de Metadatos ===
    DOWNLOAD_THUMBNAIL = True  # Descargar miniatura del episodio
    SAVE_INFO_JSON = False  # Guardar información en JSON
    ADD_METADATA = True  # Agregar metadatos al archivo de video
    
    # === Configuración de GUI ===
    WINDOW_WIDTH = 800
    WINDOW_HEIGHT = 600
    THEME = 'default'  # Tema de la interfaz gráfica
    UPDATE_INTERVAL = 500  # Intervalo de actualización de progreso en ms
    
    # === Configuración de Logging ===
    LOG_LEVEL = 'INFO'  # Nivel de logging (DEBUG, INFO, WARNING, ERROR)
    LOG_FILE = None  # Archivo de log (None para no guardar archivo)
    LOG_MAX_SIZE = 10 * 1024 * 1024  # Tamaño máximo del archivo de log (10MB)
    LOG_BACKUP_COUNT = 3  # Número de archivos de backup del log
    
    # === Configuración de Sitios Web ===
    SUPPORTED_SITES = [
        'youtube.com',
        'youtu.be',
        'twitch.tv',
        'vimeo.com',
        'dailymotion.com',
        # Agregar más sitios según sea necesario
    ]
    
    # Headers personalizados para requests
    HEADERS = {
        'User-Agent': USER_AGENT,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
    }
    
    # === Configuración de Calidad ===
    QUALITY_PREFERENCES = {
        '480p': {
            'height': 480,
            'format': 'best[height<=480]',
            'description': 'Calidad estándar (480p)'
        },
        '720p': {
            'height': 720,
            'format': 'best[height<=720]',
            'description': 'Alta calidad (720p HD)'
        },
        '1080p': {
            'height': 1080,
            'format': 'best[height<=1080]',
            'description': 'Muy alta calidad (1080p Full HD)'
        },
        'best': {
            'height': 9999,
            'format': 'best',
            'description': 'Mejor calidad disponible'
        }
    }
    
    # === Configuración de Proxy ===
    USE_PROXY = False  # Usar proxy para descargas
    PROXY_URL = None  # URL del proxy (ej: 'http://proxy.example.com:8080')
    PROXY_USERNAME = None
    PROXY_PASSWORD = None
    
    # === Configuración de Rate Limiting ===
    RATE_LIMIT = False  # Activar limitación de velocidad
    MAX_DOWNLOAD_RATE = '1M'  # Velocidad máxima de descarga (ej: '500K', '1M')
    
    # === Configuración de Organización ===
    ORGANIZE_BY_ANIME = True  # Organizar en carpetas por anime
    ORGANIZE_BY_SEASON = True  # Organizar por temporadas
    AUTO_RENAME = True  # Renombrar archivos automáticamente
    
    # Patrones para nombres de archivo
    FILENAME_PATTERNS = {
        'episode': '{anime_name} - E{episode:02d} - {title}',
        'movie': '{anime_name} - {title}',
        'ova': '{anime_name} - OVA{episode:02d} - {title}',
        'special': '{anime_name} - Especial{episode:02d} - {title}'
    }
    
    @classmethod
    def load_from_env(cls):
        """Carga configuración desde variables de entorno"""
        # Actualizar configuración desde variables de entorno si existen
        cls.DEFAULT_QUALITY = os.getenv('ANIME_QUALITY', cls.DEFAULT_QUALITY)
        cls.DOWNLOAD_PATH = os.getenv('ANIME_DOWNLOAD_PATH', cls.DOWNLOAD_PATH)
        cls.MAX_RETRIES = int(os.getenv('ANIME_MAX_RETRIES', cls.MAX_RETRIES))
        cls.CONCURRENT_DOWNLOADS = int(os.getenv('ANIME_CONCURRENT', cls.CONCURRENT_DOWNLOADS))
        cls.TIMEOUT = int(os.getenv('ANIME_TIMEOUT', cls.TIMEOUT))
        
        # Configuración booleana
        cls.DOWNLOAD_SUBTITLES = os.getenv('ANIME_SUBTITLES', 'true').lower() == 'true'
        cls.EMBED_SUBTITLES = os.getenv('ANIME_EMBED_SUBS', 'true').lower() == 'true'
        cls.DOWNLOAD_THUMBNAIL = os.getenv('ANIME_THUMBNAIL', 'true').lower() == 'true'
        
        # Proxy
        cls.USE_PROXY = os.getenv('ANIME_USE_PROXY', 'false').lower() == 'true'
        cls.PROXY_URL = os.getenv('ANIME_PROXY_URL', cls.PROXY_URL)
        
    @classmethod
    def validate_config(cls):
        """Valida la configuración actual"""
        errors = []
        
        # Validar calidad
        if cls.DEFAULT_QUALITY not in cls.QUALITY_PREFERENCES:
            errors.append(f"Calidad inválida: {cls.DEFAULT_QUALITY}")
        
        # Validar número de descargas concurrentes
        if cls.CONCURRENT_DOWNLOADS < 1 or cls.CONCURRENT_DOWNLOADS > 10:
            errors.append(f"Número de descargas concurrentes inválido: {cls.CONCURRENT_DOWNLOADS}")
        
        # Validar reintentos
        if cls.MAX_RETRIES < 0 or cls.MAX_RETRIES > 10:
            errors.append(f"Número de reintentos inválido: {cls.MAX_RETRIES}")
        
        # Validar timeout
        if cls.TIMEOUT < 1 or cls.TIMEOUT > 300:
            errors.append(f"Timeout inválido: {cls.TIMEOUT}")
        
        # Validar ruta de descarga
        try:
            Path(cls.DOWNLOAD_PATH).expanduser().resolve()
        except Exception:
            errors.append(f"Ruta de descarga inválida: {cls.DOWNLOAD_PATH}")
        
        if errors:
            raise ValueError(f"Errores de configuración: {', '.join(errors)}")
        
        return True
    
    @classmethod
    def get_ydl_config(cls):
        """Retorna configuración para yt-dlp"""
        config = {
            'format': cls.QUALITY_PREFERENCES[cls.DEFAULT_QUALITY]['format'],
            'outtmpl': '%(title)s.%(ext)s',
            'writesubtitles': cls.DOWNLOAD_SUBTITLES,
            'writeautomaticsub': cls.DOWNLOAD_SUBTITLES,
            'subtitleslangs': cls.SUBTITLE_LANGUAGES,
            'embed_subs': cls.EMBED_SUBTITLES,
            'writethumbnail': cls.DOWNLOAD_THUMBNAIL,
            'writeinfojson': cls.SAVE_INFO_JSON,
            'ignoreerrors': False,
            'no_warnings': False,
            'extractaudio': False,
            'socket_timeout': cls.TIMEOUT,
        }
        
        if cls.USE_PROXY and cls.PROXY_URL:
            config['proxy'] = cls.PROXY_URL
        
        if cls.RATE_LIMIT and cls.MAX_DOWNLOAD_RATE:
            config['ratelimit'] = cls.MAX_DOWNLOAD_RATE
        
        return config

# Cargar configuración desde variables de entorno al importar
Config.load_from_env()
