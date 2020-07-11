from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save, post_delete

import os
from hashlib import md5
from datetime import datetime

from ..registration.models import DepartmentType
from .signals import generate_and_save_hash, auto_delete_file_on_delete


def generate_upload_location(instance, filename):
    filename = filename + str(datetime.now())
    m = md5(filename.encode())
    filename = m.hexdigest()[:10] + '.pdf'
    return 'sg_{}/{}'.format(
        instance.studentgroup.md5hash,
        filename)


class Batch(models.Model):
    number = models.PositiveSmallIntegerField(unique=True)
    max_groups_num = models.PositiveSmallIntegerField(default=5)
    min_groups_num = models.PositiveSmallIntegerField(default=0)

    class Meta:
        verbose_name_plural = 'batches'

    def __str__(self):
        return f'Batch {self.number}'


class StudentGroup(models.Model):
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        default=None,
        related_name='studentgroups',
        on_delete=models.SET_DEFAULT,
        limit_choices_to={"is_teacher": True},
    )
    internal = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        default=None,
        related_name='internal_studentgroups',
        on_delete=models.SET_DEFAULT,
        limit_choices_to={"is_teacher": True}
    )
    external = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        default=None,
        related_name='external_studentgroups',
        on_delete=models.SET_DEFAULT,
        limit_choices_to={"is_teacher": True},
    )
    title = models.CharField(max_length=256)
    department = models.CharField(
        max_length=3,
        choices=DepartmentType.choices,
    )
    md5hash = models.CharField(max_length=10, null=True)
    progress = models.IntegerField(default=0)
    approved = models.BooleanField(default=False)
    batch = models.ForeignKey(
        Batch,
        on_delete=models.SET_NULL,
        null=True,
    )
    field = models.ForeignKey(
        'ResearchField',
        null=True,
        default=None,
        related_name='studentgroups',
        on_delete=models.SET_NULL,
    )

    @property
    def status(self):
        if self.progress == 0:
            return 'Created'
        elif self.progress <= 59:
            return 'In Progress'
        elif self.progress <= 89:
            return 'Pre-Defense Done'
        elif self.progress <= 99:
            return 'Defense Done'
        else:
            return 'Finished'

    def save(self, *args, **kwargs):
        return super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.department}_{self.batch.number}_{self.id}'

    def generate_hash(self):
        text = self.title + str(datetime.now())
        m = md5(text.encode())
        return m.hexdigest()[:8]


class Document(models.Model):
    class DocumentType(models.TextChoices):
        PROPOSAL = "Proposal"
        PRE_DEFENSE = "Pre-Defense Report"
        DEFENSE = "Defense Report"

    studentgroup = models.ForeignKey(
        StudentGroup,
        on_delete=models.CASCADE,
        related_name='documents')
    upload_time = models.DateTimeField(auto_now_add=True)
    document_type = models.CharField(
        max_length=24,
        choices=DocumentType.choices,
    )
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
        limit_choices_to={'is_teacher': True},
        blank=True
    )

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Mark(models.Model):
    mark = models.PositiveSmallIntegerField()
    remarks = models.TextField(blank=True)
    studentgroup = models.ForeignKey(
        StudentGroup,
        on_delete=models.CASCADE,
    )
    graded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'is_teacher': True},
        related_name='graded_by_marks',
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'is_student': True},
        related_name='student_marks',
    )

    class Meta:
        default_related_name = 'marks'
        unique_together = ['studentgroup', 'graded_by', 'student']

    def clean(self):
        group = self.studentgroup
        if self.student not in group.students.all():
            raise ValidationError({"student": "Invalid Student"})
        elif self.graded_by != group.teacher or self.graded_by != group.internal or self.graded_by != group.external:
            raise ValidationError({"graded_by": "Invalid Teacher"})

    def __str__(self):
        return self.name


# Signals
post_save.connect(generate_and_save_hash, sender=StudentGroup)
post_delete.connect(auto_delete_file_on_delete, sender=Document)
