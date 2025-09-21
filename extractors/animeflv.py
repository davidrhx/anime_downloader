#!/bin/bash
# Script completo para configurar AnimeFLV

echo "🎌 Configurando extractor de AnimeFLV..."

# 1. Crear extractors/animeflv.py
echo "📝 Creando extractor de AnimeFLV..."
# (Copia el contenido del artifact animeflv_extractor aquí)

# 2. Actualizar __init__.py
echo "🔄 Actualizando extractors/__init__.py..."
cat > extractors/__init__.py << 'EOF'
"""
Extractors package - Extractores personalizados para sitios de anime
"""

__version__ = '1.0.0'
__all__ = ['jkanime', 'animeflv']

EXTRACTORS_AVAILABLE = []

try:
    from .jkanime import JKAnimeExtractor
    EXTRACTORS_AVAILABLE.append('jkanime')
    print("✅ JKAnime extractor loaded")
except ImportError as e:
    print(f"Warning: JKAnime extractor not available: {e}")

try:
    from .animeflv import AnimeFLVExtractor  
    EXTRACTORS_AVAILABLE.append('animeflv')
    print("✅ AnimeFLV extractor loaded")
except ImportError as e:
    print(f"Warning: AnimeFLV extractor not available: {e}")

print(f"📋 Total extractors available: {len(EXTRACTORS_AVAILABLE)}")
EOF

# 3. Script de prueba
echo "🧪 Creando script de prueba..."
cat > test_animeflv.py << 'EOF'
#!/usr/bin/env python3
"""Test completo de AnimeFLV"""

print("🔍 DIAGNÓSTICO ANIMEFLV")
print("=" * 50)

# Test importación directa
print("1️⃣ Probando importación directa:")
try:
    from extractors.animeflv import AnimeFLVExtractor
    print("✅ AnimeFLVExtractor importado")
    
    extractor = AnimeFLVExtractor()
    print("✅ Instancia creada")
    
    # Probar URLs
    test_urls = [
        "https://animeflv.net/ver/one-piece-1",
        "https://animeflv.net/ver/naruto-1", 
        "https://animeflv.net/anime/one-piece"
    ]
    
    for url in test_urls:
        can_handle = extractor.can_handle(url)
        print(f"   {url}: {can_handle}")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

# Test downloader extendido  
print("\n2️⃣ Probando downloader extendido:")
try:
    from downloader_extended import ExtendedAnimeDownloader
    downloader = ExtendedAnimeDownloader()
    
    extractors = list(downloader.custom_extractors.keys())
    print(f"✅ Extractores: {extractors}")
    
    if 'animeflv' in extractors:
        test_url = "https://animeflv.net/ver/one-piece-1"
        result = downloader.can_handle_url(test_url)
        print(f"✅ Puede manejar AnimeFLV: {result}")
    else:
        print("❌ AnimeFLV no registrado")
        
except Exception as e:
    print(f"❌ Error: {e}")

print("=" * 50)
print("🏁 Test completado")
EOF

chmod +x test_animeflv.py

echo "✅ Configuración de AnimeFLV completada"
echo ""
echo "🧪 Para probar:"
echo "   python test_animeflv.py"
echo ""
echo "🎯 URLs de ejemplo:"
echo "   python main.py -u \"https://animeflv.net/ver/one-piece-1\" --info"
echo "   python main.py -u \"https://animeflv.net/ver/naruto-1\" --info"
