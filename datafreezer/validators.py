from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator

import csv


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
    def to_python(self, value):
        return value.split(',')

    def validate(self, value):
        # Use parents' handling of required fields, etc.
        super(MultiURLField, self).validate(value)
        for url in value:
            URLValidator(url)
