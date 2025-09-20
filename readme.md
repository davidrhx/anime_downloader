# 🎌 Anime Downloader

Un downloader de anime simple, eficiente y fácil de usar con interfaz gráfica y línea de comandos.

## ✨ Características

- 🎥 **Múltiples calidades**: 480p, 720p, 1080p y la mejor disponible
- 🖥️ **Interfaz gráfica**: GUI intuitiva con Tkinter
- ⌨️ **Línea de comandos**: Para usuarios avanzados y automatización
- 📱 **Subtítulos automáticos**: Descarga e incrusta subtítulos
- 🔄 **Reintentos automáticos**: Manejo robusto de errores
- 📊 **Progreso en tiempo real**: Visualización del progreso de descarga
- 📁 **Organización automática**: Estructura de carpetas por anime
- 🚀 **Descargas por lotes**: Múltiples episodios simultáneamente

## 📋 Requisitos

- Python 3.7 o superior
- Sistema operativo: Windows, macOS, Linux
- Conexión a internet
- Espacio en disco suficiente

## 🚀 Instalación Rápida

### Opción 1: Script Automático (Recomendado)

```bash
git clone https://github.com/TU_USUARIO/anime-downloader.git
cd anime-downloader
chmod +x install.sh
./install.sh
```

### Opción 2: Instalación Manual

```bash
# Clonar el repositorio
git clone https://github.com/TU_USUARIO/anime-downloader.git
cd anime-downloader

# Crear entorno virtual
python3 -m venv anime-downloader-env
source anime-downloader-env/bin/activate  # En Linux/macOS
# o en Windows: anime-downloader-env\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# ¡Listo para usar!
python main.py --help
```

## 🎮 Uso

### Interfaz Gráfica (GUI)

La forma más fácil de usar el downloader:

```bash
# Si usaste el script de instalación
./start_gui.sh

# O manualmente
python main.py --gui
```

**Características de la GUI:**
- Ingresa la URL del episodio
- Selecciona la calidad deseada
- Elige la carpeta de destino
- Obtén información del video antes de descargar
- Monitorea el progreso en tiempo real
- Log de actividad integrado

### Línea de Comandos (CLI)

Para usuarios avanzados y automatización:

```bash
# Ayuda
python main.py --help

# Descarga básica
python main.py -u "https://ejemplo.com/anime/episodio-1"

# Especificar calidad y destino
python main.py -u "URL" -q 1080p -o "~/Anime/MiSerie"

# Modo verbose
python main.py -u "URL" -q 720p --verbose
```

#### Opciones disponibles:

| Opción | Descripción | Ejemplo |
|--------|-------------|---------|
| `-u, --url` | URL del episodio | `-u "https://..."` |
| `-q, --quality` | Calidad (480p/720p/1080p/best) | `-q 720p` |
| `-o, --output` | Directorio de descarga | `-o "~/Anime"` |
| `--gui` | Abrir interfaz gráfica | `--gui` |
| `-v, --verbose` | Información detallada | `--verbose` |
| `--version` | Mostrar versión | `--version` |

### Descargas por Lotes

Para descargar múltiples episodios:

```bash
python batch_download.py -f lista_urls.txt -q 720p
```

Donde `lista_urls.txt` contiene:
```
https://ejemplo.com/anime/episodio-1
https://ejemplo.com/anime/episodio-2
https://ejemplo.com/anime/episodio-3
```

## ⚙️ Configuración

Edita `config.py` para personalizar el comportamiento:

```python
# Configuración básica
DEFAULT_QUALITY = '720p'
DOWNLOAD_PATH = '~/Downloads/Anime'
MAX_RETRIES = 3
CONCURRENT_DOWNLOADS = 2

# Subtítulos
DOWNLOAD_SUBTITLES = True
SUBTITLE_LANGUAGES = ['es', 'en', 'ja']
EMBED_SUBTITLES = True
```

### Variables de Entorno

También puedes usar variables de entorno:

```bash
export ANIME_QUALITY=1080p
export ANIME_DOWNLOAD_PATH="$HOME/Anime"
export ANIME_MAX_RETRIES=5
python main.py -u "URL"
```

## 📁 Estructura del Proyecto

```
anime-downloader/
├── main.py              # Aplicación principal CLI
├── downloader.py        # Lógica de descarga
├── utils.py             # Funciones auxiliares  
├── config.py            # Configuración
├── gui.py               # Interfaz gráfica
├── batch_download.py    # Descargas por lotes
├── requirements.txt     # Dependencias
├── install.sh          # Script de instalación
├── README.md           # Este archivo
├── .gitignore          # Archivos ignorados por git
└── tests/              # Pruebas unitarias
    └── test_utils.py
```

## 🧪 Pruebas

Ejecutar las pruebas unitarias:

```bash
# Activar entorno virtual
source anime-downloader-env/bin/activate

# Ejecutar pruebas
python -m pytest tests/ -v

# Con cobertura
python -m pytest tests/ --cov=. --cov-report=html
```

## 🔧 Solución de Problemas

### Error: "yt-dlp not found"
```bash
pip install --upgrade yt-dlp
```

### Error: "tkinter module not found"
```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# CentOS/RHEL
sudo yum install tkinter

# macOS (con Homebrew)
brew install python-tk
```

### Permisos de escritura
```bash
chmod 755 ~/Downloads/Anime
```

### Videos no se descargan
- Verifica que la URL sea válida
- Algunos sitios requieren configuración especial
- Revisa los logs para más detalles

## 🚫 Limitaciones y Consideraciones

- **Sitios soportados**: Funciona con sitios compatibles con yt-dlp
- **Rate limiting**: Algunos sitios limitan descargas
- **Términos de servicio**: Respeta los TOS de los sitios web
- **Copyright**: Solo descarga contenido que tengas derecho a usar

## 🤝 Contribuir

¡Las contribuciones son bienvenidas!

1. Fork el proyecto
2. Crea una branch (`git checkout -b feature/nueva-caracteristica`)
3. Commit tus cambios (`git commit -am 'Agrega nueva característica'`)
4. Push a la branch (`git push origin feature/nueva-caracteristica`)
5. Abre un Pull Request

### Desarrollo Local

```bash
# Clonar tu fork
git clone https://github.com/TU_USUARIO/anime-downloader.git
cd anime-downloader

# Instalar en modo desarrollo
pip install -e .

# Instalar herramientas de desarrollo
pip install pytest black flake8

# Formatear código
black *.py

# Linting
flake8 *.py
```

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

## ⚖️ Descargo de Responsabilidad

Este software es solo para fines educativos y de uso personal. Los usuarios son responsables de cumplir con las leyes de copyright y los términos de servicio de los sitios web. Los desarrolladores no se hacen responsables del uso indebido del software.

## 📞 Soporte

- 🐛 **Reportar bugs**: [Issues](https://github.com/TU_USUARIO/anime-downloader/issues)
- 💡 **Solicitar características**: [Feature Requests](https://github.com/TU_USUARIO/anime-downloader/issues/new)
- 📖 **Documentación**: [Wiki](https://github.com/TU_USUARIO/anime-downloader/wiki)
- 💬 **Discusiones**: [Discussions](https://github.com/TU_USUARIO/anime-downloader/discussions)

## 🙏 Agradecimientos

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - Motor de descarga
- [Python](https://python.org) - Lenguaje de programación
- [Tkinter](https://docs.python.org/3/library/tkinter.html) - Interfaz gráfica
- Comunidad open source

---

**¿Te gusta el proyecto?** ⭐ ¡Dale una estrella en GitHub!

**¿Encontraste un bug?** 🐛 [Repórtalo aquí](https://github.com/TU_USUARIO/anime-downloader/issues)

**¿Quieres contribuir?** 🚀 ¡Lee la guía de contribución!
