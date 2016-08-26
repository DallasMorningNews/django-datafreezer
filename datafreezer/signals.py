# Imports from django.  # NOQA
# from django.conf import settings
# from django.core.mail import EmailMultiAlternatives
from django.db.models.signals import (
    post_save,  # NOQA
    # pre_save,
)
# from django.dispatch import receiver, Signal
# from django.template.loader import render_to_string


# Imports from datafreezer.
from datafreezer.models import Dataset


def foo(sender, **kwargs):
    # print "Received!"
    pass

post_save.connect(foo, sender=Dataset, weak=True, dispatch_uid=None)
