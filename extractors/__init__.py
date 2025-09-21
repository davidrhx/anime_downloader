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
