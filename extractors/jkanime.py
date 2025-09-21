"""
JKAnime Extractor - Extractor específico para jkanime.net
Permite descargar videos desde JKAnime
"""

import re
import json
import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import logging
import time

from utils import clean_filename, format_bytes

class JKAnimeExtractor:
    """Extractor para jkanime.net"""
    
    def __init__(self):
        """Inicializa el extractor de JKAnime"""
        self.logger = logging.getLogger(__name__)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        self.base_url = 'https://jkanime.net'
        
    def can_handle(self, url):
        """
        Verifica si la URL es de JKAnime
        
        Args:
            url (str): URL a verificar
            
        Returns:
            bool: True si puede manejar esta URL
        """
        return 'jkanime.net' in url
    
    def extract_video_info(self, url):
        """
        Extrae información del video de JKAnime
        
        Args:
            url (str): URL del episodio
            
        Returns:
            dict: Información del video extraída
        """
        try:
            self.logger.info(f"Extrayendo información de JKAnime: {url}")
            
            # Realizar request a la página principal
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extraer título del anime y episodio
            title_element = soup.find('h1') or soup.find('title')
            if title_element:
                title = title_element.get_text().strip()
                title = clean_filename(title)
            else:
                # Extraer título de la URL como fallback
                path_parts = urlparse(url).path.strip('/').split('/')
                if len(path_parts) >= 2:
                    anime_name = path_parts[0].replace('-', ' ').title()
                    episode = path_parts[1] if len(path_parts) > 1 else '1'
                    title = f"{anime_name} - Episodio {episode}"
                else:
                    title = "JKAnime Episode"
            
            # Buscar información adicional
            description = ""
            desc_element = soup.find('div', class_='sinopsis') or soup.find('div', class_='description')
            if desc_element:
                description = desc_element.get_text().strip()[:200]
            
            # Extraer enlaces de video
            video_urls = self._extract_video_urls(soup, url)
            
            video_info = {
                'title': title,
                'description': description,
                'video_urls': video_urls,
                'thumbnail': self._extract_thumbnail(soup),
                'duration': 0,  # JKAnime no siempre proporciona duración
                'uploader': 'JKAnime',
                'source': 'jkanime.net'
            }
            
            self.logger.info(f"Información extraída: {title}")
            self.logger.info(f"Enlaces de video encontrados: {len(video_urls)}")
            
            return video_info
            
        except Exception as e:
            self.logger.error(f"Error extrayendo información de JKAnime: {e}")
            return None
    
    def _extract_video_urls(self, soup, page_url):
        """
        Extrae URLs de video de la página de JKAnime
        
        Args:
            soup (BeautifulSoup): Contenido HTML parseado
            page_url (str): URL de la página principal
            
        Returns:
            list: Lista de URLs de video encontradas
        """
        video_urls = []
        
        try:
            # Método 1: Buscar scripts que contengan URLs de video
            script_tags = soup.find_all('script')
            
            for script in script_tags:
                if script.string:
                    script_content = script.string
                    
                    # Buscar patrones comunes de URLs de video
                    video_patterns = [
                        r'https?://[^"\s]+\.m3u8[^"\s]*',
                        r'https?://[^"\s]+\.mp4[^"\s]*',
                        r'https?://[^"\s]+/playlist\.m3u8[^"\s]*',
                        r'"file":\s*"([^"]+)"',
                        r'"url":\s*"([^"]+)"',
                        r'source:\s*"([^"]+)"',
                    ]
                    
                    for pattern in video_patterns:
                        matches = re.findall(pattern, script_content, re.IGNORECASE)
                        for match in matches:
                            # Limpiar la URL
                            if isinstance(match, tuple):
                                url = match[0] if match else None
                            else:
                                url = match
                            
                            if url and self._is_valid_video_url(url):
                                if not url.startswith('http'):
                                    url = urljoin(self.base_url, url)
                                video_urls.append(url)
            
            # Método 2: Buscar iframes con reproductores
            iframes = soup.find_all('iframe')
            for iframe in iframes:
                src = iframe.get('src')
                if src and ('player' in src or 'embed' in src):
                    if not src.startswith('http'):
                        src = urljoin(self.base_url, src)
                    
                    # Intentar extraer video del iframe
                    iframe_urls = self._extract_from_iframe(src)
                    video_urls.extend(iframe_urls)
            
            # Método 3: Buscar enlaces directos en la página
            video_links = soup.find_all('a', href=True)
            for link in video_links:
                href = link['href']
                if any(ext in href for ext in ['.mp4', '.m3u8', 'video']):
                    if not href.startswith('http'):
                        href = urljoin(self.base_url, href)
                    video_urls.append(href)
            
            # Eliminar duplicados y filtrar
            video_urls = list(set(video_urls))
            video_urls = [url for url in video_urls if self._is_valid_video_url(url)]
            
            return video_urls
            
        except Exception as e:
            self.logger.error(f"Error extrayendo URLs de video: {e}")
            return []
    
    def _extract_from_iframe(self, iframe_url):
        """
        Extrae URLs de video desde un iframe
        
        Args:
            iframe_url (str): URL del iframe
            
        Returns:
            list: URLs de video encontradas
        """
        try:
            self.logger.debug(f"Extrayendo desde iframe: {iframe_url}")
            
            # Pequeña pausa para evitar rate limiting
            time.sleep(1)
            
            response = self.session.get(iframe_url, timeout=15)
            response.raise_for_status()
            
            iframe_soup = BeautifulSoup(response.content, 'html.parser')
            return self._extract_video_urls(iframe_soup, iframe_url)
            
        except Exception as e:
            self.logger.debug(f"Error extrayendo desde iframe {iframe_url}: {e}")
            return []
    
    def _extract_thumbnail(self, soup):
        """
        Extrae URL de thumbnail/miniatura
        
        Args:
            soup (BeautifulSoup): Contenido HTML parseado
            
        Returns:
            str: URL de la miniatura o None
        """
        try:
            # Buscar meta tags de imagen
            og_image = soup.find('meta', property='og:image')
            if og_image:
                return og_image.get('content')
            
            # Buscar imágenes en la página
            img_tags = soup.find_all('img')
            for img in img_tags:
                src = img.get('src') or img.get('data-src')
                if src and ('thumb' in src or 'poster' in src or 'cover' in src):
                    if not src.startswith('http'):
                        src = urljoin(self.base_url, src)
                    return src
            
            return None
            
        except Exception as e:
            self.logger.debug(f"Error extrayendo thumbnail: {e}")
            return None
    
    def _is_valid_video_url(self, url):
        """
        Verifica si una URL es válida para video
        
        Args:
            url (str): URL a verificar
            
        Returns:
            bool: True si es una URL de video válida
        """
        if not url or len(url) < 10:
            return False
        
        # Filtrar URLs no deseadas
        invalid_patterns = [
            'javascript:',
            'mailto:',
            '.css',
            '.js',
            '.png',
            '.jpg',
            '.gif',
            'facebook.com',
            'twitter.com',
            'instagram.com'
        ]
        
        if any(pattern in url.lower() for pattern in invalid_patterns):
            return False
        
        # Verificar patrones válidos
        valid_patterns = [
            '.mp4',
            '.m3u8',
            'video',
            'stream',
            'player',
            'embed'
        ]
        
        return any(pattern in url.lower() for pattern in valid_patterns)
    
    def download_video(self, video_info, output_path, progress_callback=None):
        """
        Descarga el video usando las URLs extraídas
        
        Args:
            video_info (dict): Información del video
            output_path (str): Ruta donde guardar el video
            progress_callback (callable): Función de callback para progreso
            
        Returns:
            bool: True si la descarga fue exitosa
        """
        video_urls = video_info.get('video_urls', [])
        
        if not video_urls:
            self.logger.error("No se encontraron URLs de video válidas")
            return False
        
        self.logger.info(f"Intentando descargar desde {len(video_urls)} URL(s)")
        
        # Intentar cada URL hasta que una funcione
        for i, url in enumerate(video_urls):
            try:
                self.logger.info(f"Probando URL {i+1}/{len(video_urls)}: {url}")
                
                # Usar yt-dlp para descargar la URL extraída
                import yt_dlp
                
                ydl_opts = {
                    'outtmpl': f"{output_path}/{video_info['title']}.%(ext)s",
                    'format': 'best',
                    'ignoreerrors': True,
                    'no_warnings': False,
                    'socket_timeout': 30,
                    'http_headers': self.session.headers,
                }
                
                if progress_callback:
                    def safe_progress_hook(data):
                        try:
                            if data.get('status') == 'downloading':
                                progress_callback({
                                    'status': 'downloading',
                                    'percentage': data.get('_percent_str', '0%').replace('%', ''),
                                    'speed': data.get('_speed_str', 'N/A'),
                                    'eta': data.get('_eta_str', 'N/A'),
                                })
                        except:
                            pass
                    
                    ydl_opts['progress_hooks'] = [safe_progress_hook]
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                
                self.logger.info("✅ Descarga de JKAnime completada exitosamente")
                return True
                
            except Exception as e:
                self.logger.warning(f"Error con URL {i+1}: {e}")
                continue
        
        self.logger.error("❌ No se pudo descargar desde ninguna URL")
        return False

def create_jkanime_extractor():
    """Factory function para crear extractor de JKAnime"""
    return JKAnimeExtractor()
