#!/bin/bash

# Script de instalación para soporte de JKAnime
# Este script agrega el extractor de JKAnime al Anime Downloader

set -e

# Colores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}"
echo "╔═══════════════════════════════════════╗"
echo "║     JKAnime Extractor Installer      ║"
echo "║         Anime Downloader v1.0        ║"
echo "╚═══════════════════════════════════════╝"
echo -e "${NC}"

# Verificar que estamos en el directorio correcto
if [ ! -f "main.py" ] || [ ! -f "downloader.py" ]; then
    echo -e "${RED}Error: Ejecuta este script desde el directorio del proyecto anime-downloader${NC}"
    exit 1
fi

# Crear directorio de extractores
echo -e "${BLUE}[INFO]${NC} Creando directorio de extractores..."
mkdir -p extractors

# Crear __init__.py para hacer el directorio un paquete Python
cat > extractors/__init__.py << 'EOF'
"""
Extractors package - Extractores personalizados para sitios de anime
"""

__version__ = '1.0.0'
__all__ = ['jkanime']
EOF

# Verificar si los archivos necesarios están presentes
if [ ! -f "extractors/jkanime.py" ]; then
    echo -e "${RED}Error: extractors/jkanime.py no encontrado${NC}"
    echo "Por favor copia el archivo jkanime.py al directorio extractors/"
    exit 1
fi

if [ ! -f "downloader_extended.py" ]; then
    echo -e "${RED}Error: downloader_extended.py no encontrado${NC}"
    echo "Por favor copia el archivo downloader_extended.py al directorio raíz"
    exit 1
fi

# Instalar dependencias adicionales para web scraping
echo -e "${BLUE}[INFO]${NC} Instalando dependencias adicionales..."

if [ -f "anime-downloader-env/bin/activate" ]; then
    source anime-downloader-env/bin/activate
    echo -e "${GREEN}[SUCCESS]${NC} Entorno virtual activado"
else
    echo -e "${RED}Error: Entorno virtual no encontrado${NC}"
    echo "Ejecuta primero: ./install.sh"
    exit 1
fi

# Instalar dependencias para web scraping
pip install beautifulsoup4 lxml requests --upgrade

# Hacer backup del main.py original si no existe
if [ ! -f "main.py.backup" ]; then
    echo -e "${BLUE}[INFO]${NC} Creando backup de main.py..."
    cp main.py main.py.backup
fi

# Reemplazar main.py con la versión extendida si existe
if [ -f "main_extended.py" ]; then
    echo -e "${BLUE}[INFO]${NC} Actualizando main.py con soporte extendido..."
    cp main_extended.py main.py
fi

# Crear script de prueba para JKAnime
cat > test_jkanime.py << 'EOF'
#!/usr/bin/env python3
"""
Script de prueba para el extractor de JKAnime
"""

import sys
from downloader_extended import ExtendedAnimeDownloader

def test_jkanime():
    """Prueba el extractor de JKAnime"""
    
    # URL de prueba
    test_url = "https://jkanime.net/dandadan-2nd-season/12/"
    
    print("🎌 Probando extractor de JKAnime...")
    print(f"URL de prueba: {test_url}")
    print("-" * 50)
    
    try:
        # Crear downloader
        downloader = ExtendedAnimeDownloader()
        
        # Verificar si puede manejar la URL
        if downloader.can_handle_url(test_url):
            print("✅ Extractor puede manejar la URL")
            
            # Obtener información
            print("📋 Obteniendo información del video...")
            info = downloader.get_video_info(test_url)
            
            if info:
                print(f"  Título: {info.get('title', 'N/A')}")
                print(f"  Fuente: {info.get('source', 'N/A')}")
                print(f"  URLs encontradas: {info.get('video_urls_count', 0)}")
                
                if info.get('description'):
                    desc = info['description'][:100]
                    print(f"  Descripción: {desc}...")
                
                print("\n✅ ¡Extractor funcionando correctamente!")
                print("\nPara descargar:")
                print(f"python main.py -u \"{test_url}\" -q 720p")
                
            else:
                print("❌ No se pudo obtener información")
                return False
                
        else:
            print("❌ Extractor no puede manejar esta URL")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = test_jkanime()
    sys.exit(0 if success else 1)
EOF

chmod +x test_jkanime.py

# Actualizar requirements.txt
echo -e "${BLUE}[INFO]${NC} Actualizando requirements.txt..."
if ! grep -q "beautifulsoup4" requirements.txt; then
    echo "beautifulsoup4>=4.12.2" >> requirements.txt
fi
if ! grep -q "lxml" requirements.txt; then
    echo "lxml>=4.9.3" >> requirements.txt
fi

# Crear script de inicio para JKAnime
cat > start_jkanime.sh << 'EOF'
#!/bin/bash
# Script de inicio rápido para descargas de JKAnime

source anime-downloader-env/bin/activate

echo "🎌 Anime Downloader - JKAnime Ready"
echo ""
echo "Ejemplos de uso:"
echo ""
echo "# Obtener información:"
echo "python main.py -u \"https://jkanime.net/dandadan-2nd-season/12/\" --info"
echo ""
echo "# Descargar episodio:"
echo "python main.py -u \"https://jkanime.net/dandadan-2nd-season/12/\" -q 720p"
echo ""
echo "# Abrir GUI:"
echo "python main.py --gui"
echo ""

# Si se pasaron argumentos, ejecutarlos
if [ $# -gt 0 ]; then
    python main.py "$@"
fi
EOF

chmod +x start_jkanime.sh

# Probar la instalación
echo -e "${BLUE}[INFO]${NC} Probando instalación..."
if python test_jkanime.py; then
    echo -e "${GREEN}[SUCCESS]${NC} ¡Instalación de JKAnime completada exitosamente!"
    
    echo ""
    echo -e "${GREEN}┌─ Cómo usar JKAnime ─┐${NC}"
    echo ""
    echo "🎯 Ejemplos de uso:"
    echo ""
    echo "# Información del video:"
    echo "./start_jkanime.sh -u \"https://jkanime.net/dandadan-2nd-season/12/\" --info"
    echo ""
    echo "# Descargar episodio:"
    echo "./start_jkanime.sh -u \"https://jkanime.net/dandadan-2nd-season/12/\" -q 720p"
    echo ""
    echo "# Ver sitios soportados:"
    echo "./start_jkanime.sh --list-sites"
    echo ""
    echo "# GUI con soporte JKAnime:"
    echo "./start_jkanime.sh --gui"
    echo ""
    
else
    echo -e "${RED}[ERROR]${NC} Error en la instalación. Revisa los archivos y vuelve a intentar."
    exit 1
fi

echo -e "${BLUE}[INFO]${NC} Archivos creados:"
echo "  ✅ extractors/jkanime.py - Extractor de JKAnime"
echo "  ✅ downloader_extended.py - Downloader extendido"  
echo "  ✅ main.py - Actualizado con soporte extendido"
echo "  ✅ test_jkanime.py - Script de prueba"
echo "  ✅ start_jkanime.sh - Script de inicio rápido"
echo ""
echo -e "${GREEN}🎌 ¡JKAnime listo para usar!${NC}"
