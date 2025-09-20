#!/usr/bin/env python3
"""
Anime Downloader - Aplicación principal de línea de comandos
Permite descargar episodios de anime desde la terminal
"""

import argparse
import sys
import os
from pathlib import Path

from downloader import AnimeDownloader
from config import Config
from utils import setup_logging, validate_url, clean_filename

def main():
    """Función principal del programa"""
    parser = argparse.ArgumentParser(
        description='Descarga episodios de anime desde diferentes sitios web',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python main.py -u "https://ejemplo.com/anime/episodio-1" -q 720p
  python main.py -u "https://ejemplo.com/anime/episodio-1" -o "~/Descargas/Anime"
  python main.py --gui  # Abrir interfaz gráfica
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
        '-v', '--verbose',
        action='store_true',
        help='Mostrar información detallada'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='Anime Downloader 1.0.0'
    )
    
    args = parser.parse_args()
    
    # Configurar logging
    setup_logging(verbose=args.verbose)
    
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
        print("Usa --help para ver las opciones disponibles o --gui para la interfaz gráfica.")
        sys.exit(1)
    
    # Validar URL
    if not validate_url(args.url):
        print(f"Error: URL inválida: {args.url}")
        sys.exit(1)
    
    # Crear directorio de descarga si no existe
    output_path = Path(args.output).expanduser().resolve()
    output_path.mkdir(parents=True, exist_ok=True)
    
    print(f"🎌 Anime Downloader v1.0.0")
    print(f"📥 Descargando desde: {args.url}")
    print(f"🎥 Calidad: {args.quality}")
    print(f"📂 Destino: {output_path}")
    print("-" * 50)
    
    # Inicializar downloader
    downloader = AnimeDownloader(
        output_path=str(output_path),
        quality=args.quality,
        max_retries=Config.MAX_RETRIES,
        concurrent_downloads=Config.CONCURRENT_DOWNLOADS
    )
    
    try:
        # Realizar descarga
        success = downloader.download_episode(args.url)
        
        if success:
            print("✅ Descarga completada exitosamente!")
        else:
            print("❌ Error en la descarga. Revisa los logs para más detalles.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Descarga cancelada por el usuario.")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
