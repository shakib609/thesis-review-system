from django.db import models
from django.conf import settings

from hashlib import md5
from datetime import datetime


class StudentGroup(models.Model):
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        default=None,
        related_name='studentgroups',
        on_delete=models.SET_NULL)
    title = models.CharField(max_length=256)
    md5hash = models.CharField(max_length=33, null=True)

    def __str__(self):
        return self.title

    def generate_hash(self):
        text = self.title + str(datetime.now())
        m = md5(text.encode())
        return m.hexdigest()
