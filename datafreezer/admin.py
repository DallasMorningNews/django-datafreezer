from django.contrib import admin

from models import *

admin.site.register(Dataset)
admin.site.register(Tag)
admin.site.register(Article)
admin.site.register(DataDictionary)
admin.site.register(DataDictionaryField)
