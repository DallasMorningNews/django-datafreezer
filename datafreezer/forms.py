from django.forms.widgets import HiddenInput
from django.forms import ModelForm, DateField, DateInput
from django import forms

from models import *
from validators import *

import requests
from datetime import datetime

from djangoformsetjs.utils import formset_media_js


class DataDictionaryUploadForm(ModelForm):
	notes = forms.CharField(required=False,
		help_text="Is there anything else we should know about this dataset?",
		label="Dataset notes",
		widget=forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}))
	attachments = forms.FileField(required=False,
		help_text="If you already have a data dictionary for this file, you can upload it\
		here rather than filling out the rest of this form.",
		widget=forms.FileInput(attrs={'class': 'form-control'}))

	class Meta:
		model = DataDictionary
		fields = ('notes', 'attachments')


class DataDictionaryFieldUploadForm(ModelForm):
	columnIndex = forms.ChoiceField(widget=forms.Select(
		attrs={"class": "form-control"}),
		help_text="What column number/letter is this?",
		label="Column",
		choices=DataDictionaryField.COLUMN_INDEX_CHOICES)
	heading = forms.CharField(required=False,
		max_length=100,
		help_text="What is the name of this column?",
		widget=forms.TextInput(attrs={"class": "form-control"}))
	description = forms.CharField(required=False,
		help_text="What can you tell us about this column?",
		widget=forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}))
	dataType = forms.ChoiceField(widget=forms.Select(
		attrs={"class": "form-control"}),
		choices=DataDictionaryField.DATATYPE_CHOICES)

	def __init__(self, *args, **kwargs):
		super(DataDictionaryFieldUploadForm, self).__init__(*args, **kwargs)
		self.fields['dataType'].initial = 'TEXT'

	class Media(object):
		js = formset_media_js + (
			# other form media here
		)

	class Meta:
		model = DataDictionaryField
		fields = ('columnIndex', 'heading', 'description', 'dataType')


class DatasetUploadForm(ModelForm):
	def clean(self):
		cleaned_data = super(DatasetUploadForm, self).clean()
		date_begin = self.cleaned_data.get('date_begin')
		date_end = self.cleaned_data.get('date_end')
		if date_end < date_begin:
			msg = u'End date should be after start date.'
			self.add_error('date_begin', msg)
			self.add_error('date_end', msg)
		return cleaned_data

	VALID_DATE_FORMS_TEXT = """Enter as YYYY-MM-DD,
		MM/DD/YYYY or MM/DD/YY."""

	hubs_json = requests.get('http://datalab.dallasnews.com/staff/api/hub/').json()
	HUBS_CHOICES = ((hub['slug'], hub['name']) for hub in hubs_json)

	START_YR = 1900
	END_YR = datetime.now().year
	YEARS = [yr for yr in range(START_YR, END_YR+1)]

	def get_vertical_from_hub(self, hub_slug):
		for hub in self.hubs_json:
			if hub['slug'] == hub_slug:
				return hub['vertical']['slug']

	title = forms.CharField(max_length=100,
		label="Dataset title",
		help_text="Make your title as descriptive and succinct as possible.",
		widget=forms.TextInput(attrs={"class": "form-control"}))
	description = forms.CharField(widget=forms.Textarea(attrs={'rows': 4,
		"class": "form-control"}),
		label="Dataset description",
		help_text="What do these data show?")
	source = forms.CharField(
		widget=forms.TextInput(
			attrs={"class": "form-control"}
		), label="Dataset source",
		help_text="Where were these data found?"
	)
	date_begin = forms.DateField(required=False,
		label="Beginning date of dataset time frame",
		help_text=VALID_DATE_FORMS_TEXT,
		widget=forms.SelectDateWidget(years=YEARS,
			attrs={"class": "form-control"}))
	date_end = forms.DateField(required=False,
		label="End date of dataset time frame",
		help_text=VALID_DATE_FORMS_TEXT,
		widget=forms.SelectDateWidget(years=YEARS,
			attrs={"class": "form-control"}))
	# vertical_slug = forms.ChoiceField(label="Vertical",
	#	 help_text="To which vertical does this dataset best belong?",
	#	 widget=forms.Select(attrs={"class": "form-control"}))
	hub_slug = forms.ChoiceField(label="Hub",
		help_text="To which hub does this dataset best belong?",
		widget=forms.Select(attrs={"class": "form-control"}),
		choices=HUBS_CHOICES)
	appears_in = MultiURLField(required=False,
		label="Article URL",
		help_text="""Were these data published in an article yet?
			This form requires full URLs separated by commas:
			http://www.dallasnews.com/123/your-article,
			http://beta.dallasnews.com/123/your-article, etc.""",
		widget=forms.URLInput(attrs={"class": "form-control"}))
	dataset_file = forms.FileField(label="File input",
		validators=[validate_dataset_file],
		help_text="Upload your file as comma separated values (CSV).",
		widget=forms.FileInput(attrs={'class': 'form-control'}))
	has_headers = forms.BooleanField(required=False,
		label="File headers",
		help_text="Does the first row of your CSV contain column headers?",
		widget=forms.CheckboxInput(attrs={'type': 'checkbox'}))
	tags = forms.CharField(label="Tags",
		help_text="Enter terms applicable to this dataset separated by commas. \
		If your term appears in the dropdown menu, select it.",
		widget=forms.TextInput(attrs={"class": "form-control"}))

	class Meta:
		model = Dataset
		fields = ('title', 'description', 'source', 'date_begin', 'date_end',
			'hub_slug', 'appears_in', 'tags', 'dataset_file', 'has_headers')
