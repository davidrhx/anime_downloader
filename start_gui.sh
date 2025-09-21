#!/bin/bash
# start_gui.sh - Inicio rápido para la interfaz gráfica

if [ -d "anime-downloader-env" ]; then
    source anime-downloader-env/bin/activate
    echo "🎌 Iniciando Anime Downloader GUI..."
    python main.py --gui
else
    echo "❌ Entorno virtual no encontrado."
    echo "Ejecuta primero: ./install.sh"
fi


