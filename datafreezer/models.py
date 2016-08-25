from django.db import models
from django.utils.text import slugify
from django.utils import timezone
import os

from apps import BASE_DIR
from core.settings import MEDIA_ROOT

import string
import itertools


def create_col_nums():
	colLetters = list(string.ascii_uppercase) + map(''.join, itertools.product(string.ascii_uppercase, repeat=2))
	letterNums = []
	count = 1
	for letter in colLetters:
		letterNums.append((count, str(count) + " (" + letter + ")"))
		count += 1

	return tuple(letterNums)


class Tag(models.Model):
	word = models.CharField(max_length=50, unique=True)
	# Slug generation upon saving
	slug = models.SlugField(max_length=100, unique=True)

	def __unicode__(self):
		return self.word


class Article(models.Model):
	url = models.URLField(max_length=500)
	# Serif API:
	_title = models.CharField(max_length=500, blank=True, null=True, db_column="title")
	image_url = models.URLField(blank=True, null=True)

	def __unicode__(self):
		if self.title:
			return self.title
		else:
			return self.url

	@property
	def title(self):
		if not self._title:
			return "Dataset sourced in %s" %(self.url)
		else:
			return self._title

	@title.setter
	def title(self, value):
		self._title = value


class DataDictionary(models.Model):
	last_updated = models.DateTimeField(default=timezone.now)
	# title = models.CharField(max_length=100, default=Dataset.title)
	author = models.EmailField(max_length=100)
	notes = models.TextField(blank=True, null=True)

	# No need for fields if we have an actual data dictionary document
	attachments = models.FileField(blank=True, null=True)

	def __unicode__(self):
		return "%s's dictionary" %(self.author)

	class Meta:
		verbose_name_plural = 'data dictionaries'


class DataDictionaryField(models.Model):
	COLUMN_INDEX_CHOICES = create_col_nums()

	columnIndex = models.IntegerField(choices=COLUMN_INDEX_CHOICES,
									default=COLUMN_INDEX_CHOICES[0][0])


	heading = models.CharField(max_length=50)
	description = models.TextField()

	NUMBER = 'NUMBER'
	TEXT = 'TEXT'
	LONGTEXT = 'LONGTEXT'
	# Date no time
	DATE = 'DATE'
	# Time no date
	TIME = 'TIME'
	# Date and time
	DATETIME = 'DATETIME'

	DATATYPE_CHOICES = (
		(NUMBER, 'Number'),
		(TEXT, 'Text'),
		(LONGTEXT, 'Longtext'),
		(DATE, 'Date'),
		(TIME, 'Time'),
		(DATETIME, 'Datetime'),
	)


	dataType = models.CharField(max_length=10,
								choices=DATATYPE_CHOICES,
								default=TEXT)

	# Relations
	parent_dict = models.ForeignKey(DataDictionary, null=True)

	class Meta:
		verbose_name = 'data dictionary field'
		verbose_name_plural = 'data dictionary fields'


class Dataset(models.Model):
	title = models.CharField(max_length=200)
	slug = models.SlugField(max_length=250, blank=True)
	date_uploaded = models.DateTimeField(default=timezone.now, blank=True)
	description = models.TextField()
	uploaded_by = models.EmailField()
	source = models.CharField(max_length=200)
	source_slug = models.CharField(max_length=250, blank=True)

	# Date that Dataset begins
	date_begin = models.DateTimeField(blank=True, null=True)
	# Date that Dataset ends
	date_end = models.DateTimeField(blank=True, null=True)

	# Need to populate w/ choices from Staff API on view.
	# Save selection as CharField.
	vertical_slug = models.CharField(max_length=25)
	hub_slug = models.CharField(max_length=25)

	# Relationships:
	tags = models.ManyToManyField(Tag)
	appears_in = models.ManyToManyField(Article, blank=True)
	data_dictionary = models.OneToOneField(DataDictionary, null=True)
	dataset_file = models.FileField(max_length=500, upload_to='%Y/%m/%d/')

	# zip it up
	attachments = models.FileField(blank=True, null=True)

	# could_parse = models.NullBooleanField(blank=True, null=True)
	has_headers = models.BooleanField()

	# Source information:
	# Need to have a think about what we need to require during form validation
	# rolodex_person_id = models.PositiveSmallIntegerField(null=True)
	# rolodex_contact_id = models.PositiveSmallIntegerField(null=True)
	# rolodex_organization_id = models.PositiveSmallIntegerField(null=True)

	def __unicode__(self):
		return self.title
