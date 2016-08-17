from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver, Signal
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from models import *


def foo(sender, **kwargs):
    print "Received!"

post_save.connect(foo, sender=Dataset, weak=True, dispatch_uid=None)
