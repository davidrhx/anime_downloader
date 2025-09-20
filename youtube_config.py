# youtube_config.py - Configuración específica para YouTube
YOUTUBE_SAFE_CONFIG = {
    'format': 'best[height<=720][ext=mp4]',
    'writesubtitles': False,
    'writeautomaticsub': False,
    'writethumbnail': False,
    'embed_subs': False,
    'ignoreerrors': True,
    'sleep_interval': 2,
    'max_sleep_interval': 5,
}
