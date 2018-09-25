from django.db import models
from django.conf import settings
from django.db.models.signals import post_save, post_delete

import os
from hashlib import md5
from datetime import datetime

from .signals import generate_and_save_hash, auto_delete_file_on_delete


def generate_upload_location(instance, filename):
    filename = filename + str(datetime.now())
    m = md5(filename.encode())
    filename = m.hexdigest()[:10] + '.pdf'
    return 'sg_{}/{}'.format(
        instance.studentgroup.md5hash,
        filename)


class StudentGroup(models.Model):
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        default=None,
        related_name='studentgroups',
        on_delete=models.SET_NULL)
    title = models.CharField(max_length=256)
    md5hash = models.CharField(max_length=10, null=True)
    approved = models.BooleanField(default=False)
    field = models.ForeignKey(
        'ResearchField',
        null=True,
        default=None,
        related_name='studentgroups',
        on_delete=models.SET_NULL,
    )

    def __str__(self):
        return self.title

    def generate_hash(self):
        text = self.title + str(datetime.now())
        m = md5(text.encode())
        return m.hexdigest()[:8]


class Document(models.Model):
    studentgroup = models.ForeignKey(
        StudentGroup,
        on_delete=models.CASCADE,
        related_name='documents')
    upload_time = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to=generate_upload_location)

    class Meta:
        ordering = ['-upload_time', ]

    def __str__(self):
        return self.filename

    @property
    def filename(self):
        return os.path.basename(self.file.name)


class Comment(models.Model):
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    studentgroup = models.ForeignKey(
        StudentGroup,
        on_delete=models.CASCADE,
        related_name='comments'
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.content[:10] + '...'


class ResearchField(models.Model):
    name = models.CharField(max_length=256)
    teachers = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='fields',
        limit_choices_to={'is_teacher': True}
    )

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


# Signals
post_save.connect(generate_and_save_hash, sender=StudentGroup)
post_delete.connect(auto_delete_file_on_delete, sender=Document)
