# Imports from python.  # NOQA
from copy import deepcopy
from csv import reader, writer  # NOQA
import json
# from urlparse import urlparse


# Imports from django.
# from django.contrib.auth.decorators import login_required
# from django.core.exceptions import (
#     ObjectDoesNotExist,  # NOQA
#     PermissionDenied,
#     ValidationError,
# )
# from django.core.mail import send_mail, EmailMultiAlternatives
from django.core.paginator import (
    EmptyPage,  # NOQA
    PageNotAnInteger,
    Paginator,
)
from django.db.models import Count
# from django import forms
from django.forms import (
    # formset_factory,  # NOQA
    inlineformset_factory,
)
from django.http import (
    HttpResponse,  # NOQA
    # HttpResponseRedirect,
    Http404,
    # HttpResponseForbidden,
    # QueryDict
)
from django.shortcuts import (
    render,  # NOQA
    # render_to_response,
    get_object_or_404,
    # get_list_or_404,
    redirect
)
# from django.template import RequestContext
# from django.template.loader import render_to_string
# from django.templatetags.static import static
from django.utils.text import (
    # normalize_newlines,  # NOQA
    slugify
)
from django.views.decorators.http import require_http_methods
from django.views.generic import View


# Imports from datafreezer.
from datafreezer.apps import HUBS_LIST, STAFF_LIST  # NOQA
from datafreezer.forms import (
    DataDictionaryFieldUploadForm,  # NOQA
    # DataDictionaryUploadForm,
    DatasetUploadForm,
)
# Create Table SQL TK
# from datafreezer.helpers import (
#     get_connection_string,  # NOQA
#     get_db_type_from_text,
# )
from datafreezer.models import (
    Article,  # NOQA
    DataDictionary,
    DataDictionaryField,
    Dataset,
    Tag,
)


# Imports from other dependencies.
from bs4 import BeautifulSoup
import requests
# Create Table SQL TK
# from sqlalchemy import (
#     Column,
#     create_engine,
#     # Integer,
#     MetaData,
#     Table,
#     # Text,
#     # Unicode,
# )
# from sqlalchemy.schema import CreateTable


def map_hubs_to_verticals():
    """Return all verticals (sections) mapped to hubs (subsections).

    """
    vertical_hub_map = {}
    for hub in HUBS_LIST:
        vertical_slug = hub['vertical']['slug']
        if vertical_slug not in vertical_hub_map:
            vertical_hub_map[vertical_slug] = {
                'name': hub['vertical']['name'],
                'hubs': [hub['slug']]
            }
        else:
            vertical_hub_map[vertical_slug]['hubs'].append(hub['slug'])

    return vertical_hub_map

VERTICAL_HUB_MAP = map_hubs_to_verticals()


def add_dataset(request, dataset_id=None):
    """Handles creation of Dataset models from form POST information.

    Called by edit_dataset_metadata(...) view between Dataset entry and
    Data Dictionary entry. If dataset_id is passed as an argument, this
    function edits a given dataset rather than adding a dataset.
    Otherwise, a new model is saved to the database.

    Adds article URLs and scrapes page for headline, saves tags to DB.

    Returns the same page if validation fails, otherwise returns a
    redirect to data dictionary creation/edit.
    """
    # Save form to create dataset model
    # Populate non-form fields
    if dataset_id:
        dataset_instance = Dataset.objects.get(pk=dataset_id)

        metadata_form = DatasetUploadForm(
            request.POST,
            request.FILES,
            instance=dataset_instance
        )

        # metadata_form.base_fields['dataset_file'].required = False

    else:
        metadata_form = DatasetUploadForm(
            request.POST,
            request.FILES
        )

    if metadata_form.is_valid():
        dataset_metadata = metadata_form.save(commit=False)

        dataset_metadata.uploaded_by = request.user.email
        dataset_metadata.slug = slugify(dataset_metadata.title)

        # Find vertical from hub
        dataset_metadata.vertical_slug = metadata_form.get_vertical_from_hub(
            dataset_metadata.hub_slug
        )
        dataset_metadata.source_slug = slugify(dataset_metadata.source)

        # Save to database so that we can add Articles,
        # DataDictionaries, other foreignkeyed/M2M'd models.
        dataset_metadata.save()

        # Create relationships
        url_list = metadata_form.cleaned_data['appears_in'].split(', ')
        tag_list = metadata_form.cleaned_data['tags'].split(', ')
        # print(tag_list)

        dictionary = DataDictionary()
        dictionary.author = request.user.email
        dictionary.save()

        dataset_metadata.data_dictionary = dictionary
        dataset_metadata.save()

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

                        # Looking for <meta ... property="og:title">
                        meta_title_tag = soup.find(
                            'meta',
                            attrs={'property': 'og:title'}
                        )

                        try:
                            # print "Trying og:title..."
                            # print meta_title_tag
                            title = meta_title_tag['content']
                        except (TypeError, KeyError):
                            # TypeError implies meta_title_tag is None;
                            # KeyError implies that meta_title_tag does not
                            # have a content property.
                            title_tag = soup.find('title')

                            try:
                                # print "Falling back to title..."
                                # print title_tag
                                title = title_tag.text
                            except (TypeError, KeyError):
                                description_tag = soup.find(
                                    'meta',
                                    attrs={'property': 'og:description'}
                                )

                                try:
                                    # print "Falling back to description..."
                                    # print description_tag
                                    title = description_tag['content']
                                # Fallback value. Display is handled in models.
                                except (TypeError, KeyError):
                                    title = None

                        article.title = title
                        article.save()

                dataset_metadata.appears_in.add(article)

            for tag in tag_list:
                if tag:
                    cleanTag = tag.strip().lower()

                    tagToAdd, created = Tag.objects.get_or_create(
                        slug=slugify(cleanTag),
                        defaults={'word': cleanTag}
                    )

                    dataset_metadata.tags.add(tagToAdd)

        return redirect(
            'datafreezer_datadict_upload',
            dataset_id=dataset_metadata.id
        )

    return render(
        request,
        'datafreezer/upload.html',
        {
            'fileUploadForm': metadata_form,
        }
    )


def parse_csv_headers(dataset_id):
    """Return the first row of a CSV as a list of headers."""
    data = Dataset.objects.get(pk=dataset_id)
    with open(data.dataset_file.path, 'r') as datasetFile:
        csvReader = reader(datasetFile, delimiter=',', quotechar='"')
        headers = next(csvReader)
        # print headers
    return headers


# Handles multiple emails, returns a dictionary of {email: name}
def grab_names_from_emails(email_list):
    """Return a dictionary mapping names to email addresses.

    Only gives a response if the email is found
    in the staff API/JSON.

    Expects an API of the format =
    [
        {
            'email': 'foo@bar.net',
            ...
            'fullName': 'Frank Oo'
        },
        ...
    ]

    """
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
    """Return a hub name from its slug."""
    for hub in HUBS_LIST:
        if hub['slug'] == hub_slug:
            return hub['name']

    return hub_slug


def get_vertical_name_from_slug(vertical_slug):
    """Return a vertical name from its slug."""
    for hub in HUBS_LIST:
        if hub['vertical']['slug'] == vertical_slug:
            return hub['vertical']['name']

    return vertical_slug


@require_http_methods(["GET"])
def tag_lookup(request):
    """JSON endpoint that returns a list of potential tags.

    Used for upload template autocomplete.

    """
    tag = request.GET['tag']
    tagSlug = slugify(tag.strip())
    tagCandidates = Tag.objects.values('word').filter(slug__startswith=tagSlug)
    tags = json.dumps([candidate['word'] for candidate in tagCandidates])
    return HttpResponse(tags, content_type='application/json')


@require_http_methods(["GET"])
def source_lookup(request):
    """JSON endpoint that returns a list of potential sources.

    Used for upload template autocomplete.
    """
    source = request.GET['source']
    source_slug = slugify(source.strip())
    source_candidates = Dataset.objects.values('source').filter(
        source_slug__startswith=source_slug
    )
    sources = json.dumps([cand['source'] for cand in source_candidates])

    return HttpResponse(sources, content_type='application/json')


@require_http_methods(["GET"])
def download_data_dictionary(request, dataset_id):
    """Generates and returns compiled data dictionary from database.

    Returned as a CSV response.
    """
    dataset = Dataset.objects.get(pk=dataset_id)
    dataDict = dataset.data_dictionary
    fields = DataDictionaryField.objects.filter(
        parent_dict=dataDict
    ).order_by('columnIndex')

    response = HttpResponse(content_type='text/csv')
    csvName = slugify(dataset.title + ' data dict') + '.csv'
    response['Content-Disposition'] = 'attachment; filename=%s' % (csvName)

    csvWriter = writer(response)
    metaHeader = [
        'Data Dictionary for {0} prepared by {1}'.format(
            dataset.title,
            dataset.uploaded_by
        )
    ]
    csvWriter.writerow(metaHeader)
    trueHeader = ['Column Index', 'Heading', 'Description', 'Data Type']
    csvWriter.writerow(trueHeader)

    for field in fields:
        mappedIndex = field.COLUMN_INDEX_CHOICES[field.columnIndex-1][1]
        csvWriter.writerow(
            [mappedIndex, field.heading, field.description, field.dataType]
        )

    return response


# @login_required
# Home page for the application
def home(request):
    """Renders Datafreezer homepage. Includes recent uploads."""
    recent_uploads = Dataset.objects.order_by('-date_uploaded')[:11]

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

    return render(
        request,
        'datafreezer/home.html',
        {
            'recent_uploads': recent_uploads,
            'heading': 'Most Recent Uploads'
        }
    )


# Upload a data set here
def edit_dataset_metadata(request, dataset_id=None):
    """Renders a template to upload or edit a Dataset.

    Most of the heavy lifting is done by add_dataset(...).

    """
    if request.method == 'POST':
        return add_dataset(request, dataset_id)

    elif request.method == 'GET':
        # create a blank form
        # Edit
        if dataset_id:
            metadata_form = DatasetUploadForm(
                instance=get_object_or_404(Dataset, pk=dataset_id)
            )
        # Upload
        else:
            metadata_form = DatasetUploadForm()

        return render(
            request,
            'datafreezer/upload.html',
            {
                'fileUploadForm': metadata_form,
            }
        )


class DataDictionaryEditView(View):
    """Edit/create view for each dataset's data dictionary."""
    def get(self, request, dataset_id):
        active_dataset = get_object_or_404(Dataset, pk=dataset_id)

        data_dictionary = None
        if active_dataset.data_dictionary is not None:
            data_dictionary = active_dataset.data_dictionary

        DictFieldsFormSet = inlineformset_factory(
            DataDictionary,
            DataDictionaryField,
            form=DataDictionaryFieldUploadForm,
            extra=0
        )

        formset = DictFieldsFormSet(instance=data_dictionary)

        ExtraFormSet = inlineformset_factory(
            DataDictionary,
            DataDictionaryField,
            form=DataDictionaryFieldUploadForm,
            extra=1
        )

        extra_formset = ExtraFormSet()

        return render(
            request,
            'datafreezer/datadict_edit.html',
            {
                # 'fieldsFormset': fieldsFormset,
                # 'dataDictExtrasForm': DataDictionaryExtras,
                # 'title': page_title,
                # 'hasHeaders': active_dataset.has_headers,
                'ds': active_dataset,
                'formset': formset,
                'extra_formset': extra_formset,
            }
        )

    def post(self, request, dataset_id):
        active_dataset = get_object_or_404(Dataset, pk=dataset_id)

        data_dictionary = None
        if active_dataset.data_dictionary is not None:
            data_dictionary = active_dataset.data_dictionary

        DictFieldsFormSet = inlineformset_factory(
            DataDictionary,
            DataDictionaryField,
            form=DataDictionaryFieldUploadForm,
            extra=0
        )

        formset = DictFieldsFormSet(
            request.POST,
            request.FILES,
            instance=data_dictionary,
        )

        if formset.is_valid():
            print(1)
            formset.save()

            return redirect('datafreezer_dataset_detail', dataset_id)

        print(formset.errors)

        return render(
            request,
            'datafreezer/datadict_edit.html',
            {
                # 'fieldsFormset': fieldsFormset,
                # 'dataDictExtrasForm': DataDictionaryExtras,
                # 'title': page_title,
                # 'hasHeaders': active_dataset.has_headers,
                'ds': active_dataset,
                'formset': formset,
                'formset_shown': formset,
            }
        )


# View individual dataset
def dataset_detail(request, dataset_id):
    """Renders individual dataset detail page."""
    active_dataset = get_object_or_404(Dataset, pk=dataset_id)
    datadict_id = active_dataset.data_dictionary_id
    datadict = DataDictionaryField.objects.filter(
        parent_dict=datadict_id
    ).order_by('columnIndex')
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

    return render(
        request,
        'datafreezer/dataset_details.html',
        {
            'dataset': active_dataset,
            'datadict': datadict,
            'uploader_name': uploader_name,
            'tags': tags,
            'articles': articles,
        }
    )

# Generate Create Table SQL Feature TK
# class GenerateCreateTable(View):
#     """Generates/returns CREATE TABLE statements in various SQL flavors.
#
#     Generates statement based on data dictionary field information
#     entered into DB.
#
#     """
#     def get(self, request):
#         data_dict_id = request.GET['data_dict_id']
#         sql_dialect = request.GET['sql_dialect']
#         dataDictionary = get_object_or_404(DataDictionary, pk=data_dict_id)
#         fields = DataDictionaryField.objects.filter(
#             parent_dict=dataDictionary.id
#         ).order_by('columnIndex')
#
#         cols = [
#             {
#                 'name': field.heading,
#                 'type': get_db_type_from_text(field.dataType)
#             }
#             for field in fields
#         ]
#
#         e = create_engine(get_connection_string(sql_dialect))
#
#         newTable = Table(dataDictionary.dataset.title,
#             MetaData(bind=e),
#             *(Column(col['name'], col['type'])
#                 for col in cols
#             )  # noqa
#         )
#
#         createTableStatement = CreateTable(newTable)
#
#         # print(createTableStatement)
#
#         return HttpResponse(createTableStatement)


class PaginatedBrowseAll(View):
    """Return all Datasets to template ordered by date uploaded.

    """

    template_path = 'datafreezer/browse_all.html'
    browse_type = 'ALL'
    page_title = "Browse "

    def generate_page_title(self):
        return self.page_title + self.browse_type.title()

    def generate_sections(self):
        datasets = Dataset.objects.all().order_by('-date_uploaded')
        for dataset in datasets:
            dataset.fullName = grab_names_from_emails([
                dataset.uploaded_by
            ])[dataset.uploaded_by]
        return datasets

    def get(self, request):
        """Handle HTTP GET request.

        Returns template and context from generate_page_title and
        generate_sections to populate template.
        """
        sections_list = self.generate_sections()

        p = Paginator(sections_list, 25)

        page = request.GET.get('page')

        try:
            sections = p.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            sections = p.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), return last page of results.
            sections = p.page(p.num_pages)

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


class BrowseBase(View):
    """Abstracted class for class-based Browse views.

    self.page_title is used to generate the page title shown atop the template.
    self.paginated indicates whether a page is paginated or not.
    self.template_path is used in child classes to specify the template used.

    """

    page_title = "Browse "
    paginated = False

    def generate_page_title(self):
        """Not implemented in base class.

        Child classes return an appropriate page title to template.
        """
        raise NotImplementedError

    def generate_sections(self):
        """Not implemented in base class.

        Child classes return categories/sections dependent on the type of view.
        For mid-level browse views, these are categorical.
        For all, these sections are simply datasets.
        """
        raise NotImplementedError

    def get(self, request):
        """View for HTTP GET method.

        Returns template and context from generate_page_title and
        generate_sections to populate template.
        """
        sections = self.generate_sections()

        if self.paginated:
            p = Paginator(sections, 25)

            page = request.GET.get('page')

            try:
                sections = p.page(page)
            except PageNotAnInteger:
                # If page is not an integer, deliver first page.
                sections = p.page(1)
            except EmptyPage:
                # If page is out of range (e.g. 9999), return last page
                # of results.
                sections = p.page(p.num_pages)

            pageUpper = int(p.num_pages) / 2

            try:
                pageLower = int(page) / 2
            except TypeError:
                pageLower = -999
        else:
            pageUpper = None
            pageLower = None

        context = {
            'sections': sections,
            'page_title': self.generate_page_title(),
            'browse_type': self.browse_type,
            'pageUpper': pageUpper,
            'pageLower': pageLower
        }

        return render(
            request,
            self.template_path,
            context
        )


class BrowseAll(BrowseBase):
    """Return all Datasets to paginated template ordered by date uploaded.

    Child class of BrowseBase.
    """

    template_path = 'datafreezer/browse_all.html'
    browse_type = 'ALL'
    paginated = True

    def generate_page_title(self):
        """Return browse all page title."""
        return self.page_title + self.browse_type.title()

    def generate_sections(self):
        """Return all datasets ordered by date uploaded/uploader name.

        """
        datasets = Dataset.objects.all().order_by('-date_uploaded')
        for dataset in datasets:
            dataset.fullName = grab_names_from_emails([
                dataset.uploaded_by
            ])[dataset.uploaded_by]
        return datasets


class BrowseHubs(BrowseBase):
    """Return all hubs to which Datasets are linked.

    Child class of BrowseBase.

    """
    template_path = 'datafreezer/browse_mid.html'
    browse_type = 'HUBS'

    def generate_page_title(self):
        """Return browse hub page title."""
        return self.page_title + self.browse_type.title()

    def generate_sections(self):
        """Return all hubs, slugs, and upload counts."""
        datasets = Dataset.objects.values(
            'hub_slug'
        ).annotate(
            upload_count=Count(
                'hub_slug'
            )
        ).order_by('-upload_count')

        return [
            {
                'count': dataset['upload_count'],
                'name': get_hub_name_from_slug(dataset['hub_slug']),
                'slug': dataset['hub_slug']
            }
            for dataset in datasets
        ]

        # for dataset in datasets:
        #     dataset['hub_name'] = get_hub_name_from_slug(dataset['hub_slug'])


class BrowseAuthors(BrowseBase):
    """Return all authors to which datasets are linked.

    Child class of BrowseBase.

    """
    template_path = 'datafreezer/browse_mid.html'
    browse_type = 'AUTHORS'

    def generate_page_title(self):
        """Return browse author page title."""
        return self.page_title + self.browse_type.title()

    def generate_sections(self):
        """Return all authors to which datasets have been attributed."""
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
    """Return all tags to which datasets are linked.

    Child class of BrowseBase.

    """
    template_path = 'datafreezer/browse_mid.html'
    browse_type = 'TAGS'

    def generate_page_title(self):
        return self.page_title + self.browse_type.title()

    def generate_sections(self):
        tags = Tag.objects.all().annotate(
            dataset_count=Count('dataset')
        ).order_by('-dataset_count')

        sections = [
            {
                'slug': tag.slug,
                'name': tag.word,
                'count': tag.dataset_count
            }
            for tag in tags
        ]

        return sections


class BrowseVerticals(BrowseBase):
    """Return all verticals to which datasets are linked.

    Child class of BrowseBase.

    """
    template_path = 'datafreezer/browse_mid.html'
    browse_type = 'VERTICALS'

    def generate_page_title(self):
        return self.page_title + self.browse_type.title()

    def generate_sections(self):
        hub_counts = Dataset.objects.values('hub_slug').annotate(
            hub_count=Count('hub_slug')
        )
        # We don't want to change the original
        vertical_sections = deepcopy(VERTICAL_HUB_MAP)

        for vertical in vertical_sections:
            vertical_sections[vertical]['count'] = 0
            for hub in hub_counts:
                if hub['hub_slug'] in vertical_sections[vertical]['hubs']:
                    vertical_sections[vertical]['count'] += hub['hub_count']

        return sorted([
            {
                'slug': vertical,
                'name': vertical_sections[vertical]['name'],
                'count': vertical_sections[vertical]['count']
            }
            for vertical in vertical_sections
        ], key=lambda k: k['count'], reverse=True)


class BrowseSources(BrowseBase):
    """Return all sources to which datasets are linked.

    Child class of BrowseBase.

    """
    template_path = 'datafreezer/browse_mid.html'
    browse_type = 'SOURCES'

    def generate_page_title(self):
        """Return page title for Browse Sources."""
        return self.page_title + self.browse_type.title()

    def generate_sections(self):
        """Return dictionary of source section slugs, name, and counts."""
        sources = Dataset.objects.values(
            'source', 'source_slug'
        ).annotate(source_count=Count('source_slug'))

        return sorted([
            {
                'slug': source['source_slug'],
                'name': source['source'],
                'count': source['source_count']
            }
            for source in sources
        ], key=lambda k: k['count'], reverse=True)


class DetailBase(View):
    """Base class for mid-level Detail pages. These are aggregate pages.

    """

    def generate_page_title(self, data_slug):
        """Not implemented in base class.

        Generates a page title in child classes.
        """
        raise NotImplementedError

    def generate_matching_datasets(self, data_slug):
        """Not implemented in base class.

        Generates datasets that match data_slug.
        """
        raise NotImplementedError

    def generate_additional_context(self, matching_datasets):
        """Not implemented in base class.

        Generates additional context displayed on page.
        """
        raise NotImplementedError

    def get(self, request, slug):
        """Basic functionality for GET request to view.

        """
        matching_datasets = self.generate_matching_datasets(slug)

        if matching_datasets is None:
            raise Http404("Datasets meeting these criteria do not exist.")

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
    """Renders author-specific Dataset aggregate page.

    Extends DetailBase.
    """
    template_path = 'datafreezer/author_detail.html'

    def generate_page_title(self, data_slug):
        """Generates remainder of author-specific title based on slug.

        """
        return grab_names_from_emails([data_slug])[data_slug]

    def generate_matching_datasets(self, data_slug):
        """Return datasets that match data_slug (author email).

        """
        return Dataset.objects.filter(
            uploaded_by=data_slug
        ).order_by('-date_uploaded')

    def generate_additional_context(self, matching_datasets):
        """Return additional information about matching datasets.

        Includes upload counts, related hubs, related tags.
        """
        dataset_ids = [upload.id for upload in matching_datasets]
        tags = Tag.objects.filter(
            dataset__in=dataset_ids
        ).distinct().annotate(
            Count('word')
        ).order_by('-word__count')[:5]

        hubs = matching_datasets.values("hub_slug").annotate(
            Count('hub_slug')
        ).order_by('-hub_slug__count')

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
    """Renders tag-specific detail page.

    Extends DetailBase.
    """
    template_path = 'datafreezer/tag_detail.html'

    def generate_page_title(self, data_slug):
        """Generates remainder of page title specific to data_slug (tag)."""
        tag = Tag.objects.filter(slug=data_slug)
        return tag[0].word

    def generate_matching_datasets(self, data_slug):
        """Return datasets that match data_slug (tag)."""
        tag = Tag.objects.filter(slug=data_slug)
        try:
            return tag[0].dataset_set.all().order_by('-uploaded_by')
        except IndexError:
            return None

    def generate_additional_context(self, matching_datasets):
        """Return context about matching datasets."""
        related_tags = Tag.objects.filter(
            dataset__in=matching_datasets
        ).distinct().annotate(
            Count('word')
        ).order_by('-word__count')[:5]

        return {
            'related_tags': related_tags
        }


class HubDetail(DetailBase):
    """Renders hub-specific detail page.

    Extends DetailBase.
    """
    template_path = 'datafreezer/hub_detail.html'

    def generate_page_title(self, data_slug):
        """Generates remainder of page title specific to data_slug (hub)."""
        return get_hub_name_from_slug(data_slug)

    def generate_matching_datasets(self, data_slug):
        """Return datasets that match data_slug (hub_slug)."""
        matching_datasets = Dataset.objects.filter(
            hub_slug=data_slug
        ).order_by('-date_uploaded')

        if len(matching_datasets) > 0:
            return matching_datasets
        else:
            return None

    def generate_additional_context(self, matching_datasets):
        """Return top tags and authors for matching datasets.

        """
        top_tags = Tag.objects.filter(
            dataset__in=matching_datasets
        ).annotate(
            tag_count=Count('word')
        ).order_by('-tag_count')[:3]

        top_authors = Dataset.objects.filter(
            hub_slug=matching_datasets[0].hub_slug
        ).values('uploaded_by').annotate(
            author_count=Count('uploaded_by')
        ).order_by('-author_count')[:3]

        for author in top_authors:
            author['fullName'] = grab_names_from_emails([
                author['uploaded_by']
            ])[author['uploaded_by']]

        # print top_authors

        return {
            'top_tags': top_tags,
            'top_authors': top_authors
        }


class VerticalDetail(DetailBase):
    """Renders vertical-specific detail page.

    Extends DetailBase.

    """
    template_path = 'datafreezer/vertical_detail.html'

    def generate_page_title(self, data_slug):
        """Generate remainder of page title from data_slug (vertical slug)."""
        return get_vertical_name_from_slug(data_slug)

    def generate_matching_datasets(self, data_slug):
        """Return datasets that belong to a vertical by querying hubs.

        """
        matching_hubs = VERTICAL_HUB_MAP[data_slug]['hubs']
        return Dataset.objects.filter(hub_slug__in=matching_hubs)

    def generate_additional_context(self, matching_datasets):
        """Generate top tags and authors for a given Vertical."""
        top_tags = Tag.objects.filter(
            dataset__in=matching_datasets
        ).annotate(
            tag_count=Count('word')
        ).order_by('-tag_count')[:3]

        top_authors = Dataset.objects.filter(
            id__in=matching_datasets
        ).values('uploaded_by').annotate(
            author_count=Count('uploaded_by')
        ).order_by('-author_count')[:3]

        for author in top_authors:
            author['fullName'] = grab_names_from_emails([
                author['uploaded_by']
            ])[author['uploaded_by']]

        return {
            'top_tags': top_tags,
            'top_authors': top_authors
        }


class SourceDetail(DetailBase):
    """Render a source-specific detail page.

    Extends DetailBase.

    """
    template_path = 'datafreezer/source_detail.html'

    def generate_page_title(self, data_slug):
        """Generates remainder of page title based on data_slug (source)."""
        return Dataset.objects.filter(source_slug=data_slug)[0].source

    def generate_matching_datasets(self, data_slug):
        """Return datasets that match data_slug (source_slug)."""
        return Dataset.objects.filter(source_slug=data_slug)

    def generate_additional_context(self, matching_datasets):
        """Return top tags for a source."""
        top_tags = Tag.objects.filter(
            dataset__in=matching_datasets
        ).annotate(
            tag_count=Count('word')
        ).order_by('-tag_count')[:3]

        return {
            'top_tags': top_tags
        }
