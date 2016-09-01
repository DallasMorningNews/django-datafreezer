# Imports from django.  # NOQA
from django.contrib import admin


# Imports from datafreezer.
from datafreezer.models import (
    Article,  # NOQA
    DataDictionary,
    DataDictionaryField,
    Dataset,
    Tag,
)

admin.site.register(Dataset)
admin.site.register(Tag)
admin.site.register(Article)
admin.site.register(DataDictionary)
admin.site.register(DataDictionaryField)
