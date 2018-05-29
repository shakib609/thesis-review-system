from django.db import models
from django.conf import settings
from django.db.models.signals import post_save

from hashlib import md5
from datetime import datetime

from .signals import generate_and_save_hash


class StudentGroup(models.Model):
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        default=None,
        related_name='studentgroups',
        on_delete=models.SET_NULL)
    title = models.CharField(max_length=256)
    md5hash = models.CharField(max_length=10, null=True)

    def __str__(self):
        return self.title

    def generate_hash(self):
        text = self.title + str(datetime.now())
        m = md5(text.encode())
        return m.hexdigest()[:8]


# Signals
post_save.connect(generate_and_save_hash, sender=StudentGroup)
