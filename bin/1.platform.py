import re

def identify_platform(url):
    patterns = {
        'YouTube': r'(https?://(?:www\.)?youtube\.com|youtu\.be)',
        'Vimeo': r'vimeo\.com',
        'Dailymotion': r'dailymotion\.com',
        'Twitch': r'twitch\.tv',
        'Facebook': r'facebook\.com',
        'Instagram': r'instagram\.com',
        'TikTok': r'tiktok\.com',
        'Twitter': r'(https?://(?:www\.)?twitter\.com|x\.com)'
    }

    for platform, pattern in patterns.items():
        if re.search(pattern, url, re.IGNORECASE):
            return platform
    return 'Unknown'

# Example usage:
test_urls = [
    'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
    'https://vimeo.com/12345678',
    'https://www.tiktok.com/@user/video/123456789',
    'https://x.com/user/status/1234567890'
]

for url in test_urls:
    print(f'{url} -> {identify_platform(url)}')

