# Imports from python.  # NOQA
import itertools
# import os
import string


# Imports from django.
from django.db import models
from django.utils import timezone
# from django.utils.text import slugify


# Imports from datafreezer.
# from datafreezer.apps import BASE_DIR


def create_col_nums():
    """Return column numbers and letters that repeat up to NUM_REPEATS.

    I.e., NUM_REPEATS = 2 would return a list of 26 * 26 = 676 2-tuples.

    """
    NUM_REPEATS = 2
    column_letters = list(
        string.ascii_uppercase
    ) + map(
        ''.join,
        itertools.product(
            string.ascii_uppercase,
            repeat=NUM_REPEATS
        )
    )
    letter_numbers = []

    count = 1
    for letter in column_letters:
        letter_numbers.append((count, str(count) + ' (' + letter + ')'))
        count += 1

    return tuple(letter_numbers)


class Tag(models.Model):
    """Tag model.

    Tag is a child of a many-to-many relationship with Dataset.

    word: Verbose word of the tag
    slug: Slugified word for querying and URL construction
    """
    word = models.CharField(max_length=50, unique=True)
    # Slug generation upon saving
    slug = models.SlugField(max_length=100, unique=True)

    def __unicode__(self):
        return self.word


class Article(models.Model):
    """Article model.

    The Article model holds info regarding how Datasets are used outside
    of this application.

    url: The URL at which the Dataset has been used.
    _title: Scraped headline title.
    image_url: URL for used image. Scraping not yet implemented.

    """
    url = models.URLField(max_length=500)
    # Serif API:
    _title = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        db_column='title'
    )
    image_url = models.URLField(blank=True, null=True)

    def __unicode__(self):
        if self.title:
            return self.title
        else:
            return self.url

    @property
    def title(self):
        """Getter function for self.title.

        If no title was stored, use URL.
        """
        if not self._title:
            return 'Dataset sourced in {}'.format(self.url)
        else:
            return self._title

    @title.setter
    def title(self, value):
        """Setter function for self.title.

        """
        self._title = value


class DataDictionary(models.Model):
    """Data Dictionary model.

    Contains basic information about a Dataset and foreign
    keys to DataDictionaryFields, which describe columns.

    last_updated: Indicates when this data dictionary was last updated.
    author: Uploader's email.
    notes: Any additional notes regarding a Dataset.
    attachments: User can upload a DataDictionary of their own. (TK)

    """
    last_updated = models.DateTimeField(default=timezone.now)
    # title = models.CharField(max_length=100, default=Dataset.title)
    author = models.EmailField(max_length=100)
    notes = models.TextField(blank=True, null=True)

    # No need for fields if we have an actual data dictionary document
    attachments = models.FileField(blank=True, null=True)

    def __unicode__(self):
        return '{}\'s dictionary'.format(self.author)

    class Meta:  # NOQA
        verbose_name_plural = 'data dictionaries'


class DataDictionaryField(models.Model):
    """Data Dictionary Field model.

    Contains information about a specific Data Dictionary field.

    columnIndex: the index at which this column can be found in the
                 original Dataset file.
    heading: name of this field.
    description: a description of this field.
    dataType: the type of data which is stored in this field.

    """
    COLUMN_INDEX_CHOICES = create_col_nums()

    INTEGER = 'INTEGER'
    FLOAT = 'FLOAT'
    TEXT = 'TEXT'
    LONGTEXT = 'LONGTEXT'
    # Date no time
    DATE = 'DATE'
    # Time no date
    TIME = 'TIME'
    # Date and time
    DATETIME = 'DATETIME'

    DATATYPE_CHOICES = (
        (INTEGER, 'Integer'),
        (FLOAT, 'Decimal'),
        (TEXT, 'Text'),
        (LONGTEXT, 'Longtext'),
        (DATE, 'Date'),
        (TIME, 'Time'),
        (DATETIME, 'Datetime'),
    )

    # TODO(ajv): Change this field name to 'column_index'.
    columnIndex = models.IntegerField(
        choices=COLUMN_INDEX_CHOICES,
        default=COLUMN_INDEX_CHOICES[0][0]
    )

    heading = models.CharField(max_length=50)
    description = models.TextField()

    # TODO(ajv): Change this field name to 'data_type'.
    dataType = models.CharField(
        max_length=10,
        choices=DATATYPE_CHOICES,
        default=TEXT
    )

    # Relations
    parent_dict = models.ForeignKey(DataDictionary, null=True)

    class Meta:  # NOQA
        verbose_name = 'data dictionary field'
        verbose_name_plural = 'data dictionary fields'


class Dataset(models.Model):
    """Dataset model.

    The Dataset model defines the properties of a Dataset, including
    most metadata about the entire data.

    title: Title of dataset.
    slug: Slugified title.
    date_uploaded: when this Dataset was originally uploaded.
    description: For what purpose was this data used?
    uploaded_by: Email address of the user who uploaded this Dataset.
    source: From where are these data?
    source_slug: Slugified source.

    Optional parameters:
    date_begin: On what date do these data begin?
    date_end: On what date do these data end?
    attachments: Additional files that go with the Dataset (not a codebook)(TK)
    Attachments are not currently included on the forms.

    """
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
