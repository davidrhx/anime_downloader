cat > extractors/__init__.py << 'EOF'
"""
Extractors package - Extractores personalizados para sitios de anime
"""

__version__ = '1.0.0'
__all__ = ['jkanime', 'animeflv']

# Importar extractores disponibles
EXTRACTORS_AVAILABLE = []

try:
    from .jkanime import JKAnimeExtractor
    EXTRACTORS_AVAILABLE.append('jkanime')
except ImportError as e:
    print(f"Warning: Could not import JKAnime extractor: {e}")

try:
    from .animeflv import AnimeFLVExtractor
    EXTRACTORS_AVAILABLE.append('animeflv')
    print("✅ AnimeFLV extractor loaded")
except ImportError as e:
    print(f"Warning: Could not import AnimeFLV extractor: {e}")

print(f"📋 Extractors available: {EXTRACTORS_AVAILABLE}")
EOF
