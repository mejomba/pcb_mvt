import os
from django.conf import settings
from django.core.files.storage import FileSystemStorage

_instance = None


def protected_media_storage():
    """استوریج فایل‌ساز که فایل‌ها را خارج از MEDIA عمومی نگه می‌دارد."""
    global _instance
    if _instance is None:
        location = getattr(settings, 'PROTECTED_MEDIA_ROOT', None) \
            or os.path.join(settings.BASE_DIR, 'protected_media')
        _instance = FileSystemStorage(location=str(location))
    return _instance
