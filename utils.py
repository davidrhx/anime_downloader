"""
Anime Downloader - Utilidades y funciones auxiliares
Contiene funciones de apoyo para el proyecto
"""

import os
import re
import shutil
import logging
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from urllib.request import urlopen
import time
import hashlib

def clean_filename(filename, max_length=200):
    """
    Limpia un nombre de archivo eliminando caracteres inválidos
    
    Args:
        filename (str): Nombre original del archivo
        max_length (int): Longitud máxima del nombre
        
    Returns:
        str: Nombre de archivo limpio
    """
    if not filename:
        return "unknown_file"
    
    # Caracteres no permitidos en nombres de archivo
    invalid_chars = r'[<>:"/\\|?*\x00-\x1f]'
    
    # Reemplazar caracteres inválidos
    clean_name = re.sub(invalid_chars, '_', str(filename))
    
    # Eliminar espacios múltiples y al principio/final
    clean_name = re.sub(r'\s+', ' ', clean_name.strip())
    
    # Truncar si es muy largo
    if len(clean_name) > max_length:
        name_part = clean_name[:max_length-4]
        clean_name = name_part + "..."
    
    # Evitar nombres vacíos
    if not clean_name or clean_name.isspace():
        clean_name = "unnamed_file"
    
    return clean_name

def validate_url(url):
    """
    Valida si una URL tiene formato correcto
    
    Args:
        url (str): URL a validar
        
    Returns:
        bool: True si la URL es válida
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def extract_video_info(html_content):
    """
    Extrae información de video desde contenido HTML
    (Función genérica - necesita adaptación según el sitio)
    
    Args:
        html_content (str): Contenido HTML de la página
        
    Returns:
        dict: Información extraída del video
    """
    from bs4 import BeautifulSoup
    
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Patrones comunes para encontrar información de video
        video_info = {}
        
        # Buscar título
        title_selectors = ['h1', 'title', '.video-title', '.episode-title']
        for selector in title_selectors:
            element = soup.select_one(selector)
            if element:
                video_info['title'] = clean_filename(element.get_text().strip())
                break
        
        # Buscar enlaces de video
        video_links = []
        video_selectors = ['video source', 'iframe[src*="player"]', 'a[href*=".mp4"]']
        for selector in video_selectors:
            elements = soup.select(selector)
            for element in elements:
                src = element.get('src') or element.get('href')
                if src and validate_url(src):
                    video_links.append(src)
        
        video_info['video_links'] = list(set(video_links))  # Eliminar duplicados
        
        return video_info
        
    except Exception as e:
        logging.error(f"Error extrayendo información de video: {e}")
        return {}

def check_disk_space(path):
    """
    Verifica el espacio disponible en disco
    
    Args:
        path (str): Ruta a verificar
        
    Returns:
        int: Bytes disponibles en disco
    """
    try:
        if os.name == 'nt':  # Windows
            import ctypes
            free_bytes = ctypes.c_ulonglong(0)
            ctypes.windll.kernel32.GetDiskFreeSpaceExW(
                ctypes.c_wchar_p(str(path)),
                ctypes.pointer(free_bytes),
                None, None
            )
            return free_bytes.value
        else:  # Unix/Linux/macOS
            statvfs = os.statvfs(path)
            return statvfs.f_frsize * statvfs.f_available
    except:
        return float('inf')  # Si no se puede determinar, asumir espacio infinito

def format_bytes(bytes_value):
    """
    Convierte bytes a formato legible (KB, MB, GB)
    
    Args:
        bytes_value (int): Número de bytes
        
    Returns:
        str: Tamaño formateado
    """
    if bytes_value == 0:
        return "0 B"
    
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    unit_index = 0
    size = float(bytes_value)
    
    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1
    
    return f"{size:.2f} {units[unit_index]}"

def format_duration(seconds):
    """
    Convierte segundos a formato HH:MM:SS
    
    Args:
        seconds (int): Duración en segundos
        
    Returns:
        str: Duración formateada
    """
    if not seconds or seconds < 0:
        return "00:00"
    
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    else:
        return f"{minutes:02d}:{seconds:02d}"

def setup_logging(verbose=False, log_file=None):
    """
    Configura el sistema de logging
    
    Args:
        verbose (bool): Si mostrar logs detallados
        log_file (str): Archivo de log opcional
    """
    level = logging.DEBUG if verbose else logging.INFO
    format_str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Configurar logging básico
    logging.basicConfig(
        level=level,
        format=format_str,
        handlers=[]
    )
    
    # Handler para consola
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_formatter = logging.Formatter(
        '%(levelname)s: %(message)s' if not verbose else format_str
    )
    console_handler.setFormatter(console_formatter)
    logging.getLogger().addHandler(console_handler)
    
    # Handler para archivo si se especifica
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(format_str)
        file_handler.setFormatter(file_formatter)
        logging.getLogger().addHandler(file_handler)

def generate_file_hash(file_path, algorithm='md5'):
    """
    Genera hash de un archivo
    
    Args:
        file_path (str): Ruta del archivo
        algorithm (str): Algoritmo de hash (md5, sha1, sha256)
        
    Returns:
        str: Hash del archivo
    """
    hash_obj = hashlib.new(algorithm)
    
    try:
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_obj.update(chunk)
        return hash_obj.hexdigest()
    except Exception as e:
        logging.error(f"Error generando hash del archivo {file_path}: {e}")
        return None

def create_directory_structure(base_path, anime_name, season=None):
    """
    Crea estructura de directorios para organizar anime
    
    Args:
        base_path (str): Ruta base
        anime_name (str): Nombre del anime
        season (int): Número de temporada opcional
        
    Returns:
        Path: Ruta del directorio creado
    """
    clean_anime_name = clean_filename(anime_name)
    
    if season:
        folder_name = f"{clean_anime_name} - Temporada {season}"
    else:
        folder_name = clean_anime_name
    
    full_path = Path(base_path) / folder_name
    full_path.mkdir(parents=True, exist_ok=True)
    
    return full_path

class ProgressHook:
    """Clase para manejar el progreso de descarga"""
    
    def __init__(self, callback=None):
        """
        Args:
            callback (callable): Función a llamar con información de progreso
        """
        self.callback = callback
        self.last_update = 0
        
    def hook(self, data):
        """
        Hook para yt-dlp que maneja el progreso de descarga
        
        Args:
            data (dict): Datos de progreso de yt-dlp
        """
        if not self.callback:
            return
            
        # Limitar actualizaciones para no sobrecargar la UI
        current_time = time.time()
        if current_time - self.last_update < 0.5:  # Actualizar máximo cada 0.5 segundos
            return
            
        self.last_update = current_time
        
        status = data.get('status')
        
        if status == 'downloading':
            progress_data = {
                'status': 'downloading',
                'filename': data.get('filename', ''),
                'downloaded_bytes': data.get('downloaded_bytes', 0),
                'total_bytes': data.get('total_bytes') or data.get('total_bytes_estimate', 0),
                'speed': data.get('speed', 0),
                'eta': data.get('eta', 0),
            }
            
            # Calcular porcentaje
            if progress_data['total_bytes'] > 0:
                progress_data['percentage'] = (
                    progress_data['downloaded_bytes'] / progress_data['total_bytes'] * 100
                )
            else:
                progress_data['percentage'] = 0
                
        elif status == 'finished':
            progress_data = {
                'status': 'finished',
                'filename': data.get('filename', ''),
                'total_bytes': data.get('total_bytes', 0),
                'percentage': 100,
            }
            
        elif status == 'error':
            progress_data = {
                'status': 'error',
                'error': str(data.get('error', 'Error desconocido')),
                'percentage': 0,
            }
        else:
            return  # Estado no reconocido
            
        try:
            self.callback(progress_data)
        except Exception as e:
            logging.error(f"Error en callback de progreso: {e}")

def retry_on_failure(max_retries=3, delay=1, backoff=2):
    """
    Decorador para reintentar funciones que fallan
    
    Args:
        max_retries (int): Número máximo de reintentos
        delay (float): Delay inicial en segundos
        backoff (float): Factor de backoff exponencial
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            retries = 0
            current_delay = delay
            
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    retries += 1
                    if retries >= max_retries:
                        logging.error(f"Función {func.__name__} falló después de {max_retries} intentos: {e}")
                        raise e
                    
                    logging.warning(f"Intento {retries} falló para {func.__name__}: {e}")
                    time.sleep(current_delay)
                    current_delay *= backoff
                    
        return wrapper
    return decorator

def is_video_file(file_path):
    """
    Verifica si un archivo es un video basado en su extensión
    
    Args:
        file_path (str): Ruta del archivo
        
    Returns:
        bool: True si es un archivo de video
    """
    video_extensions = {'.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm', '.m4v'}
    return Path(file_path).suffix.lower() in video_extensions

def get_video_files_in_directory(directory):
    """
    Obtiene todos los archivos de video en un directorio
    
    Args:
        directory (str): Ruta del directorio
        
    Returns:
        list: Lista de archivos de video encontrados
    """
    video_files = []
    try:
        for file_path in Path(directory).rglob('*'):
            if file_path.is_file() and is_video_file(file_path):
                video_files.append(file_path)
    except Exception as e:
        logging.error(f"Error buscando archivos de video en {directory}: {e}")
    
    return sorted(video_files)
