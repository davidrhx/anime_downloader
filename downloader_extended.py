"""
Anime Downloader Extended - Versión con soporte para sitios de anime específicos
Incluye el downloader original + extractores para sitios como JKAnime
"""

import os
import time
import logging
from pathlib import Path
from urllib.parse import urlparse
import yt_dlp

from downloader import AnimeDownloader as BaseDownloader
from utils import clean_filename, format_bytes
from config import Config

# Intentar importar extractores personalizados
try:
    from extractors.jkanime import JKAnimeExtractor
    JKANIME_AVAILABLE = True
except ImportError:
    JKANIME_AVAILABLE = False
    logging.warning("Extractor de JKAnime no disponible")

class ExtendedAnimeDownloader(BaseDownloader):
    """Downloader extendido con soporte para sitios de anime específicos"""
    
    def __init__(self, output_path=None, quality='720p', max_retries=3):
        """
        Inicializa el downloader extendido
        
        Args:
            output_path (str): Ruta donde guardar las descargas
            quality (str): Calidad de video preferida
            max_retries (int): Número máximo de reintentos
        """
        super().__init__(output_path, quality, max_retries, 1)
        
        # Inicializar extractores personalizados
        self.custom_extractors = {}
        
        if JKANIME_AVAILABLE:
            self.custom_extractors['jkanime'] = JKAnimeExtractor()
            self.logger.info("✅ Extractor de JKAnime cargado")
        
        self.logger.info(f"Downloader extendido inicializado con {len(self.custom_extractors)} extractores personalizados")
    
    def can_handle_url(self, url):
        """
        Verifica qué extractor puede manejar la URL
        
        Args:
            url (str): URL a verificar
            
        Returns:
            str: Nombre del extractor que puede manejar la URL, o None
        """
        for name, extractor in self.custom_extractors.items():
            if extractor.can_handle(url):
                return name
        return None
    
    def download_episode(self, url, progress_callback=None, enable_subtitles=False):
        """
        Descarga un episodio usando el extractor apropiado
        
        Args:
            url (str): URL del episodio
            progress_callback (callable): Función callback para progreso
            enable_subtitles (bool): Si descargar subtítulos
            
        Returns:
            bool: True si la descarga fue exitosa
        """
        # Verificar si tenemos un extractor personalizado para esta URL
        extractor_name = self.can_handle_url(url)
        
        if extractor_name:
            self.logger.info(f"🎌 Usando extractor personalizado: {extractor_name}")
            return self._download_with_custom_extractor(url, extractor_name, progress_callback)
        else:
            self.logger.info("🔄 Usando extractor estándar (yt-dlp)")
            return super().download_episode(url, progress_callback, enable_subtitles)
    
    def _download_with_custom_extractor(self, url, extractor_name, progress_callback=None):
        """
        Descarga usando un extractor personalizado
        
        Args:
            url (str): URL del episodio
            extractor_name (str): Nombre del extractor a usar
            progress_callback (callable): Función callback para progreso
            
        Returns:
            bool: True si la descarga fue exitosa
        """
        try:
            extractor = self.custom_extractors[extractor_name]
            self.logger.info(f"Iniciando descarga con {extractor_name}: {url}")
            
            # Verificar espacio en disco
            if not self._check_available_space():
                return False
            
            # Extraer información del video
            video_info = extractor.extract_video_info(url)
            
            if not video_info:
                self.logger.error(f"No se pudo extraer información usando {extractor_name}")
                return False
            
            # Mostrar información extraída
            self.logger.info(f"Título: {video_info.get('title', 'Desconocido')}")
            if video_info.get('description'):
                self.logger.info(f"Descripción: {video_info['description'][:100]}...")
            
            video_urls = video_info.get('video_urls', [])
            self.logger.info(f"URLs de video encontradas: {len(video_urls)}")
            
            if not video_urls:
                self.logger.error("No se encontraron URLs de video válidas")
                return False
            
            # Intentar descarga con cada URL
            for attempt in range(self.max_retries):
                try:
                    self.logger.info(f"Intento {attempt + 1} de {self.max_retries}")
                    
                    if attempt > 0:
                        wait_time = min(2 ** attempt, 10)
                        self.logger.info(f"Esperando {wait_time} segundos...")
                        time.sleep(wait_time)
                    
                    # Usar el método de descarga del extractor
                    success = extractor.download_video(
                        video_info, 
                        str(self.output_path), 
                        progress_callback
                    )
                    
                    if success:
                        self.logger.info("✅ Descarga completada exitosamente con extractor personalizado")
                        return True
                    
                except Exception as e:
                    self.logger.error(f"Error en intento {attempt + 1}: {e}")
                    if attempt < self.max_retries - 1:
                        continue
            
            # Si el extractor personalizado falla, intentar con yt-dlp como fallback
            self.logger.warning(f"Extractor {extractor_name} falló, intentando con yt-dlp...")
            return self._fallback_download(video_urls, video_info, progress_callback)
            
        except Exception as e:
            self.logger.error(f"Error con extractor personalizado {extractor_name}: {e}")
            return False
    
    def _fallback_download(self, video_urls, video_info, progress_callback=None):
        """
        Intenta descargar usando yt-dlp como fallback
        
        Args:
            video_urls (list): Lista de URLs de video
            video_info (dict): Información del video
            progress_callback (callable): Función de callback
            
        Returns:
            bool: True si la descarga fue exitosa
        """
        self.logger.info("Intentando descarga de fallback con yt-dlp...")
        
        for i, url in enumerate(video_urls[:3]):  # Intentar máximo 3 URLs
            try:
                self.logger.info(f"Probando URL de fallback {i+1}: {url}")
                
                ydl_opts = {
                    'outtmpl': str(self.output_path / f"{video_info['title']}.%(ext)s"),
                    'format': 'best',
                    'ignoreerrors': True,
                    'socket_timeout': 30,
                    'retries': 2,
                    'http_headers': {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                        'Referer': 'https://jkanime.net/',
                    }
                }
                
                if progress_callback:
                    from downloader import SafeProgressHook
                    safe_hook = SafeProgressHook(progress_callback)
                    ydl_opts['progress_hooks'] = [safe_hook]
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                
                self.logger.info("✅ Descarga de fallback exitosa")
                return True
                
            except Exception as e:
                self.logger.warning(f"Fallback URL {i+1} falló: {e}")
                continue
        
        self.logger.error("❌ Todas las opciones de descarga fallaron")
        return False
    
    def get_video_info(self, url):
        """
        Obtiene información del video usando el extractor apropiado
        
        Args:
            url (str): URL del video
            
        Returns:
            dict: Información del video
        """
        # Verificar si tenemos un extractor personalizado
        extractor_name = self.can_handle_url(url)
        
        if extractor_name:
            try:
                self.logger.info(f"Obteniendo información con extractor: {extractor_name}")
                extractor = self.custom_extractors[extractor_name]
                info = extractor.extract_video_info(url)
                
                if info:
                    return {
                        'title': info.get('title', 'Desconocido'),
                        'description': info.get('description', ''),
                        'duration': info.get('duration', 0),
                        'uploader': info.get('uploader', extractor_name),
                        'thumbnail': info.get('thumbnail'),
                        'source': info.get('source', extractor_name),
                        'video_urls_count': len(info.get('video_urls', []))
                    }
            except Exception as e:
                self.logger.error(f"Error obteniendo info con extractor personalizado: {e}")
        
        # Fallback al método estándar
        return super().get_video_info(url)
    
    def list_supported_sites(self):
        """
        Lista los sitios soportados
        
        Returns:
            dict: Diccionario con sitios soportados
        """
        supported = {
            'standard': [
                'youtube.com', 'youtu.be', 'vimeo.com', 
                'dailymotion.com', 'twitch.tv', 'facebook.com'
            ],
            'custom_extractors': list(self.custom_extractors.keys())
        }
        
        return supported

# Función de conveniencia para crear el downloader extendido
def create_extended_downloader(output_path=None, quality='720p', max_retries=3):
    """
    Crea una instancia del downloader extendido
    
    Args:
        output_path (str): Ruta de descarga
        quality (str): Calidad de video
        max_retries (int): Número de reintentos
        
    Returns:
        ExtendedAnimeDownloader: Instancia del downloader
    """
    return ExtendedAnimeDownloader(output_path, quality, max_retries)

if __name__ == "__main__":
    # Ejemplo de uso
    downloader = create_extended_downloader()
    
    # Listar sitios soportados
    supported = downloader.list_supported_sites()
    print("Sitios soportados:")
    print(f"  Estándar: {', '.join(supported['standard'])}")
    print(f"  Extractores personalizados: {', '.join(supported['custom_extractors'])}")
    
    # Ejemplo de URL de JKAnime
    jkanime_url = "https://jkanime.net/dandadan-2nd-season/12/"
    
    if downloader.can_handle_url(jkanime_url):
        print(f"\n✅ Puede manejar: {jkanime_url}")
        
        # Obtener información
        info = downloader.get_video_info(jkanime_url)
        if info:
            print(f"Título: {info['title']}")
            print(f"Fuente: {info.get('source', 'N/A')}")
    else:
        print(f"\n❌ No puede manejar: {jkanime_url}")
