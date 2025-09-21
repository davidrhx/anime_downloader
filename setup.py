#!/usr/bin/env python3
"""
Setup script para Anime Downloader
Permite instalación con pip install .
"""

from setuptools import setup, find_packages
from pathlib import Path

# Leer README para descripción larga
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

# Leer requirements
requirements = []
try:
    with open('requirements.txt', 'r') as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        # Filtrar comentarios y líneas vacías
        requirements = [req for req in requirements if not req.startswith('#') and req.strip()]
except FileNotFoundError:
    # Requirements básicos si no existe el archivo
    requirements = [
        'yt-dlp>=2023.7.6',
        'requests>=2.31.0',
        'beautifulsoup4>=4.12.2',
        'lxml>=4.9.3',
        'tqdm>=4.65.0',
        'colorama>=0.4.6',
    ]

setup(
    name="anime-downloader",
    version="1.0.0",
    author="Tu Nombre",  # Cambia esto
    author_email="tu.email@ejemplo.com",  # Cambia esto
    description="Un downloader de anime simple y eficiente con interfaz gráfica y soporte para múltiples sitios",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/TU_USUARIO/anime-downloader",  # Cambia esto
    packages=find_packages(),
    py_modules=[
        'main',
        'downloader', 
        'gui',
        'config',
        'utils',
        'batch_download',
        'downloader_extended',
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Multimedia :: Video",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Environment :: Console",
        "Environment :: X11 Applications",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    extras_require={
        'dev': [
            'pytest>=7.4.0',
            'black>=23.7.0',
            'flake8>=6.0.0',
        ],
        'gui': [],  # Tkinter viene incluido
        'full': [
            'pillow>=10.0.0',
            'ffmpeg-python>=0.2.0',
        ],
    },
    entry_points={
        'console_scripts': [
            'anime-downloader=main:main',
            'anime-dl=main:main',
        ],
    },
    include_package_data=True,
    package_data={
        '': ['*.txt', '*.md', '*.yml', '*.yaml'],
    },
    project_urls={
        "Bug Reports": "https://github.com/TU_USUARIO/anime-downloader/issues",
        "Source": "https://github.com/TU_USUARIO/anime-downloader",
        "Documentation": "https://github.com/TU_USUARIO/anime-downloader/wiki",
    },
    keywords="anime, downloader, youtube, jkanime, video, download, gui, batch",
    zip_safe=False,
)
