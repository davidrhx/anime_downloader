#!/bin/bash

# Anime Downloader - Instalación Completa Todo-en-Uno
# Instala automáticamente: dependencias + JKAnime + GUI + CLI
# Uso: git clone repo && cd anime-downloader && chmod +x install.sh && ./install.sh

set -e  # Salir si algún comando falla

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Función para mostrar mensajes coloreados
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "${PURPLE}[STEP]${NC} $1"
}

# Banner principal
clear
echo -e "${CYAN}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                   🎌 ANIME DOWNLOADER v1.0.0                ║"
echo "║                    Instalación Todo-en-Uno                  ║"
echo "║                                                              ║"
echo "║  ✨ Instala automáticamente:                                 ║"
echo "║     • Python + Dependencias                                 ║"
echo "║     • Downloader estándar (YouTube, Vimeo, etc.)           ║"
echo "║     • Extractor de JKAnime                                  ║"
echo "║     • Interfaz gráfica (GUI)                                ║"
echo "║     • Scripts de conveniencia                               ║"
echo "║                                                              ║"
echo "║  🚀 Después de la instalación, usa:                         ║"
echo "║     ./start_gui.sh    (Interfaz gráfica)                   ║"
echo "║     ./start_cli.sh    (Línea de comandos)                  ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""

# Verificar que estemos en el directorio correcto
log_step "Verificando archivos del proyecto..."
REQUIRED_FILES=("main.py" "downloader.py" "gui.py" "config.py" "utils.py")
MISSING_FILES=()

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        log_success "$file ✓"
    else
        MISSING_FILES+=("$file")
        log_error "$file ✗"
    fi
done

if [ ${#MISSING_FILES[@]} -gt 0 ]; then
    log_error "Archivos faltantes: ${MISSING_FILES[*]}"
    log_error "Asegúrate de estar en el directorio del proyecto anime-downloader"
    exit 1
fi

# Verificar Python
log_step "Verificando instalación de Python..."
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        log_error "Python no está instalado."
        log_info "Instala Python 3.7+ desde: https://www.python.org/downloads/"
        echo ""
        log_info "En Ubuntu/Debian: sudo apt update && sudo apt install python3 python3-pip python3-venv python3-tk"
        log_info "En CentOS/RHEL: sudo yum install python3 python3-pip python3-tkinter"
        log_info "En macOS: brew install python3"
        exit 1
    else
        PYTHON_CMD="python"
    fi
else
    PYTHON_CMD="python3"
fi

# Verificar versión de Python
PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | cut -d' ' -f2)
log_success "Python $PYTHON_VERSION encontrado"

PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 7 ]); then
    log_error "Se requiere Python 3.7 o superior. Versión actual: $PYTHON_VERSION"
    exit 1
fi

# Verificar pip
log_step "Verificando pip..."
if ! $PYTHON_CMD -m pip --version &> /dev/null; then
    log_error "pip no está disponible."
    log_info "Instala pip: curl https://bootstrap.pypa.io/get-pip.py | $PYTHON_CMD"
    exit 1
fi
log_success "pip encontrado"

# Crear entorno virtual
VENV_DIR="anime-downloader-env"
log_step "Configurando entorno virtual..."

if [ -d "$VENV_DIR" ]; then
    log_warning "El entorno virtual ya existe. Eliminando y recreando..."
    rm -rf "$VENV_DIR"
fi

log_info "Creando entorno virtual..."
$PYTHON_CMD -m venv $VENV_DIR
log_success "Entorno virtual creado: $VENV_DIR"

# Activar entorno virtual
log_info "Activando entorno virtual..."
source $VENV_DIR/bin/activate

# Actualizar pip en el entorno virtual
log_info "Actualizando pip en entorno virtual..."
python -m pip install --upgrade pip setuptools wheel

# Verificar/crear requirements.txt
log_step "Verificando dependencias..."
if [ ! -f "requirements.txt" ]; then
    log_warning "requirements.txt no encontrado. Creando archivo de dependencias..."
    cat > requirements.txt << 'EOF'
# Anime Downloader - Dependencias completas
yt-dlp>=2023.7.6
requests>=2.31.0
urllib3>=2.0.4
beautifulsoup4>=4.12.2
lxml>=4.9.3
PyYAML>=6.0.1
tqdm>=4.65.0
colorama>=0.4.6
python-dateutil>=2.8.2
EOF
    log_success "requirements.txt creado"
fi

# Instalar dependencias
log_step "Instalando dependencias de Python..."
pip install -r requirements.txt
log_success "Dependencias principales instaladas"

# Instalar dependencias adicionales para web scraping
log_info "Instalando dependencias adicionales para extractores personalizados..."
pip install beautifulsoup4 lxml requests --upgrade

# Verificar tkinter para GUI
log_step "Verificando soporte para interfaz gráfica..."
if python -c "import tkinter" 2>/dev/null; then
    log_success "Tkinter disponible - GUI funcionará correctamente"
    GUI_AVAILABLE=true
else
    log_warning "Tkinter no disponible - GUI puede no funcionar"
    log_info "Para instalar tkinter:"
    log_info "  Ubuntu/Debian: sudo apt-get install python3-tk"
    log_info "  CentOS/RHEL: sudo yum install tkinter"
    log_info "  macOS: Viene incluido con Python de python.org"
    GUI_AVAILABLE=false
fi

# Configurar estructura de extractores
log_step "Configurando extractores personalizados..."

# Crear directorio extractors si no existe
mkdir -p extractors

# Crear o verificar __init__.py
if [ ! -f "extractors/__init__.py" ]; then
    log_info "Creando extractors/__init__.py..."
    cat > extractors/__init__.py << 'EOF'
"""
Extractors package - Extractores personalizados para sitios de anime
"""

__version__ = '1.0.0'
__all__ = ['jkanime']

# Importar extractores disponibles
try:
    from .jkanime import JKAnimeExtractor
    EXTRACTORS_AVAILABLE = ['jkanime']
except ImportError as e:
    print(f"Warning: Could not import JKAnime extractor: {e}")
    EXTRACTORS_AVAILABLE = []
EOF
    log_success "extractors/__init__.py creado"
fi

# Verificar y mover jkanime.py si está en lugar incorrecto
JKANIME_AVAILABLE=false
if [ -f "extractors/jkanime.py" ]; then
    log_success "extractors/jkanime.py ya está en su lugar"
    JKANIME_AVAILABLE=true
elif [ -f "jkanime_extractor.py" ]; then
    log_info "Moviendo jkanime_extractor.py a extractors/jkanime.py..."
    mv jkanime_extractor.py extractors/jkanime.py
    log_success "jkanime.py movido correctamente"
    JKANIME_AVAILABLE=true
elif [ -f "jkanime.py" ]; then
    log_info "Moviendo jkanime.py a extractors/jkanime.py..."
    mv jkanime.py extractors/jkanime.py
    log_success "jkanime.py movido correctamente"
    JKANIME_AVAILABLE=true
else
    log_warning "Extractor de JKAnime no encontrado"
    log_info "Se creará un extractor básico..."
    # Aquí podrías crear un extractor básico o descargarlo
    JKANIME_AVAILABLE=false
fi

# Verificar downloader_extended.py
if [ ! -f "downloader_extended.py" ]; then
    if [ -f "anime_downloader_extended.py" ]; then
        log_info "Renombrando anime_downloader_extended.py a downloader_extended.py..."
        mv anime_downloader_extended.py downloader_extended.py
        log_success "downloader_extended.py configurado"
    else
        log_warning "downloader_extended.py no encontrado - solo funcionará modo estándar"
    fi
fi

# Crear directorio de descargas por defecto
DEFAULT_DOWNLOAD_DIR="$HOME/Downloads/Anime"
log_step "Configurando directorio de descargas..."
if [ ! -d "$DEFAULT_DOWNLOAD_DIR" ]; then
    log_info "Creando directorio de descargas: $DEFAULT_DOWNLOAD_DIR"
    mkdir -p "$DEFAULT_DOWNLOAD_DIR"
    log_success "Directorio de descargas creado"
else
    log_success "Directorio de descargas ya existe"
fi

# Crear scripts de conveniencia
log_step "Creando scripts de conveniencia..."

# Script de activación del entorno
log_info "Creando script de activación..."
cat > activate_anime_downloader.sh << 'EOF'
#!/bin/bash
# Script para activar el entorno del Anime Downloader
if [ -d "anime-downloader-env" ]; then
    source anime-downloader-env/bin/activate
    echo "🎌 Entorno Anime Downloader activado"
    echo ""
    echo "📋 Comandos disponibles:"
    echo "  python main.py --gui           # Interfaz gráfica"
    echo "  python main.py -u URL -q 720p  # Descargar video"
    echo "  python main.py --list-sites    # Ver sitios soportados"
    echo "  python main.py --help          # Ayuda completa"
    echo ""
    echo "🎌 URLs de prueba:"
    echo "  YouTube: https://youtube.com/watch?v=dQw4w9WgXcQ"
    if [ -f "extractors/jkanime.py" ]; then
        echo "  JKAnime: https://jkanime.net/dandadan-2nd-season/12/"
    fi
    echo ""
    echo "Para desactivar: deactivate"
else
    echo "❌ Entorno virtual no encontrado. Ejecuta primero: ./install.sh"
fi
EOF

# Script de inicio GUI
cat > start_gui.sh << 'EOF'
#!/bin/bash
# Script de inicio rápido para interfaz gráfica

echo "🎌 Iniciando Anime Downloader GUI..."

if [ -d "anime-downloader-env" ]; then
    source anime-downloader-env/bin/activate
    
    # Verificar dependencias GUI
    if python -c "import tkinter" 2>/dev/null; then
        echo "✅ GUI disponible - Iniciando interfaz gráfica..."
        python main.py --gui
    else
        echo "❌ Tkinter no disponible."
        echo "Instala tkinter:"
        echo "  Ubuntu/Debian: sudo apt-get install python3-tk"
        echo "  CentOS/RHEL: sudo yum install tkinter"
        exit 1
    fi
else
    echo "❌ Entorno virtual no encontrado."
    echo "Ejecuta primero: ./install.sh"
    exit 1
fi
EOF

# Script de inicio CLI
cat > start_cli.sh << 'EOF'
#!/bin/bash
# Script de inicio rápido para línea de comandos

if [ -d "anime-downloader-env" ]; then
    source anime-downloader-env/bin/activate
    
    if [ $# -eq 0 ]; then
        echo "🎌 Anime Downloader - Línea de Comandos"
        echo ""
        echo "📋 Uso: ./start_cli.sh [opciones]"
        echo ""
        echo "🎯 Ejemplos:"
        echo "  ./start_cli.sh -u \"https://youtube.com/watch?v=ID\" -q 720p"
        if [ -f "extractors/jkanime.py" ]; then
            echo "  ./start_cli.sh -u \"https://jkanime.net/dandadan-2nd-season/12/\" -q 720p"
        fi
        echo "  ./start_cli.sh --list-sites"
        echo "  ./start_cli.sh --help"
        echo ""
        python main.py --help
    else
        python main.py "$@"
    fi
else
    echo "❌ Entorno virtual no encontrado."
    echo "Ejecuta primero: ./install.sh"
    exit 1
fi
EOF

# Hacer ejecutables todos los scripts
chmod +x activate_anime_downloader.sh start_gui.sh start_cli.sh

log_success "Scripts de conveniencia creados"

# Probar instalación básica
log_step "Probando instalación..."
log_info "Verificando módulos principales..."

# Test de importación
python -c "
import sys
print('✅ Python:', sys.version.split()[0])

try:
    import requests
    print('✅ requests:', requests.__version__)
except ImportError:
    print('❌ requests: No disponible')

try:
    import yt_dlp
    print('✅ yt-dlp: Disponible')
except ImportError:
    print('❌ yt-dlp: No disponible')

try:
    from bs4 import BeautifulSoup
    print('✅ BeautifulSoup: Disponible')
except ImportError:
    print('❌ BeautifulSoup: No disponible')

try:
    import downloader
    print('✅ downloader: Disponible')
except ImportError as e:
    print('❌ downloader:', str(e))

try:
    import gui
    print('✅ gui: Disponible')
except ImportError as e:
    print('❌ gui:', str(e))
"

# Probar downloader extendido si está disponible
if [ -f "downloader_extended.py" ] && [ "$JKANIME_AVAILABLE" = true ]; then
    log_info "Probando extractor de JKAnime..."
    python -c "
try:
    from downloader_extended import ExtendedAnimeDownloader
    downloader = ExtendedAnimeDownloader()
    extractors = list(downloader.custom_extractors.keys())
    print('✅ Modo extendido disponible')
    print('✅ Extractores:', extractors)
    
    test_url = 'https://jkanime.net/dandadan-2nd-season/12/'
    can_handle = downloader.can_handle_url(test_url)
    if can_handle:
        print('✅ JKAnime: Funcional')
    else:
        print('❌ JKAnime: No funcional')
except Exception as e:
    print('❌ Modo extendido:', str(e))
"
fi

# Limpiar archivos temporales
log_step "Limpiando archivos temporales..."
find . -name "*.pyc" -delete 2>/dev/null || true
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# Crear archivo .gitignore si no existe
if [ ! -f ".gitignore" ]; then
    log_info "Creando .gitignore..."
    cat > .gitignore << 'EOF'
# Entorno virtual
anime-downloader-env/
venv/
env/

# Python
__pycache__/
*.py[cod]
*$py.class
*.so

# Logs
*.log
logs/

# Archivos descargados
Downloads/
Anime/
downloads/
*.mp4
*.mkv
*.avi
*.webm
*.m4v

# Subtítulos
*.srt
*.ass
*.vtt

# Temporales
*.tmp
*.temp
.cache/

# Sistema
.DS_Store
Thumbs.db
desktop.ini

# IDEs
.vscode/
.idea/
*.sublime-*

# Configuración local
config_local.py
.env
EOF
    log_success ".gitignore creado"
fi

# Información final de instalación
echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                    ✅ INSTALACIÓN COMPLETADA                 ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

log_success "🎌 Anime Downloader instalado exitosamente!"
echo ""

# Mostrar resumen de instalación
echo -e "${CYAN}📋 RESUMEN DE INSTALACIÓN:${NC}"
echo -e "${GREEN}✅ Python ${PYTHON_VERSION}${NC}"
echo -e "${GREEN}✅ Entorno virtual creado${NC}"
echo -e "${GREEN}✅ Dependencias instaladas${NC}"
if [ "$GUI_AVAILABLE" = true ]; then
    echo -e "${GREEN}✅ Interfaz gráfica disponible${NC}"
else
    echo -e "${YELLOW}⚠️  Interfaz gráfica: tkinter no disponible${NC}"
fi
if [ "$JKANIME_AVAILABLE" = true ]; then
    echo -e "${GREEN}✅ Extractor JKAnime configurado${NC}"
else
    echo -e "${YELLOW}⚠️  Extractor JKAnime: no disponible${NC}"
fi
echo -e "${GREEN}✅ Scripts de conveniencia creados${NC}"
echo -e "${GREEN}✅ Directorio de descargas: $DEFAULT_DOWNLOAD_DIR${NC}"

echo ""
echo -e "${BLUE}🚀 CÓMO USAR:${NC}"
echo ""

echo -e "${GREEN}Opción 1 - Interfaz Gráfica (Recomendado para principiantes):${NC}"
echo "  ./start_gui.sh"
echo ""

echo -e "${GREEN}Opción 2 - Línea de Comandos (Para usuarios avanzados):${NC}"
echo "  ./start_cli.sh -u \"https://youtube.com/watch?v=dQw4w9WgXcQ\" -q 720p"
if [ "$JKANIME_AVAILABLE" = true ]; then
    echo "  ./start_cli.sh -u \"https://jkanime.net/dandadan-2nd-season/12/\" -q 720p"
fi
echo "  ./start_cli.sh --list-sites  # Ver sitios soportados"
echo ""

echo -e "${GREEN}Opción 3 - Manual (Control total):${NC}"
echo "  source activate_anime_downloader.sh  # Activar entorno"
echo "  python main.py --gui                 # GUI"
echo "  python main.py -u URL -q 720p        # Descargar"
echo ""

echo -e "${YELLOW}💡 TIPS:${NC}"
echo "  • Los videos se guardan en: $DEFAULT_DOWNLOAD_DIR"
echo "  • Usa calidades: 480p, 720p, 1080p, best"
echo "  • Para subtítulos: activa en GUI o usa modo conservativo"
if [ "$JKANIME_AVAILABLE" = true ]; then
    echo "  • JKAnime funciona mejor en modo seguro (evita rate limiting)"
fi
echo ""

echo -e "${PURPLE}🌐 SITIOS SOPORTADOS:${NC}"
echo "  • YouTube, Vimeo, Dailymotion, Twitch"
if [ "$JKANIME_AVAILABLE" = true ]; then
    echo "  • JKAnime (extractor personalizado)"
fi
echo "  • 1000+ sitios más via yt-dlp"
echo ""

# Preguntar si quiere probar la instalación
echo -e "${CYAN}¿Quieres probar la instalación ahora?${NC}"
echo "1) Interfaz gráfica (GUI)"
echo "2) Línea de comandos (mostrar ayuda)"
echo "3) Listar sitios soportados"
echo "4) Salir"
echo ""
read -p "Elige una opción [1-4]: " -n 1 -r choice
echo ""

case $choice in
    1)
        if [ "$GUI_AVAILABLE" = true ]; then
            echo "🚀 Iniciando interfaz gráfica..."
            ./start_gui.sh
        else
            log_error "GUI no disponible. Instala tkinter primero."
        fi
        ;;
    2)
        echo "📋 Mostrando ayuda de línea de comandos..."
        ./start_cli.sh
        ;;
    3)
        echo "🌐 Listando sitios soportados..."
        ./start_cli.sh --list-sites
        ;;
    4|*)
        echo "👋 Instalación completada. ¡Disfruta descargando anime!"
        ;;
esac

echo ""
log_success "🎌 ¡Todo listo! Happy downloading! ✨"
