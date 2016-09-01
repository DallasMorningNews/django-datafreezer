# Imports from python.  # NOQA
from __future__ import unicode_literals
import os


# Imports from django.
from django.apps import AppConfig
from django.conf import settings


# Imports from other dependencies.
import requests


def load_json_endpoint(data_url):
    return requests.get(data_url).json()


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# We can scrape any site that is optimized for social media (graph tags/og)
HUBS_LIST = load_json_endpoint(
    getattr(settings, 'HUBS_LIST_URL', '/api/hub/')
)
STAFF_LIST = load_json_endpoint(
    getattr(settings, 'STAFF_LIST_URL', '/api/staff/')
)


class DatafreezerConfig(AppConfig):
    name = 'datafreezer'
    verbose_name = 'Datafreezer'

    def ready(self):
        from datafreezer import signals  # NOQA
