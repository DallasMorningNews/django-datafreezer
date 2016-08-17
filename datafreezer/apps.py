from __future__ import unicode_literals

from django.apps import AppConfig

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class DatafreezerConfig(AppConfig):
	name = 'datafreezer'
	verbose_name = 'Datafreezer'

	def ready(self):
		from datafreezer import signals
