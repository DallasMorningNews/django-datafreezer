from django.shortcuts import render, render_to_response, get_object_or_404, get_list_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect, Http404, HttpResponseForbidden, QueryDict
from django.template import RequestContext
from django.utils.text import normalize_newlines, slugify
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.core.exceptions import PermissionDenied, ValidationError, ObjectDoesNotExist
from django.templatetags.static import static
from django.forms import formset_factory
from django.views.decorators.http import require_http_methods
from django.views.generic import View
from django.db.models import Count

from datafreezer.models import Dataset, Article, Tag, DataDictionary, DataDictionaryField
from datafreezer.forms import DataDictionaryUploadForm, DataDictionaryFieldUploadForm, DatasetUploadForm

import requests
from urlparse import urlparse
from bs4 import BeautifulSoup
from csv import reader
import json


def load_json_endpoint(data_url):
    return requests.get(data_url).json()

# We can scrape any site that is optimized for social media (graph tags/og)
HUBS_LIST = load_json_endpoint(
    getattr(settings, 'HUBS_LIST_URL', '/api/hub/')
)
STAFF_LIST = load_json_endpoint(
    getattr(settings, 'STAFF_LIST_URL', '/api/staff/')
)


def add_dataset(fileUploadForm, request):
	# Save form to create dataset model
	# Populate non-form fields
	dataset_upload = fileUploadForm.save(commit=False)

	dataset_upload.uploaded_by = request.user.email
	dataset_upload.slug = slugify(dataset_upload.title)

	# Find vertical from hub
	hub_slug = dataset_upload.hub_slug
	dataset_upload.vertical_slug = fileUploadForm.get_vertical_from_hub(hub_slug)

	# Save to database so that we can add Articles,
	# DataDictionaries, other foreignkeyed/M2M'd models.
	dataset_upload.save()

	# Create relationships
	url_list = fileUploadForm.cleaned_data['appears_in']
	tag_list = fileUploadForm.cleaned_data['tags'].split(', ')
	print tag_list

	for url in url_list:
		url = url.strip()
		if len(url) > 0:
			article, created = Article.objects.get_or_create(url=url)
			if created:
				article_req = requests.get(url)
				if article_req.status_code == 200:
					# We good. Get the HTML.
					page = article_req.content
					soup = BeautifulSoup(page, 'html.parser')
					#Looking for <meta ... property="og:title">
					meta_title_tag = soup.find('meta', attrs={'property': 'og:title'})
					try:
						# print "Trying og:title..."
						# print meta_title_tag
						title = meta_title_tag['content']
					# TypeError implies meta_title_tag is None
					# KeyError implies that meta_title_tag does not have a content property.
					except (TypeError, KeyError):
						title_tag = soup.find('title')
						try:
							# print "Falling back to title..."
							# print title_tag
							title = title_tag.text
						except (TypeError, KeyError):
							description_tag = soup.find('meta', attrs={'property': 'og:description'})
							try:
								# print "Falling back to description..."
								# print description_tag
								title = description_tag['content']
							# Fall back value. Display is handled in models.
							except (TypeError, KeyError):
								title = None

					print title
					article.title = title
					article.save()

			dataset_upload.appears_in.add(article)

		for tag in tag_list:
			# print tag
			if tag:
				cleanTag = tag.strip().lower()
				tagToAdd, created = Tag.objects.get_or_create(slug=slugify(cleanTag), defaults={'word': cleanTag})
				dataset_upload.tags.add(tagToAdd)

	return dataset_upload


def parse_csv_headers(dataset_id):
	data = Dataset.objects.get(pk=dataset_id)
	with open(data.dataset_file.path, 'r') as datasetFile:
		reader = csv.reader(datasetFile, delimiter=',', quotechar='"')
		headers = next(reader)
		# print headers
	return headers


# Handles multiple emails, returns a dictionary of {email: name}
def grab_names_from_emails(email_list):
	all_staff = STAFF_LIST

	emails_names = {}

	for email in email_list:
		for person in all_staff:
			if email == person['email'] and email not in emails_names:
				emails_names[email] = person['fullName']
				# print emails_names[email]

	for email in email_list:
		matched = False
		for assignment in emails_names:
			if email == assignment:
				matched = True
		if not matched:
			emails_names[email] = email

	return emails_names

def get_hub_name_from_slug(hub_slug):
	for hub in HUBS_LIST:
		if hub['slug'] == hub_slug:
			return hub['name']

	return hub_slug

def get_vertical_name_from_slug(vertical_slug):
	for hub in HUBS_LIST:
		if hub['vertical']['slug'] == vertical_slug:
			return hub['vertical']['slug']

	return vertical_slug


@require_http_methods(["GET"])
def tag_lookup(request):
	tag = request.GET['tag']
	tagSlug = slugify(tag.strip().lower())
	tagCandidates = Tag.objects.filter(slug__startswith=tagSlug)
	tags = json.dumps([candidate.word for candidate in tagCandidates])
	return HttpResponse(tags, content_type='application/json')


# @login_required
# Home page for the application
def home(request):
	recent_uploads = Dataset.objects.order_by('-date_uploaded')[:10]

	email_list = [upload.uploaded_by.strip() for upload in recent_uploads]
	# print all_staff

	emails_names = grab_names_from_emails(email_list)
	# print emails_names

	for upload in recent_uploads:
		for item in emails_names:
			if upload.uploaded_by == item:
				upload.fullName = emails_names[item]

	for upload in recent_uploads:
		if not hasattr(upload, 'fullName'):
			upload.fullName = upload.uploaded_by

	return render(request, 'datafreezer/home.html',
		{'recent_uploads': recent_uploads,
		'heading': 'Most Recent Uploads'})


# Upload a data set here
def dataset_upload(request):
	if request.method == 'POST':
		# create form instance and populate it with data from the request
		fileUploadForm = DatasetUploadForm(request.POST, request.FILES)

		# If the form validates, we can create our models:
		if fileUploadForm.is_valid():
			# dataset_upload = fileUploadForm.save(commit=False)
			dataset_upload = add_dataset(fileUploadForm, request)

			return redirect('datafreezer_datadict_upload', dataset_id=dataset_upload.id)
			# return redirect('datafreezer_datadict_upload', dataset_id=dataset_upload.id)

	else:
		# create a blank form
		fileUploadForm = DatasetUploadForm()
	return render(request, 'datafreezer/upload.html',
		{'fileUploadForm': fileUploadForm,
		'formTitle': 'Upload a Dataset'})

# Data dictionary form
def data_dictionary_upload(request, dataset_id):
	active_dataset = get_object_or_404(Dataset, pk=dataset_id)
	if active_dataset.has_headers:
		headers = parse_csv_headers(dataset_id)
		# Would like to have this at beginning of function...
		DataDictionaryFormSet = formset_factory(DataDictionaryFieldUploadForm,
			max_num=len(headers))
	else:
		EXTRA_COLUMNS = 25
		DataDictionaryFormSet = formset_factory(DataDictionaryFieldUploadForm,
			can_delete=True)

	if request.method == 'POST':
		# Save DataDict to Dataset
		# We only want to save once it is submitted and complete
		# print request.POST
		# print request.POST.get("description")
		fieldsFormset = DataDictionaryFormSet(request.POST, request.FILES, prefix='fields')
		DataDictionaryExtras = DataDictionaryUploadForm(request.POST, request.FILES, prefix='overall')
		print request.POST
		# DataDictionaryExtras =
		if fieldsFormset.is_valid() and DataDictionaryExtras.is_valid():
			DataDict = DataDictionaryExtras.save(commit=False)
			DataDict.author = request.user.email
			DataDict.save()
			active_dataset.data_dictionary = DataDict
			active_dataset.save()
			for form in fieldsFormset:
				field = form.save(commit=False)
				field.parent_dict = DataDict
				field.save()
			return redirect('datafreezer_home')
	else:
		DataDictionaryExtras = DataDictionaryUploadForm(prefix='overall')
		# No Data Dict in DB. Create!
		if active_dataset.data_dictionary_id is None:
			page_title = 'Tell us more about your dataset'
			# Parse headers here

			if active_dataset.has_headers:
				fieldsFormset = DataDictionaryFormSet(initial=[
					{'heading': headers[index],
					'columnIndex': index + 1}
					for index in range(len(headers))],
					prefix='fields')
			else:
				fieldsFormset = DataDictionaryFormSet(prefix='fields')
		# Data Dict has been created already. Separate edit page or edit here?
		else:
			# @TODO: fix this
			# page_title = 'Edit your data dictionary'
			raise Http404("Data dictionary already created.")
	return render(request, 'datafreezer/datadict_upload.html',
		{'fieldsFormset': fieldsFormset,
		'dataDictExtrasForm': DataDictionaryExtras,
		'title': page_title,
		'hasHeaders': active_dataset.has_headers})

# View individual dataset
def dataset_detail(request, dataset_id):
	active_dataset = get_object_or_404(Dataset, pk=dataset_id)
	datadict_id = active_dataset.data_dictionary_id
	datadict = DataDictionaryField.objects.filter(parent_dict=datadict_id)
	uploader_name = grab_names_from_emails([active_dataset.uploaded_by])
	tags = Tag.objects.filter(dataset=dataset_id)
	articles = Article.objects.filter(dataset=dataset_id)

	for hub in HUBS_LIST:
		if hub['slug'] == active_dataset.hub_slug:
			active_dataset.hub = hub['name']
			active_dataset.vertical = hub['vertical']['name']

	if len(uploader_name) == 0:
		uploader_name = active_dataset.uploaded_by
	else:
		uploader_name = uploader_name[active_dataset.uploaded_by]
	return render(request, 'datafreezer/dataset_details.html',
		{'dataset': active_dataset,
		'datadict': datadict,
		'uploader_name': uploader_name,
		'tags': tags,
		'articles': articles})


class BrowseBase(View):
	page_title = "Browse "

	def generate_page_title(self):
		raise NotImplementedError

	def generate_sections(self):
		raise NotImplementedError

	def get(self, request):
		sections = self.generate_sections()

		context = {
			'sections': sections,
			'page_title': self.generate_page_title(),
			'browse_type': self.browse_type
		}

		return render(
			request,
			self.template_path,
			context
		)


class BrowseAuthors(BrowseBase):
	template_path = 'datafreezer/browse.html'
	browse_type = 'AUTHORS'

	def generate_page_title(self):
		return self.page_title + 'Authors'

	def generate_sections(self):
		authors = Dataset.objects.values(
			'uploaded_by'
		).annotate(
			upload_count=Count(
				'uploaded_by'
			)
		).order_by('-upload_count')

		email_name_map = grab_names_from_emails(
			[row['uploaded_by'] for row in authors]
		)

		for author in authors:
			for emailKey in email_name_map:
				if author['uploaded_by'] == emailKey:
					author['name'] = email_name_map[emailKey]

		return [
			{
				'slug': author['uploaded_by'],
				'name': author['name'],
				'count': author['upload_count']

			}
			for author in authors
		]


class BrowseTags(BrowseBase):
	template_path = 'datafreezer/browse.html'
	browse_type = 'TAGS'

	def generate_page_title(self):
		return self.page_title + 'Tags'

	def generate_sections(self):
		tags = Tag.objects.all().annotate(
			dataset_count=Count('dataset')
		).order_by('-dataset_count')

		sections = [
			{
				'id': tag.slug,
				'name': tag.word,
				'count': tag.dataset_count
			}
			for tag in tags
		]

		return sections


class DetailBase(View):
	def generate_page_title(self, data_slug):
		raise NotImplementedError

	def generate_matching_datasets(self, data_slug):
		raise NotImplementedError

	def generate_additional_context(self, matching_datasets):
		raise NotImplementedError

	def get(self, request, slug):
		matching_datasets = self.generate_matching_datasets(slug)

		base_context = {
			'datasets': matching_datasets,
			'num_datasets': matching_datasets.count(),
			'page_title': self.generate_page_title(slug),
		}

		additional_context = self.generate_additional_context(
			matching_datasets
		)

		base_context.update(additional_context)
		context = base_context

		return render(
			request,
			self.template_path,
			context
		)


class AuthorDetail(DetailBase):
	template_path = 'datafreezer/author_detail.html'

	def generate_page_title(self, data_slug):
		return grab_names_from_emails([data_slug])[data_slug]

	def generate_matching_datasets(self, data_slug):
		return Dataset.objects.filter(
			uploaded_by=data_slug
		).order_by('-date_uploaded')

	def generate_additional_context(self, matching_datasets):
		dataset_ids = [upload.id for upload in matching_datasets]
		tags = Tag.objects.filter(
			dataset__in=dataset_ids
		).distinct().annotate(
			Count('word')
		).order_by('-word__count')[:5]

		hubs = matching_datasets.values("hub_slug").annotate(Count('hub_slug')).order_by('-hub_slug__count')
		if hubs:
			most_used_hub = get_hub_name_from_slug(hubs[0]['hub_slug'])
			hub_slug = hubs[0]['hub_slug']
		else:
			most_used_hub = None
			hub_slug = None

		return {
			'tags': tags,
			'hub': most_used_hub,
			'hub_slug': hub_slug,
		}


class TagDetail(DetailBase):
	template_path = 'datafreezer/tag_detail.html'

	def generate_page_title(self, data_slug):
		tag = Tag.objects.filter(slug=data_slug)
		return tag[0].word

	def generate_matching_datasets(self, data_slug):
		tag = Tag.objects.filter(slug=data_slug)
		return tag[0].dataset_set.all().order_by('-uploaded_by')

	def generate_additional_context(self, matching_datasets):
		related_tags = Tag.objects.filter(
			dataset__in=matching_datasets
		).distinct().annotate(
			Count('word')
		).order_by('-word__count')[:5]

		return {
			'related_tags': related_tags
		}
