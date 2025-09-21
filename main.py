#!/usr/bin/env python3
"""
Anime Downloader - Aplicación principal extendida
Permite descargar episodios de anime desde múltiples sitios incluyendo JKAnime
"""

import argparse
import sys
import os
from pathlib import Path

try:
    from downloader_extended import ExtendedAnimeDownloader as AnimeDownloader
    EXTENDED_MODE = True
except ImportError:
    from downloader import AnimeDownloader
    EXTENDED_MODE = False

from config import Config
from utils import setup_logging, validate_url, clean_filename

def main():
    """Función principal del programa"""
    parser = argparse.ArgumentParser(
        description='Descarga episodios de anime desde diferentes sitios web incluyendo JKAnime',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  # YouTube
  python main.py -u "https://www.youtube.com/watch?v=VIDEO_ID" -q 720p
  
  # JKAnime
  python main.py -u "https://jkanime.net/dandadan-2nd-season/12/" -q 720p
  
  # Interfaz gráfica
  python main.py --gui
  
  # Listar sitios soportados
  python main.py --list-sites
        """
    )
    
    parser.add_argument(
        '-u', '--url',
        type=str,
        help='URL del episodio de anime a descargar'
    )
    
    parser.add_argument(
        '-q', '--quality',
        type=str,
        default=Config.DEFAULT_QUALITY,
        choices=['480p', '720p', '1080p', 'best'],
        help=f'Calidad de descarga (default: {Config.DEFAULT_QUALITY})'
    )
    
    parser.add_argument(
        '-o', '--output',
        type=str,
        default=Config.DOWNLOAD_PATH,
        help=f'Directorio de descarga (default: {Config.DOWNLOAD_PATH})'
    )
    
    parser.add_argument(
        '--gui',
        action='store_true',
        help='Abrir interfaz gráfica'
    )
    
    parser.add_argument(
        '--list-sites',
        action='store_true',
        help='Listar sitios web soportados'
    )
    
    parser.add_argument(
        '--info',
        action='store_true',
        help='Solo obtener información del video, no descargar'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Mostrar información detallada'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version=f'Anime Downloader v1.0.0 {"(Extended)" if EXTENDED_MODE else "(Standard)"}'
    )
    
    args = parser.parse_args()
    
    # Configurar logging
    setup_logging(verbose=args.verbose)
    
    # Mostrar modo
    mode_text = "🚀 MODO EXTENDIDO" if EXTENDED_MODE else "📺 MODO ESTÁNDAR"
    print(f"🎌 Anime Downloader v1.0.0 - {mode_text}")
    
    # Listar sitios soportados
    if args.list_sites:
        list_supported_sites()
        return
    
    # Si se especifica GUI, lanzar interfaz gráfica
    if args.gui:
        try:
            from gui import AnimeDownloaderGUI
            app = AnimeDownloaderGUI()
            app.run()
        except ImportError as e:
            print(f"Error: No se pudo cargar la interfaz gráfica: {e}")
            print("Instala las dependencias necesarias: pip install tkinter")
            sys.exit(1)
        return
    
    # Validar argumentos requeridos para CLI
    if not args.url:
        print("Error: Se requiere una URL para descargar.")
        print("Usa --help para ver las opciones disponibles o --list-sites para ver sitios soportados.")
        sys.exit(1)
    
    # Validar URL
    if not validate_url(args.url):
        print(f"Error: URL inválida: {args.url}")
        sys.exit(1)
    
    # Crear directorio de descarga si no existe
    output_path = Path(args.output).expanduser().resolve()
    output_path.mkdir(parents=True,
