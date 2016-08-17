from django import template
from django.utils.text import slugify
import json

register = template.Library()

@register.filter
def JSONify(value):
	return json.dumps(value)