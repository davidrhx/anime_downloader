#!/bin/bash
# start_cli.sh - Inicio rápido para línea de comandos

if [ -d "anime-downloader-env" ]; then
    source anime-downloader-env/bin/activate
    
    if [ $# -eq 0 ]; then
        echo "🎌 Anime Downloader - Línea de Comandos"
        echo ""
        echo "Uso: ./start_cli.sh [opciones]"
        echo ""
        echo "Ejemplos:"
        echo "  ./start_cli.sh -u \"https://youtube.com/watch?v=ID\" -q 720p"
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
fi
