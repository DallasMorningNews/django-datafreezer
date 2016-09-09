# Imports from django.  # NOQA
# from django.conf import settings
from django.conf.urls import (
    # include,
    url,  # NOQA
)
# from django.urls import reverse
# from django.views.generic.base import RedirectView
# from django.views.static import serve


# Imports from datafreezer.
from datafreezer.views import (
    AuthorDetail,  # NOQA
    BrowseAll,
    BrowseAuthors,
    BrowseHubs,
    BrowseSources,
    BrowseTags,
    BrowseVerticals,
    DataDictionaryEditView,
    dataset_detail,
    download_data_dictionary,
    edit_dataset_metadata,
    home,
    HubDetail,
    source_lookup,
    SourceDetail,
    tag_lookup,
    TagDetail,
    VerticalDetail,
    # GenerateCreateTable,
)


# django.contrib.auth.views.LoginView will be added in Django 1.11.
# Until then, load a version of the same from our own code instead.
try:
    from django.contrib.auth.views import LoginView, LogoutView  # NOQA
except ImportError:
    from datafreezer.views_compat import LoginView, LogoutView  # NOQA


urlpatterns = [
    # Home page.
    url(r'^$', home, name='datafreezer_home'),

    # Un-narrowed browse page.
    url(
        r'^browse/all/$',
        BrowseAll.as_view(),
        name='datafreezer_browse_all'
    ),



    # ################################## #
    # Lists of available facets by type. #
    # ################################## #

    # List of available authors.
    url(
        r'^browse/authors/$',
        BrowseAuthors.as_view(),
        name='datafreezer_browse_authors'
    ),

    # List of available hubs.
    url(
        r'^browse/hubs/$',
        BrowseHubs.as_view(),
        name='datafreezer_browse_hubs'
    ),

    # List of available sources.
    url(
        r'^browse/sources/$',
        BrowseSources.as_view(),
        name='datafreezer_browse_sources'
    ),

    # List of available tags.
    url(
        r'^browse/tags/$',
        BrowseTags.as_view(),
        name='datafreezer_browse_tags'
    ),

    # List of available verticals.
    url(
        r'^browse/verticals/$',
        BrowseVerticals.as_view(),
        name='datafreezer_browse_verticals'
    ),



    # ########################## #
    # Per-facet browsable pages. #
    # ########################## #

    # Matching datasets for chosen author.
    url(
        r'^browse/authors/(?P<slug>[\w.%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4})/$',
        AuthorDetail.as_view(),
        name='datafreezer_author_detail'
    ),

    # Matching datasets for chosen hub.
    url(
        r'^browse/hubs/(?P<slug>[-\w]+)/$',
        HubDetail.as_view(),
        name='datafreezer_hub_detail'
    ),

    # Matching datasets for chosen source.
    url(
        r'^browse/sources/(?P<slug>[-\w]+)/$',
        SourceDetail.as_view(),
        name='datafreezer_source_detail'
    ),

    # Matching datasets for chosen tag.
    url(
        r'^browse/tags/(?P<slug>[-\w]+)/$',
        TagDetail.as_view(),
        name='datafreezer_tag_detail'
    ),

    # Matching datasets for chosen vertical.
    url(
        r'^browse/verticals/(?P<slug>[-\w]+)/$',
        VerticalDetail.as_view(),
        name='datafreezer_vertical_detail'
    ),



    # ####################### #
    # Dataset-specific pages. #
    # ####################### #

    # Dataset creation form.
    url(
        r'^datasets/add/$',
        edit_dataset_metadata,
        name='datafreezer_upload'
    ),
    # Dataset detail page.
    url(
        r'^datasets/(?P<dataset_id>\d+)/$',
        dataset_detail,
        name='datafreezer_dataset_detail'
    ),
    # Dataset metadata editing form.
    url(
        r'^datasets/(?P<dataset_id>\d+)/change-dataset/$',
        edit_dataset_metadata,
        name='datafreezer_metadata_edit'
    ),
    # Dataset dictionary editing form.
    url(
        r'^datasets/(?P<dataset_id>\d+)/change-dictionary/$',
        DataDictionaryEditView.as_view(),
        name='datafreezer_datadict_edit'
    ),



    # ##################### #
    # Authentication views. #
    # ##################### #

    # Login form.
    url(
        r'^login/$',
        LoginView.as_view(
            success_url='/',
            template_name='datafreezer/login.html'
        ),
        name='datafreezer_login',
    ),

    url(
        r'^logout/$',
        LogoutView.as_view(
            template_name='datafreezer/logout.html'
        ),
        name='datafreezer_logout'
    ),



    # ############### #
    # JSON endpoints. #
    # ############### #

    # Lookup list for sources.
    url(
        r'^sourcelookup/$',
        source_lookup,
        name='datafreezer_source_lookup'
    ),

    # Lookup list for tags.
    url(
        r'^taglookup/$',
        tag_lookup,
        name='datafreezer_tag_lookup'
    ),



    # ########################## #
    # Other miscellaneous pages. #
    # ########################## #

    # Data Dictionary Download
    url(
        r'^download/datadict/(?P<dataset_id>\d{1,})/$',
        download_data_dictionary,
        name='datafreezer_download_data_dictionary'
    ),

    # Generate create table statement
    # url(r'^create_table_sql/$',
    #     GenerateCreateTable.as_view(),
    #     name='datafreezer_create_table_sql'),
]
