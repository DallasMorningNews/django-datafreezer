# Imports from django.  # NOQA
from django.conf import settings
from django.core.files.storage import get_storage_class


if hasattr(settings, 'DATAFREEZER_CUSTOM_STORAGE_CLASS'):
    DATAFREEZER_STORAGE = settings.DATAFREEZER_CUSTOM_STORAGE_CLASS
else:
    DATAFREEZER_STORAGE = get_storage_class(
        getattr(
            settings,
            'DEFAULT_FILE_STORAGE',
            'django.core.files.storage.FileSystemStorage',
        )
    )
