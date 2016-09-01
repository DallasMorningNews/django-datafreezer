# Imports from django.  # NOQA
# from django.conf import settings
from django.conf.urls import (
    # include,
    url,  # NOQA
)
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

urlpatterns = [
    # Home page.
    url(r'^$', home, name='datafreezer_home'),

    # Upload pages
    url(
        r'^upload/$',
        edit_dataset_metadata,
        name='datafreezer_upload'
    ),
    url(
        r'^upload/(?P<dataset_id>\d{1,})/$',
        DataDictionaryEditView.as_view(),
        name='datafreezer_datadict_upload'
    ),
    url(
        r'^edit/(?P<dataset_id>\d+)/change-dictionary/$',
        DataDictionaryEditView.as_view(),
        name='datafreezer_datadict_edit'
    ),
    url(
        r'^browse/datasets/edit/(?P<dataset_id>\d{1,})/$',
        edit_dataset_metadata,
        name='datafreezer_metadata_edit'
    ),

    # Individual dataset detail
    url(
        r'^browse/datasets/(?P<dataset_id>\d{1,})/$',
        dataset_detail,
        name='datafreezer_dataset_detail'
    ),

    # Low-level browse URLs
    url(
        r'^browse/authors/(?P<slug>[\w.%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4})/$',
        AuthorDetail.as_view(),
        name='datafreezer_author_detail'
    ),
    url(
        r'^browse/tags/(?P<slug>[-\w]+)/$',
        TagDetail.as_view(),
        name='datafreezer_tag_detail'
    ),
    url(
        r'^browse/hubs/(?P<slug>[-\w]+)/$',
        HubDetail.as_view(),
        name='datafreezer_hub_detail'
    ),
    url(
        r'^browse/verticals/(?P<slug>[-\w]+)/$',
        VerticalDetail.as_view(),
        name='datafreezer_vertical_detail'
    ),
    url(
        r'^browse/sources/(?P<slug>[-\w]+)/$',
        SourceDetail.as_view(),
        name='datafreezer_source_detail'
    ),

    # Mid-level browse URLs
    url(
        r'^browse/all/$',
        BrowseAll.as_view(),
        name='datafreezer_browse_all'
    ),
    url(
        r'^browse/hubs/$',
        BrowseHubs.as_view(),
        name='datafreezer_browse_hubs'
    ),
    url(
        r'^browse/verticals/$',
        BrowseVerticals.as_view(),
        name='datafreezer_browse_verticals'
    ),
    url(
        r'^browse/sources/$',
        BrowseSources.as_view(),
        name='datafreezer_browse_sources'
    ),
    url(
        r'^browse/authors/$',
        BrowseAuthors.as_view(),
        name='datafreezer_browse_authors'
    ),
    url(
        r'^browse/tags/$',
        BrowseTags.as_view(),
        name='datafreezer_browse_tags'
    ),

    # Data Dict Download
    url(
        r'^download/datadict/(?P<dataset_id>\d{1,})/$',
        download_data_dictionary,
        name='datafreezer_download_data_dictionary'
    ),

    # Generate create table statement
    # url(r'^create_table_sql/$',
    #     GenerateCreateTable.as_view(),
    #     name='datafreezer_create_table_sql'),

    # JSON endpoints
    url(
        r'^taglookup/$',
        tag_lookup,
        name='datafreezer_tag_lookup'
    ),
    url(
        r'^sourcelookup/$',
        source_lookup,
        name='datafreezer_source_lookup'
    ),

    # url(r'^detail/(\d+)/$')
]
