"""
Anime Downloader - Lógica principal de descarga (Versión Mejorada)
Maneja la descarga de episodios con mejor manejo de rate limiting
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
    check_disk_space, format_bytes, 
    ProgressHook
)
from config import Config

class AnimeDownloader:
    """Clase principal para manejar descargas de anime con rate limiting"""
    
    def __init__(self, output_path=None, quality='720p', max_retries=3, concurrent_downloads=1):
        """
        Inicializa el downloader
        
        Args:
            output_path (str): Ruta donde guardar las descargas
            quality (str): Calidad de video preferida
            max_retries (int): Número máximo de reintentos
            concurrent_downloads (int): Descargas simultáneas (reducido por defecto)
        """
        self.output_path = Path(output_path or Config.DOWNLOAD_PATH).expanduser().resolve()
        self.quality = quality
        self.max_retries = max_retries
        self.concurrent_downloads = max(1, min(concurrent_downloads, 2))  # Limitar a máximo 2
        self.logger = logging.getLogger(__name__)
        
        # Crear directorio de salida
        self.output_path.mkdir(parents=True, exist_ok=True)
        
        # Configurar yt-dlp con configuración segura
        self.ydl_opts = Config.get_ydl_config_safe(quality)
        self.ydl_opts['outtmpl'] = str(self.output_path / '%(title)s.%(ext)s')
        
        # Log de configuración
        self.logger.info(f"Downloader inicializado - Calidad: {quality}, Rate Limiting: {Config.USE_RATE_LIMITING}")
        
    def download_episode(self, url, progress_callback=None, enable_subtitles=False):
        """
        Descarga un episodio individual con manejo mejorado de errores
        
        Args:
            url (str): URL del episodio
            progress_callback (callable): Función callback para progreso
            enable_subtitles (bool): Si descargar subtítulos (puede causar rate limiting)
            
        Returns:
            bool: True si la descarga fue exitosa
        """
        self.logger.info(f"Iniciando descarga de: {url}")
        
        # Verificar espacio en disco
        if not self._check_available_space():
            return False
        
        # Usar configuración segura o con subtítulos según se solicite
        if enable_subtitles:
            ydl_opts = Config.get_ydl_config_with_subtitles(self.quality, ['es'])
            self.logger.info("Modo con subtítulos activado (puede ser más lento)")
        else:
            ydl_opts = Config.get_ydl_config_safe(self.quality)
            self.logger.info("Modo seguro activado (sin subtítulos)")
        
        # Actualizar ruta de salida
        ydl_opts['outtmpl'] = str(self.output_path / '%(title)s.%(ext)s')
        
        # Configurar hook de progreso si se proporciona
        if progress_callback:
            ydl_opts['progress_hooks'] = [
                ProgressHook(progress_callback).hook
            ]
        
        # Intentar descarga con reintentos
        for attempt in range(self.max_retries):
            try:
                self.logger.info(f"Intento {attempt + 1} de {self.max_retries}")
                
                # Pausa entre intentos para evitar rate limiting
                if attempt > 0:
                    wait_time = min(2 ** attempt, 10)  # Backoff exponencial, máximo 10s
                    self.logger.info(f"Esperando {wait_time} segundos antes del intento...")
                    time.sleep(wait_time)
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    # Extraer información del video primero
                    try:
                        info = ydl.extract_info(url, download=False)
                        
                        if not info:
                            self.logger.error("No se pudo extraer información del video")
                            continue
                        
                        title = clean_filename(info.get('title', 'Unknown'))
                        duration = info.get('duration', 0)
                        filesize = info.get('filesize') or info.get('filesize_approx', 0)
                        
                        self.logger.info(f"Título: {title}")
                        if duration:
                            self.logger.info(f"Duración: {duration//60}:{duration%60:02d}")
                        if filesize:
                            self.logger.info(f"Tamaño aproximado: {format_bytes(filesize)}")
                        
                        # Pequeña pausa antes de la descarga real
                        time.sleep(1)
                        
                    except Exception as e:
                        self.logger.warning(f"No se pudo obtener información previa: {e}")
                    
                    # Realizar descarga
                    ydl.download([url])
                    
                self.logger.info("✅ Descarga completada exitosamente")
                return True
                
            except yt_dlp.DownloadError as e:
                error_msg = str(e)
                
                # Manejo específico de errores comunes
                if "429" in error_msg or "Too Many Requests" in error_msg:
                    self.logger.error(f"Rate limiting detectado (intento {attempt + 1})")
                    if attempt < self.max_retries - 1:
                        wait_time = min(30 + (attempt * 10), 60)  # Espera más larga para 429
                        self.logger.info(f"Esperando {wait_time} segundos para evitar rate limiting...")
                        time.sleep(wait_time)
                elif "subtitles" in error_msg.lower():
                    self.logger.warning(f"Error con subtítulos, reintentando sin ellos: {e}")
                    # En el siguiente intento, usar modo seguro
                    ydl_opts = Config.get_ydl_config_safe(self.quality)
                    ydl_opts['outtmpl'] = str(self.output_path / '%(title)s.%(ext)s')
                else:
                    self.logger.error(f"Error de descarga (intento {attempt + 1}): {e}")
                
                if attempt < self.max_retries - 1:
                    wait_time = 2 ** attempt  # Backoff exponencial normal
                    time.sleep(wait_time)
                
            except Exception as e:
                self.logger.error(f"Error inesperado (intento {attempt + 1}): {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(2)
        
        self.logger.error("❌ Descarga falló después de todos los intentos")
        return False
    
    def download_episode_safe(self, url, progress_callback=None):
        """
        Descarga un episodio en modo seguro (sin subtítulos, sin thumbnails)
        
        Args:
            url (str): URL del episodio
            progress_callback (callable): Función callback para progreso
            
        Returns:
            bool: True si la descarga fue exitosa
        """
        return self.download_episode(url, progress_callback, enable_subtitles=False)
    
    def download_episode_with_subtitles(self, url, progress_callback=None, subtitle_langs=['es']):
        """
        Descarga un episodio con subtítulos (más riesgo de rate limiting)
        
        Args:
            url (str): URL del episodio
            progress_callback (callable): Función callback para progreso
            subtitle_langs (list): Idiomas de subtítulos
            
        Returns:
            bool: True si la descarga fue exitosa
        """
        self.logger.warning("Modo con subtítulos puede causar rate limiting")
        return self.download_episode(url, progress_callback, enable_subtitles=True)
    
    def download_batch(self, urls, progress_callback=None, safe_mode=True):
        """
        Descarga múltiples episodios con pausa entre descargas
        
        Args:
            urls (list): Lista de URLs a descargar
            progress_callback (callable): Función callback para progreso
            safe_mode (bool): Si usar modo seguro con pausas más largas
            
        Returns:
            dict: Resultados de las descargas
        """
        self.logger.info(f"Iniciando descarga en lote de {len(urls)} episodios (modo seguro: {safe_mode})")
        
        results = {
            'successful': [],
            'failed': [],
            'total': len(urls)
        }
        
        # En modo seguro, reducir concurrencia y agregar pausas
        max_workers = 1 if safe_mode else min(self.concurrent_downloads, 2)
        batch_delay = 5 if safe_mode else 2
        
        self.logger.info(f"Usando {max_workers} trabajadores con pausa de {batch_delay}s entre descargas")
        
        for i, url in enumerate(urls):
            self.logger.info(f"Descargando episodio {i + 1}/{len(urls)}: {url}")
            
            def batch_progress(progress_data):
                if progress_callback:
                    progress_data['episode'] = i + 1
                    progress_data['total_episodes'] = len(urls)
                    progress_callback(progress_data)
            
            # Descargar en modo seguro por defecto
            success = self.download_episode_safe(url, batch_progress)
            
            if success:
                results['successful'].append(url)
                self.logger.info(f"✅ Episodio {i + 1} completado")
            else:
                results['failed'].append(url)
                self.logger.error(f"❌ Episodio {i + 1} falló")
            
            # Pausa entre descargas para evitar rate limiting
            if i < len(urls) - 1:  # No pausar después del último
                self.logger.info(f"Pausando {batch_delay} segundos antes del siguiente episodio...")
                time.sleep(batch_delay)
        
        self.logger.info(f"Descarga en lote completada:")
        self.logger.info(f"  ✅ Exitosas: {len(results['successful'])}")
        self.logger.info(f"  ❌ Fallidas: {len(results['failed'])}")
        
        return results
    
    def _check_available_space(self, min_space_gb=1):
        """
        Verifica si hay suficiente espacio en disco
        
        Args:
            min_space_gb (int): Espacio mínimo requerido en GB
            
        Returns:
            bool: True si hay suficiente espacio
        """
        try:
            available_space = check_disk_space(self.output_path)
            min_space_bytes = min_space_gb * 1024**3
            
            if available_space < min_space_bytes:
                self.logger.error(
                    f"Espacio insuficiente. Disponible: {format_bytes(available_space)}, "
                    f"Requerido: {format_bytes(min_space_bytes)}"
                )
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
        """
        Obtiene información del video sin descargarlo
        
        Args:
            url (str): URL del video
            
        Returns:
            dict: Información del video
        """
        try:
            # Usar configuración mínima para solo extraer info
            opts = {
                'quiet': True,
                'no_warnings': True,
                'socket_timeout': 15,
                'ignoreerrors': True,
            }
            
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return {
                    'title': clean_filename(info.get('title', 'Unknown')),
                    'duration': info.get('duration', 0),
                    'formats': info.get('formats', []),
                    'thumbnail': info.get('thumbnail'),
                    'description': info.get('description', ''),
                    'uploader': info.get('uploader', 'Unknown'),
                    'upload_date': info.get('upload_date'),
                }
        except Exception as e:
            self.logger.error(f"Error obteniendo información del video: {e}")
            return None
    
    def set_safe_mode(self, enabled=True):
        """
        Activa/desactiva modo seguro
        
        Args:
            enabled (bool): Si activar modo seguro
        """
        if enabled:
            self.ydl_opts = Config.get_ydl_config_safe(self.quality)
            self.concurrent_downloads = 1
            self.logger.info("✅ Modo seguro activado (sin subtítulos, velocidad reducida)")
        else:
            self.ydl_opts = Config.get_ydl_config_with_subtitles(self.quality)
            self.logger.warning("⚠️ Modo normal activado (puede causar rate limiting)")
        
        # Actualizar ruta de salida
        self.ydl_opts['outtmpl'] = str(self.output_path / '%(title)s.%(ext)s')
