#!/bin/bash

# Anime Downloader - Script de instalación automático
# Este script configura el entorno e instala todas las dependencias

set -e  # Salir si algún comando falla

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

# Banner
echo -e "${BLUE}"
echo "╔═══════════════════════════════════════╗"
echo "║        Anime Downloader v1.0.0       ║"
echo "║           Script de Instalación      ║"
echo "╚═══════════════════════════════════════╝"
echo -e "${NC}"

# Verificar si Python está instalado
log_info "Verificando instalación de Python..."
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        log_error "Python no está instalado. Por favor instala Python 3.7+ antes de continuar."
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

# Verificar si la versión es compatible (3.7+)
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 7 ]); then
    log_error "Se requiere Python 3.7 o superior. Versión actual: $PYTHON_VERSION"
    exit 1
fi

# Verificar pip
log_info "Verificando pip..."
if ! $PYTHON_CMD -m pip --version &> /dev/null; then
    log_error "pip no está disponible. Por favor instala pip antes de continuar."
    exit 1
fi
log_success "pip encontrado"

# Crear entorno virtual si no existe
VENV_DIR="anime-downloader-env"

if [ ! -d "$VENV_DIR" ]; then
    log_info "Creando entorno virtual..."
    $PYTHON_CMD -m venv $VENV_DIR
    log_success "Entorno virtual creado: $VENV_DIR"
else
    log_warning "El entorno virtual ya existe: $VENV_DIR"
fi

# Activar entorno virtual
log_info "Activando entorno virtual..."
source $VENV_DIR/bin/activate

# Actualizar pip en el entorno virtual
log_info "Actualizando pip..."
python -m pip install --upgrade pip

# Instalar dependencias
log_info "Instalando dependencias desde requirements.txt..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    log_success "Dependencias instaladas correctamente"
else
    log_warning "requirements.txt no encontrado. Instalando dependencias básicas..."
    pip install yt-dlp requests beautifulsoup4 PyYAML tqdm colorama
fi

# Verificar instalación de tkinter (para GUI)
log_info "Verificando tkinter para la interfaz gráfica..."
python -c "import tkinter" 2>/dev/null && log_success "tkinter disponible" || log_warning "tkinter no disponible. La GUI puede no funcionar."

# Crear directorio de descargas por defecto
DEFAULT_DOWNLOAD_DIR="$HOME/Downloads/Anime"
if [ ! -d "$DEFAULT_DOWNLOAD_DIR" ]; then
    log_info "Creando directorio de descargas: $DEFAULT_DOWNLOAD_DIR"
    mkdir -p "$DEFAULT_DOWNLOAD_DIR"
fi

# Verificar que los archivos principales existen
log_info "Verificando archivos del proyecto..."
REQUIRED_FILES=("main.py" "downloader.py" "utils.py" "config.py" "gui.py")

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        log_success "$file ✓"
    else
        log_error "$file no encontrado"
        exit 1
    fi
done

# Hacer ejecutables los scripts Python
chmod +x main.py 2>/dev/null || true

# Probar instalación básica
log_info "Probando instalación..."
python -c "
try:
    import downloader
    import utils
    import config
    print('✓ Módulos principales importados correctamente')
except ImportError as e:
    print(f'✗ Error importando módulos: {e}')
    exit(1)
"

# Crear script de activación
log_info "Creando script de activación..."
cat > activate_anime_downloader.sh << 'EOF'
#!/bin/bash
# Script para activar el entorno del Anime Downloader
source anime-downloader-env/bin/activate
echo "🎌 Entorno Anime Downloader activado"
echo "Uso:"
echo "  python main.py --help          # Ver opciones de línea de comandos"
echo "  python main.py --gui           # Abrir interfaz gráfica"
echo "  python main.py -u URL          # Descargar desde URL"
echo ""
echo "Para desactivar: deactivate"
EOF

chmod +x activate_anime_downloader.sh

# Crear script de inicio rápido para GUI
log_info "Creando script de inicio rápido..."
cat > start_gui.sh << EOF
#!/bin/bash
source anime-downloader-env/bin/activate
$PYTHON_CMD main.py --gui
EOF

chmod +x start_gui.sh

# Crear script de inicio rápido para CLI
cat > start_cli.sh << 'EOF'
#!/bin/bash
source anime-downloader-env/bin/activate
python main.py "$@"
EOF

chmod +x start_cli.sh

# Información final
echo ""
log_success "¡Instalación completada exitosamente!"
echo ""
echo -e "${BLUE}┌─ Cómo usar Anime Downloader ─┐${NC}"
echo ""
echo -e "${GREEN}Opción 1 - Interfaz Gráfica:${NC}"
echo "  ./start_gui.sh"
echo ""
echo -e "${GREEN}Opción 2 - Línea de Comandos:${NC}"
echo "  ./start_cli.sh --help                    # Ver ayuda"
echo "  ./start_cli.sh -u 'URL' -q 720p          # Descargar video"
echo ""
echo -e "${GREEN}Opción 3 - Activar entorno manualmente:${NC}"
echo "  source activate_anime_downloader.sh"
echo "  python main.py --gui"
echo ""
echo -e "${YELLOW}Nota:${NC} Los videos se descargarán en: $DEFAULT_DOWNLOAD_DIR"
echo ""

# Opcional: Probar descarga de prueba
read -p "¿Deseas probar la instalación con la interfaz gráfica? (y/n): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    log_info "Iniciando interfaz gráfica de prueba..."
    python main.py --gui &
fi

log_success "Setup completado. ¡Disfruta descargando anime!"