# Imports from python.  # NOQA
import os


# Imports from django.
from django.conf import settings
from django.core.files.storage import get_storage_class


# Imports from django-storages.
from storages.backends.s3boto import S3BotoStorage


class MediaRootS3BotoStorage(S3BotoStorage):
    access_key = getattr(settings, 'DATAFREEZER_AWS_ACCESS_KEY_ID', '')
    secret_key = getattr(settings, 'DATAFREEZER_AWS_SECRET_ACCESS_KEY', '')
    bucket_name = getattr(settings, 'DATAFREEZER_AWS_STORAGE_BUCKET_NAME', '')

    def __init__(self, *args, **kwargs):
        kwargs['location'] = 'media'
        super(MediaRootS3BotoStorage, self).__init__(*args, **kwargs)


if 'DATAFREEZER_AWS_ACCESS_KEY_ID' in os.environ:
    DATAFREEZER_STORAGE = MediaRootS3BotoStorage()
elif hasattr(settings, 'DATAFREEZER_CUSTOM_STORAGE_CLASS'):
    DATAFREEZER_STORAGE = settings.DATAFREEZER_CUSTOM_STORAGE_CLASS
else:
    DATAFREEZER_STORAGE = get_storage_class(
        getattr(
            settings,
            'DEFAULT_FILE_STORAGE',
            'django.core.files.storage.FileSystemStorage',
        )
    )
