# 🎌 Anime Downloader

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub stars](https://img.shields.io/github/stars/TU_USUARIO/anime-downloader.svg)](https://github.com/TU_USUARIO/anime-downloader/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/TU_USUARIO/anime-downloader.svg)](https://github.com/TU_USUARIO/anime-downloader/network)
[![GitHub issues](https://img.shields.io/github/issues/TU_USUARIO/anime-downloader.svg)](https://github.com/TU_USUARIO/anime-downloader/issues)

Un downloader de anime simple, eficiente y fácil de usar con interfaz gráfica y soporte para múltiples sitios incluyendo JKAnime.

![Demo](https://via.placeholder.com/800x400/1a1a1a/ffffff?text=Anime+Downloader+Demo)

## ✨ Características Principales

- 🎥 **Múltiples calidades**: 480p, 720p, 1080p y la mejor disponible
- 🖥️ **Doble interfaz**: GUI intuitiva + línea de comandos potente
- 🎌 **Soporte JKAnime**: Extractor personalizado para jkanime.net
- ⚡ **1000+ sitios**: Soporte completo via yt-dlp (YouTube, Vimeo, etc.)
- 📱 **Subtítulos automáticos**: Descarga e incrusta subtítulos
- 🔄 **Reintentos inteligentes**: Manejo robusto de errores y rate limiting
- 📊 **Progreso en tiempo real**: Visualización del progreso de descarga
- 📁 **Organización automática**: Estructura de carpetas inteligente
- 🚀 **Descargas por lotes**: Múltiples episodios simultáneamente
- 🛡️ **Modo seguro**: Evita bloqueos con rate limiting inteligente

## 🚀 Instalación Rápida

### Opción 1: Script Automático (Recomendado)

```bash
[git clone https://github.com/davidrhx/anime_downloader]
cd anime_downloader
chmod +x install.sh
./install.sh
```

### Opción 3: Con pip (Próximamente)

```bash
pip install git+https://github.com/davidrhx/anime_downloader
```

## 🎮 Ejemplos de Uso

### 🖥️ Interfaz Gráfica (Principiantes)

La forma más fácil de usar el downloader:

```bash
# Método 1: Script directo
./start_gui.sh

# Método 2: Manual
source anime-downloader-env/bin/activate
python main.py --gui
```

**Características de la GUI:**
- Entrada de URL con validación
- Selector de calidad visual
- Información del video antes de descargar
- Progreso en tiempo real con barra visual
- Log de actividad integrado
- Modo seguro con un click

### ⌨️ Línea de Comandos (Avanzados)

```bash
# YouTube
./start_cli.sh -u "https://youtube.com/watch?v=dQw4w9WgXcQ" -q 720p

# JKAnime (Dandadan ejemplo)
./start_cli.sh -u "https://jkanime.net/dandadan-2nd-season/12/" -q 720p

# Solo obtener información (sin descargar)
./start_cli.sh -u "https://jkanime.net/dandadan-2nd-season/12/" --info

# Ver todos los sitios soportados
./start_cli.sh --list-sites

# Modo verbose (información detallada)
./start_cli.sh -u "URL" -q 1080p --verbose

# Especificar carpeta de destino
./start_cli.sh -u "URL" -o "~/Anime/MiSerie" -q 720p
```

### 📦 Descargas por Lotes

Para descargar múltiples episodios automáticamente:

```bash
# 1. Crear lista de URLs
cat > episodios.txt << EOF
https://jkanime.net/dandadan-2nd-season/1/
https://jkanime.net/dandadan-2nd-season/2/
https://jkanime.net/dandadan-2nd-season/3/
https://youtube.com/watch?v=VIDEO_ID_1
https://youtube.com/watch?v=VIDEO_ID_2
EOF

# 2. Descargar toda la lista
python batch_download.py -f episodios.txt -q 720p -w 2

# 3. Crear archivo de ejemplo
python batch_download.py --create-sample
```

## 🌐 Sitios Web Soportados

### 🎌 Sitios de Anime Específicos

| Sitio | URL Ejemplo | Estado |
|-------|-------------|--------|
| **JKAnime** | `https://jkanime.net/dandadan-2nd-season/12/` | ✅ Funcionando |
| AnimeFLV | `https://animeflv.net/...` | 🔄 En desarrollo |
| MonosChinos | `https://monoschinos2.com/...` | 🔄 Planeado |

### 📺 Sitios Estándar (1000+ via yt-dlp)

| Categoría | Sitios Soportados |
|-----------|-------------------|
| **Video** | YouTube, Vimeo, Dailymotion, Twitch |
| **Social** | Facebook, Twitter, Instagram, TikTok |
| **Streaming** | Crunchyroll (parcial), Funimation (parcial) |
| **Otros** | Bilibili, Niconico, y muchos más |

Ver lista completa: `python main.py --list-sites`

## 📋 Requisitos del Sistema

### Mínimos
- **Python**: 3.7 o superior
- **OS**: Windows 7+, macOS 10.12+, Linux (cualquier distro moderna)
- **RAM**: 512 MB disponibles
- **Espacio**: 100 MB para la aplicación + espacio para descargas

### Recomendados
- **Python**: 3.9+
- **RAM**: 2 GB disponibles
- **Conexión**: Banda ancha para descargas rápidas
- **Espacio**: 10+ GB para almacenar episodios

## ⚙️ Configuración Avanzada

### Variables de Entorno

```bash
# Configurar calidad por defecto
export ANIME_QUALITY=1080p

# Cambiar directorio de descarga
export ANIME_DOWNLOAD_PATH="$HOME/MisAnimes"

# Aumentar reintentos para conexiones lentas
export ANIME_MAX_RETRIES=5

# Activar subtítulos (puede causar rate limiting)
export ANIME_SUBTITLES=true

# Modo conservativo
export ANIME_RATE_LIMIT=true
export ANIME_MAX_RATE=1M
```

### Archivo de Configuración

Edita `config.py` para personalización avanzada:

```python
# Configuración personalizada
DEFAULT_QUALITY = '720p'
DOWNLOAD_PATH = '/home/user/Anime'
MAX_RETRIES = 5
CONCURRENT_DOWNLOADS = 2

# Activar modo seguro para JKAnime
USE_RATE_LIMITING = True
DOWNLOAD_SUBTITLES = False  # Evita errores 429
```

## 🔧 Solución de Problemas

### Errores Comunes

| Error | Solución |
|-------|----------|
| `ModuleNotFoundError: No module named 'yt_dlp'` | `pip install -r requirements.txt` |
| `tkinter module not found` | `sudo apt-get install python3-tk` (Ubuntu) |
| `Error 429: Too Many Requests` | Usar modo seguro: `python main.py --gui` → "Modo Seguro" |
| `Permission denied` | `chmod +x *.sh` |

### Logs y Debugging

```bash
# Modo verbose para ver detalles
python main.py -u "URL" --verbose

# Ver logs en tiempo real
tail -f logs/anime-downloader.log

# Verificar instalación
python main.py --version
python test_jkanime.py  # Solo si instalaste JKAnime
```

### Actualizar yt-dlp

```bash
# Recomendado mensualmente
pip install --upgrade yt-dlp
```

## 📁 Estructura del Proyecto

```
anime-downloader/
├── 📄 Archivos principales
│   ├── main.py              # Aplicación principal CLI
│   ├── gui.py               # Interfaz gráfica
│   ├── downloader.py        # Lógica de descarga estándar
│   ├── downloader_extended.py # Downloader con extractores personalizados
│   └── config.py            # Configuración
├── 🛠️ Utilidades
│   ├── utils.py             # Funciones auxiliares
│   ├── batch_download.py    # Descargas masivas
│   └── extractors/          # Extractores personalizados
│       ├── __init__.py
│       └── jkanime.py       # Extractor JKAnime
├── 🚀 Scripts de instalación
│   ├── install.sh           # Instalación automática
│   ├── install_jkanime.sh   # Instalación JKAnime
│   ├── start_gui.sh         # Inicio rápido GUI
│   └── start_cli.sh         # Inicio rápido CLI
└── 📚 Documentación
    ├── README.md            # Este archivo
    ├── LICENSE              # Licencia MIT
    ├── requirements.txt     # Dependencias
    └── setup.py             # Instalación con pip
```

## 🤝 Contribuir

¡Las contribuciones son bienvenidas! Aquí te explico cómo:

### Desarrollo Local

```bash
# 1. Fork el repositorio en GitHub

# 2. Clonar tu fork
git clone https://github.com/TU_USUARIO/anime-downloader.git
cd anime-downloader

# 3. Configurar entorno de desarrollo
python -m venv dev-env
source dev-env/bin/activate
pip install -r requirements.txt
pip install pytest black flake8  # Herramientas de desarrollo

# 4. Crear rama para tu feature
git checkout -b feature/nueva-caracteristica

# 5. Hacer cambios y probar
python -m pytest tests/  # Ejecutar tests
black *.py               # Formatear código
flake8 *.py             # Linting

# 6. Commit y push
git commit -am 'Agrega nueva característica increíble'
git push origin feature/nueva-caracteristica

# 7. Crear Pull Request en GitHub
```

### Ideas para Contribuir

- 🌐 **Nuevos extractores**: AnimeFLV, MonosChinos, Crunchyroll
- 🎨 **Mejoras UI**: Temas, modo oscuro, mejor UX
- 🔧 **Características**: Notificaciones, scheduling, API REST
- 🐛 **Bug fixes**: Reporta y arregla issues
- 📖 **Documentación**: Traducciones, tutoriales, wikis

## 📊 Roadmap

### v1.1.0 (Próxima versión)
- [ ] Soporte para AnimeFLV
- [ ] Modo oscuro en GUI
- [ ] Notificaciones de escritorio
- [ ] Programación de descargas

### v1.2.0 (Futuro)
- [ ] API REST
- [ ] Plugin system
- [ ] Sincronización con MAL/AniList
- [ ] Interfaz web opcional

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver [LICENSE](LICENSE) para más detalles.

### Términos Importantes
- ✅ **Uso comercial** permitido
- ✅ **Modificación** permitida  
- ✅ **Distribución** permitida
- ✅ **Uso privado** permitido
- ❌ **Sin garantía** - Úsalo bajo tu propio riesgo

## ⚖️ Descargo de Responsabilidad

**⚠️ IMPORTANTE:** Este software es únicamente para fines **educativos y de uso personal**.

### Responsabilidades del Usuario
- 📚 **Educativo**: Úsalo para aprender sobre descargas y Python
- 👤 **Personal**: Solo para contenido que tengas derecho a descargar
- ⚖️ **Legal**: Cumple las leyes de copyright de tu país
- 📝 **TOS**: Respeta los términos de servicio de los sitios web
- 🚫 **No comercial**: No uses para distribución comercial

### Limitaciones Legales
Los desarrolladores **NO** somos responsables de:
- Uso indebido del software
- Violaciones de copyright
- Infracciones de términos de servicio
- Consecuencias legales del uso

**💡 Consejo:** Si tienes dudas sobre la legalidad, consulta con un abogado especializado en copyright.

## 🙏 Agradecimientos

### Tecnologías Utilizadas
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - Motor de descarga principal
- [Python](https://python.org) - Lenguaje de programación
- [Tkinter](https://docs.python.org/3/library/tkinter.html) - Interfaz gráfica
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) - Web scraping
- [Requests](https://requests.readthedocs.io/) - HTTP requests

### Inspiración
- Comunidad de anime y fansubs
- Proyectos open source similares
- Feedback de usuarios y contributors

## 📞 Soporte y Contacto

### 🐛 Reportar Problemas
- **GitHub Issues**: [Crear Issue](https://github.com/TU_USUARIO/anime-downloader/issues/new)
- **Bug Template**: Usa el template automático
- **Incluye**: SO, versión Python, logs de error

### 💡 Solicitar Características  
- **GitHub Issues**: Etiqueta `enhancement`
- **Discussions**: Para ideas y propuestas
- **Pull Requests**: ¡Implementa tu idea!

### 💬 Comunidad
- **GitHub Discussions**: [Unirse](https://github.com/TU_USUARIO/anime-downloader/discussions)
- **Discord**: [Próximamente]
- **Reddit**: r/AnimeDownloader [Próximamente]

### 📧 Contacto Directo
- **Email**: tu.email@ejemplo.com
- **Twitter**: [@TuUsuario](https://twitter.com/TuUsuario)

---

<div align="center">

**¿Te gusta el proyecto?** ⭐ ¡Dale una estrella en GitHub!

**¿Encontraste un bug?** 🐛 [Repórtalo aquí](https://github.com/TU_USUARIO/anime-downloader/issues)

**¿Quieres contribuir?** 🚀 ¡Lee la [guía de contribución](#-contribuir)!

**Hecho con ❤️ por la comunidad de anime**

</div>
