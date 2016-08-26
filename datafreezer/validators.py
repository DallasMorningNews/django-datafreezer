# Imports from python.  # NOQA
import csv


# Imports from django.
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django import forms


def validate_dataset_file(value):
    if not value.name.endswith('.csv'):
        raise ValidationError(u'Please upload a CSV (comma separated values)\
            file.')
    # idk make this better
    try:
        # file_sample = value.file.open(1024)
        csvreader = csv.reader(value.file)
        for row in csvreader:
            if csvreader.line_num >= 25:
                break
            row
        # do sth lol
    except csv.Error:
        raise ValidationError('Failed to parse CSV file.')


class MultiURLField(forms.Field):
    # def to_python(self, value):
    #     # urls = value.all()
    #     # print urls
    #     return value
    #     # return urls
    def prepare_value(self, value):
        if value:
            urls = [item.url for item in value]
            return ', '.join(urls) + ', '
        return ''

    def validate(self, value):
        # Use parents' handling of required fields, etc.
        super(MultiURLField, self).validate(value)
        for url in value:
            URLValidator(url)


class MultiTagField(forms.CharField):
    def prepare_value(self, value):
        if value:
            tags = [item.word for item in value]
            return ', '.join(tags) + ', '
        return ''
