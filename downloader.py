"""
Anime Downloader - Lógica principal de descarga (Versión Final)
Maneja la descarga de episodios sin errores de callback
"""

import os
import time
import requests
import logging
from pathlib import Path
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor
import yt_dlp

from utils import (
    clean_filename, extract_video_info, 
    check_disk_space, format_bytes
)
from config import Config

class SafeProgressHook:
    """Hook de progreso completamente seguro"""
    
    def __init__(self, callback=None):
        self.callback = callback
        self.last_update = 0
        
    def __call__(self, data):
        """Método call para el hook"""
        if not self.callback:
            return
            
        try:
            # Limitar frecuencia de actualizaciones
            current_time = time.time()
            if current_time - self.last_update < 1.0:  # Solo cada 1 segundo
                return
            self.last_update = current_time
            
            status = data.get('status', 'unknown')
            
            if status == 'downloading':
                # Obtener valores de forma ultra-segura
                try:
                    downloaded = float(data.get('downloaded_bytes', 0))
                except (ValueError, TypeError):
                    downloaded = 0.0
                    
                try:
                    total = float(data.get('total_bytes') or data.get('total_bytes_estimate', 0))
                except (ValueError, TypeError):
                    total = 0.0
                
                try:
                    speed = float(data.get('speed', 0))
                except (ValueError, TypeError):
                    speed = 0.0
                
                # Calcular porcentaje
                if total > 0:
                    percentage = min((downloaded / total) * 100, 100)
                else:
                    percentage = 0
                
                progress_data = {
                    'status': 'downloading',
                    'percentage': percentage,
                    'downloaded_bytes': int(downloaded),
                    'total_bytes': int(total),
                    'speed': int(speed),
                    'filename': str(data.get('filename', '')),
                }
                
            elif status == 'finished':
                progress_data = {
                    'status': 'finished',
                    'percentage': 100,
                    'filename': str(data.get('filename', '')),
                }
            else:
                return  # Ignorar otros estados
            
            # Llamar callback
            self.callback(progress_data)
            
        except Exception as e:
            # Silenciar errores del callback para no afectar la descarga
            logging.debug(f"Error en callback (ignorado): {e}")

class AnimeDownloader:
    """Clase principal para manejar descargas de anime sin errores"""
    
    def __init__(self, output_path=None, quality='720p', max_retries=3, concurrent_downloads=1):
        """
        Inicializa el downloader
        
        Args:
            output_path (str): Ruta donde guardar las descargas
            quality (str): Calidad de video preferida
            max_retries (int): Número máximo de reintentos
            concurrent_downloads (int): Descargas simultáneas
        """
        self.output_path = Path(output_path or Config.DOWNLOAD_PATH).expanduser().resolve()
        self.quality = quality
        self.max_retries = max_retries
        self.concurrent_downloads = max(1, min(concurrent_downloads, 2))
        self.logger = logging.getLogger(__name__)
        
        # Crear directorio de salida
        self.output_path.mkdir(parents=True, exist_ok=True)
        
        # Log de configuración
        self.logger.info(f"Downloader inicializado - Calidad: {quality}, Rate Limiting: {Config.USE_RATE_LIMITING}")
        
    def _get_safe_ydl_config(self, enable_subtitles=False):
        """Configuración ultra-segura para yt-dlp"""
        config = {
            # Formato básico
            'format': f'best[height<={self.quality[:-1] if self.quality.endswith("p") else "720"}]',
            'outtmpl': str(self.output_path / '%(title)s.%(ext)s'),
            
            # Desactivar todo lo que puede causar problemas
            'writesubtitles': enable_subtitles,
            'writeautomaticsub': False,
            'writethumbnail': False,
            'writeinfojson': False,
            'embed_subs': False,
            
            # Configuración de red conservadora
            'socket_timeout': 30,
            'retries': 3,
            'ignoreerrors': True,
            'no_warnings': False,
            
            # Rate limiting
            'sleep_interval': 1,
            'max_sleep_interval': 5,
            
            # Headers básicos
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            },
            
            # Evitar problemas con el progreso
            'noprogress': False,
            'quiet': False,
        }
        
        return config
        
    def download_episode(self, url, progress_callback=None, enable_subtitles=False):
        """
        Descarga un episodio individual sin errores de callback
        
        Args:
            url (str): URL del episodio
            progress_callback (callable): Función callback para progreso
            enable_subtitles (bool): Si descargar subtítulos
            
        Returns:
            bool: True si la descarga fue exitosa
        """
        self.logger.info(f"Iniciando descarga de: {url}")
        
        # Verificar espacio en disco
        if not self._check_available_space():
            return False
        
        # Obtener configuración
        ydl_opts = self._get_safe_ydl_config(enable_subtitles)
        
        # Configurar progreso solo si es necesario
        if progress_callback:
            # Usar nuestro hook seguro
            safe_hook = SafeProgressHook(progress_callback)
            ydl_opts['progress_hooks'] = [safe_hook]
            self.logger.info("Hook de progreso configurado")
        else:
            # Sin progreso para evitar errores
            ydl_opts['noprogress'] = True
        
        if enable_subtitles:
            self.logger.info("Modo con subtítulos activado (puede causar rate limiting)")
        else:
            self.logger.info("Modo seguro activado (sin subtítulos)")
        
        # Intentar descarga con reintentos
        for attempt in range(self.max_retries):
            try:
                self.logger.info(f"Intento {attempt + 1} de {self.max_retries}")
                
                # Pausa entre intentos
                if attempt > 0:
                    wait_time = min(2 ** attempt, 10)
                    self.logger.info(f"Esperando {wait_time} segundos antes del intento...")
                    time.sleep(wait_time)
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    # Extraer información primero (sin callback)
                    try:
                        info_opts = self._get_safe_ydl_config(False)
                        info_opts['quiet'] = True
                        info_opts['noprogress'] = True
                        
                        with yt_dlp.YoutubeDL(info_opts) as info_ydl:
                            info = info_ydl.extract_info(url, download=False)
                        
                        if info:
                            title = clean_filename(info.get('title', 'Unknown'))
                            duration = info.get('duration', 0)
                            filesize = info.get('filesize') or info.get('filesize_approx', 0)
                            
                            self.logger.info(f"Título: {title}")
                            if duration:
                                self.logger.info(f"Duración: {duration//60}:{duration%60:02d}")
                            if filesize:
                                self.logger.info(f"Tamaño aproximado: {format_bytes(filesize)}")
                        
                        # Pausa antes de descarga
                        time.sleep(1)
                        
                    except Exception as e:
                        self.logger.warning(f"No se pudo obtener información previa: {e}")
                    
                    # Realizar descarga
                    ydl.download([url])
                    
                self.logger.info("✅ Descarga completada exitosamente")
                return True
                
            except yt_dlp.DownloadError as e:
                error_msg = str(e)
                
                # Manejo específico de errores
                if "429" in error_msg or "Too Many Requests" in error_msg:
                    self.logger.error(f"Rate limiting detectado (intento {attempt + 1})")
                    if attempt < self.max_retries - 1:
                        wait_time = min(30 + (attempt * 10), 60)
                        self.logger.info(f"Esperando {wait_time} segundos para evitar rate limiting...")
                        time.sleep(wait_time)
                elif "subtitles" in error_msg.lower() and enable_subtitles:
                    self.logger.warning(f"Error con subtítulos, reintentando sin ellos")
                    # En siguiente intento, sin subtítulos
                    enable_subtitles = False
                    ydl_opts = self._get_safe_ydl_config(False)
                else:
                    self.logger.error(f"Error de descarga (intento {attempt + 1}): {e}")
                
                if attempt < self.max_retries - 1:
                    time.sleep(2)
                
            except Exception as e:
                self.logger.error(f"Error inesperado (intento {attempt + 1}): {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(2)
        
        self.logger.error("❌ Descarga falló después de todos los intentos")
        return False
    
    def download_episode_safe(self, url, progress_callback=None):
        """Descarga en modo completamente seguro"""
        return self.download_episode(url, progress_callback, enable_subtitles=False)
    
    def download_episode_with_subtitles(self, url, progress_callback=None):
        """Descarga con subtítulos (riesgo de rate limiting)"""
        self.logger.warning("Modo con subtítulos puede causar rate limiting")
        return self.download_episode(url, progress_callback, enable_subtitles=True)
    
    def _check_available_space(self, min_space_gb=1):
        """Verifica espacio en disco disponible"""
        try:
            available_space = check_disk_space(self.output_path)
            min_space_bytes = min_space_gb * 1024**3
            
            if available_space < min_space_bytes:
                self.logger.error(f"Espacio insuficiente en disco")
                return False
                
            if available_space < float('inf'):
                self.logger.info(f"Espacio disponible: {format_bytes(available_space)}")
            else:
                self.logger.info("Espacio disponible: verificación omitida")
            return True
            
        except Exception as e:
            self.logger.warning(f"No se pudo verificar el espacio en disco: {e}")
            return True
    
    def get_video_info(self, url):
        """Obtiene información del video sin descargarlo"""
        try:
            # Configuración mínima solo para info
            opts = {
                'quiet': True,
                'no_warnings': True,
                'socket_timeout': 15,
                'ignoreerrors': True,
                'noprogress': True,
                'extract_flat': False,
            }
            
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if info:
                    return {
                        'title': clean_filename(info.get('title', 'Unknown')),
                        'duration': info.get('duration', 0),
                        'uploader': info.get('uploader', 'Unknown'),
                        'upload_date': info.get('upload_date'),
                        'description': info.get('description', ''),
                        'thumbnail': info.get('thumbnail'),
                    }
        except Exception as e:
            self.logger.error(f"Error obteniendo información del video: {e}")
            return None
    
    def set_output_path(self, path):
        """Actualiza la ruta de descarga"""
        self.output_path = Path(path).expanduser().resolve()
        self.output_path.mkdir(parents=True, exist_ok=True)
        self.logger.info(f"Ruta de descarga actualizada a: {self.output_path}")
