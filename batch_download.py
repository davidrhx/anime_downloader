#!/usr/bin/env python3
"""
Anime Downloader - Descargas por lotes
Permite descargar múltiples episodios desde una lista de URLs
"""

import argparse
import sys
import os
from pathlib import Path
import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from downloader import AnimeDownloader
from config import Config
from utils import setup_logging, validate_url, clean_filename

class BatchDownloader:
    """Clase para manejar descargas por lotes"""
    
    def __init__(self, output_path=None, quality='720p', max_workers=2):
        """
        Inicializa el batch downloader
        
        Args:
            output_path (str): Directorio de descarga
            quality (str): Calidad de video
            max_workers (int): Número de descargas simultáneas
        """
        self.output_path = Path(output_path or Config.DOWNLOAD_PATH).expanduser().resolve()
        self.quality = quality
        self.max_workers = max_workers
        self.logger = logging.getLogger(__name__)
        
        # Crear directorio de salida
        self.output_path.mkdir(parents=True, exist_ok=True)
        
        # Estadísticas
        self.stats = {
            'total': 0,
            'successful': 0,
            'failed': 0,
            'skipped': 0,
            'start_time': None,
            'end_time': None
        }
        
    def load_urls_from_file(self, file_path):
        """
        Carga URLs desde un archivo de texto
        
        Args:
            file_path (str): Ruta del archivo con URLs
            
        Returns:
            list: Lista de URLs válidas
        """
        urls = []
        file_path = Path(file_path)
        
        if not file_path.exists():
            self.logger.error(f"Archivo no encontrado: {file_path}")
            return urls
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    
                    # Ignorar líneas vacías y comentarios
                    if not line or line.startswith('#'):
                        continue
                        
                    # Validar URL
                    if validate_url(line):
                        urls.append(line)
                    else:
                        self.logger.warning(f"URL inválida en línea {line_num}: {line}")
                        
        except Exception as e:
            self.logger.error(f"Error leyendo archivo {file_path}: {e}")
            
        self.logger.info(f"Cargadas {len(urls)} URLs válidas desde {file_path}")
        return urls
        
    def download_single(self, url, episode_num=None):
        """
        Descarga un episodio individual
        
        Args:
            url (str): URL del episodio
            episode_num (int): Número del episodio (opcional)
            
        Returns:
            dict: Resultado de la descarga
        """
        result = {
            'url': url,
            'episode': episode_num,
            'success': False,
            'error': None,
            'duration': 0
        }
        
        start_time = time.time()
        
        try:
            # Crear downloader individual
            downloader = AnimeDownloader(
                output_path=str(self.output_path),
                quality=self.quality,
                max_retries=Config.MAX_RETRIES
            )
            
            self.logger.info(f"Descargando episodio {episode_num or '?'}: {url}")
            
            # Realizar descarga
            success = downloader.download_episode(url)
            
            result['success'] = success
            result['duration'] = time.time() - start_time
            
            if success:
                self.stats['successful'] += 1
                self.logger.info(f"✅ Episodio {episode_num or '?'} descargado exitosamente")
            else:
                self.stats['failed'] += 1
                self.logger.error(f"❌ Error descargando episodio {episode_num or '?'}")
                
        except Exception as e:
            result['error'] = str(e)
            result['duration'] = time.time() - start_time
            self.stats['failed'] += 1
            self.logger.error(f"❌ Excepción en episodio {episode_num or '?'}: {e}")
            
        return result
        
    def download_batch(self, urls, progress_callback=None):
        """
        Descarga múltiples URLs en paralelo
        
        Args:
            urls (list): Lista de URLs
            progress_callback (callable): Función para reportar progreso
            
        Returns:
            dict: Resultados de la descarga por lotes
        """
        self.stats['total'] = len(urls)
        self.stats['start_time'] = time.time()
        
        self.logger.info(f"Iniciando descarga por lotes de {len(urls)} episodios")
        self.logger.info(f"Calidad: {self.quality}, Trabajadores: {self.max_workers}")
        
        results = []
        
        # Usar ThreadPoolExecutor para descargas paralelas
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Enviar todas las tareas
            future_to_url = {
                executor.submit(self.download_single, url, i+1): (url, i+1)
                for i, url in enumerate(urls)
            }
            
            # Procesar resultados conforme se completen
            for future in as_completed(future_to_url):
                url, episode_num = future_to_url[future]
                
                try:
                    result = future.result()
                    results.append(result)
                    
                    # Callback de progreso
                    if progress_callback:
                        progress_data = {
                            'completed': len(results),
                            'total': len(urls),
                            'current_episode': episode_num,
                            'current_url': url,
                            'success': result['success']
                        }
                        progress_callback(progress_data)
                        
                except Exception as e:
                    self.logger.error(f"Error obteniendo resultado para {url}: {e}")
                    results.append({
                        'url': url,
                        'episode': episode_num,
                        'success': False,
                        'error': str(e),
                        'duration': 0
                    })
                    self.stats['failed'] += 1
        
        self.stats['end_time'] = time.time()
        return self._generate_summary(results)
        
    def _generate_summary(self, results):
        """
        Genera resumen de la descarga por lotes
        
        Args:
            results (list): Lista de resultados de descarga
            
        Returns:
            dict: Resumen detallado
        """
        total_duration = self.stats['end_time'] - self.stats['start_time']
        successful_results = [r for r in results if r['success']]
        failed_results = [r for r in results if not r['success']]
        
        summary = {
            'stats': self.stats.copy(),
            'duration': total_duration,
            'successful_downloads': successful_results,
            'failed_downloads': failed_results,
            'success_rate': (self.stats['successful'] / self.stats['total'] * 100) if self.stats['total'] > 0 else 0,
            'average_time_per_download': sum(r['duration'] for r in successful_results) / len(successful_results) if successful_results else 0
        }
        
        return summary
        
    def print_summary(self, summary):
        """
        Imprime resumen de la descarga por lotes
        
        Args:
            summary (dict): Resumen generado por _generate_summary
        """
        stats = summary['stats']
        
        print("\n" + "="*60)
        print("🎌 RESUMEN DE DESCARGA POR LOTES")
        print("="*60)
        print(f"📊 Total de episodios: {stats['total']}")
        print(f"✅ Exitosas: {stats['successful']}")
        print(f"❌ Fallidas: {stats['failed']}")
        print(f"📈 Tasa de éxito: {summary['success_rate']:.1f}%")
        print(f"⏱️  Tiempo total: {summary['duration']:.1f} segundos")
        
        if summary['average_time_per_download'] > 0:
            print(f"⚡ Tiempo promedio por descarga: {summary['average_time_per_download']:.1f} segundos")
        
        # Mostrar descargas fallidas si las hay
        if summary['failed_downloads']:
            print(f"\n❌ DESCARGAS FALLIDAS ({len(summary['failed_downloads'])}):")
            for fail in summary['failed_downloads']:
                error_msg = fail['error'] or "Error desconocido"
                print(f"  • Episodio {fail['episode']}: {error_msg[:50]}...")
        
        print("="*60)
        
def create_sample_urls_file(filename="sample_urls.txt"):
    """
    Crea un archivo de ejemplo con URLs
    
    Args:
        filename (str): Nombre del archivo a crear
    """
    sample_content = """# Anime Downloader - Lista de URLs de ejemplo
# Líneas que empiecen con # son comentarios y serán ignoradas
# Una URL por línea

# Ejemplo de URLs (reemplaza con URLs reales):
# https://ejemplo.com/anime/serie/episodio-01
# https://ejemplo.com/anime/serie/episodio-02
# https://ejemplo.com/anime/serie/episodio-03

# También puedes usar URLs de YouTube como ejemplo:
# https://www.youtube.com/watch?v=VIDEO_ID_1
# https://www.youtube.com/watch?v=VIDEO_ID_2
"""
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(sample_content)
        print(f"✅ Archivo de ejemplo creado: {filename}")
        print(f"   Edita este archivo y agrega las URLs reales de los episodios")
    except Exception as e:
        print(f"❌ Error creando archivo de ejemplo: {e}")

def main():
    """Función principal para descarga por lotes"""
    parser = argparse.ArgumentParser(
        description='Descarga por lotes de episodios de anime',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python batch_download.py -f urls.txt -q 720p
  python batch_download.py -f episodes.txt -o "~/Anime/MiSerie" -w 3
  python batch_download.py --create-sample  # Crear archivo de ejemplo
        """
    )
    
    parser.add_argument(
        '-f', '--file',
        type=str,
        help='Archivo con lista de URLs (una por línea)'
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
        '-w', '--workers',
        type=int,
        default=Config.CONCURRENT_DOWNLOADS,
        help=f'Número de descargas simultáneas (default: {Config.CONCURRENT_DOWNLOADS})'
    )
    
    parser.add_argument(
        '--create-sample',
        action='store_true',
        help='Crear archivo de ejemplo con URLs'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Mostrar información detallada'
    )
    
    args = parser.parse_args()
    
    # Configurar logging
    setup_logging(verbose=args.verbose)
    
    # Crear archivo de ejemplo si se solicita
    if args.create_sample:
        create_sample_urls_file()
        return
    
    # Validar argumentos
    if not args.file:
        print("Error: Se requiere un archivo con URLs.")
        print("Usa --help para ver opciones o --create-sample para crear un archivo de ejemplo.")
        sys.exit(1)
    
    # Verificar que el archivo existe
    if not Path(args.file).exists():
        print(f"Error: Archivo no encontrado: {args.file}")
        print("Usa --create-sample para crear un archivo de ejemplo.")
        sys.exit(1)
    
    print(f"🎌 Anime Batch Downloader v1.0.0")
    print(f"📂 Archivo: {args.file}")
    print(f"🎥 Calidad: {args.quality}")
    print(f"📁 Destino: {args.output}")
    print(f"👥 Trabajadores: {args.workers}")
    print("-" * 50)
    
    # Crear batch downloader
    batch_downloader = BatchDownloader(
        output_path=args.output,
        quality=args.quality,
        max_workers=args.workers
    )
    
    # Cargar URLs
    urls = batch_downloader.load_urls_from_file(args.file)
    
    if not urls:
        print("❌ No se encontraron URLs válidas en el archivo.")
        sys.exit(1)
    
    # Función de callback para mostrar progreso
    def progress_callback(data):
        completed = data['completed']
        total = data['total']
        percentage = (completed / total) * 100
        current_ep = data['current_episode']
        status = "✅" if data['success'] else "❌"
        
        print(f"{status} Progreso: {completed}/{total} ({percentage:.1f}%) - Episodio {current_ep}")
    
    try:
        # Realizar descarga por lotes
        summary = batch_downloader.download_batch(urls, progress_callback)
        
        # Mostrar resumen
        batch_downloader.print_summary(summary)
        
        # Código de salida basado en el éxito
        if summary['stats']['failed'] == 0:
            print("🎉 ¡Todas las descargas completadas exitosamente!")
            sys.exit(0)
        elif summary['stats']['successful'] > 0:
            print("⚠️  Algunas descargas fallaron. Revisa el log para más detalles.")
            sys.exit(1)
        else:
            print("💥 Todas las descargas fallaron.")
            sys.exit(2)
            
    except KeyboardInterrupt:
        print("\n🛑 Descarga por lotes cancelada por el usuario.")
        sys.exit(0)
    except Exception as e:
        print(f"💥 Error inesperado: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()