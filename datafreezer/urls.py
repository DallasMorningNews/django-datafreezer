from django.conf.urls import url, include
from django.conf import settings
from views import *

urlpatterns = [
	url(r'^$', home, name='datafreezer_home'),
	url(r'^upload/$', dataset_upload, name='datafreezer_upload'),
	url(r'^browse/authors/$', BrowseAuthors.as_view(),
		name='datafreezer_browse_authors'),
	url(r'^browse/tags/$', BrowseTags.as_view(),
		name='datafreezer_browse_tags'),
	url(r'^upload/(?P<dataset_id>\d{1,})/$', data_dictionary_upload,
		name='datafreezer_datadict_upload'),
	url(r'^taglookup/$', tag_lookup,
		name='datafreezer_tag_lookup'),
	url(r'^browse/datasets/(?P<dataset_id>\d{1,})/$', dataset_detail,
		name='datafreezer_dataset_detail'),
	url(r'^browse/authors/(?P<slug>[\w.%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4})/$',
		AuthorDetail.as_view(), name='datafreezer_author_detail'),
	url(r'^browse/tags/(?P<slug>[-\w]+)/$',
		TagDetail.as_view(), name='datafreezer_tag_detail'),


	# url(r'^detail/(\d+)/$')
]
