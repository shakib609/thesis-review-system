from django.db import models
from django.conf import settings
from rest_framework.exceptions import APIException

import os

from groups.utils import generate_upload_location


class ResearchField(models.Model):
    name = models.CharField(max_length=256)
    teachers = models.ManyToManyField(
        'users.Teacher',
        related_name='fields',
        blank=True,
    )

    class Meta:
        db_table = "tbl_research_field"
        default_related_name = 'research_fields'
        ordering = ['name']

    def __str__(self):
        return self.name


class Batch(models.Model):
    number = models.PositiveIntegerField(primary_key=True)
    max_groups_limit = models.PositiveSmallIntegerField(default=5)
    min_groups_limit = models.PositiveSmallIntegerField(default=0)

    class Meta:
        db_table = "tbl_batch"
        ordering = ['-number']

    def __str__(self):
        return self.number


class MessageChannel(models.Model):
    title = models.CharField(max_length=16, blank=True)
    users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
    )

    class Meta:
        db_table = "tbl_message_channel"
        default_related_name = "message_channels"

    def __str__(self):
        return f'{self.title if self.title else "-"} - {self.users.count()}'


class Message(models.Model):
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    message_channel = models.ForeignKey(
        MessageChannel,
        on_delete=models.CASCADE,
    )

    class Meta:
        db_table = "tbl_message"
        default_related_name = 'messages'
        ordering = ['-created_at']

    def __str__(self):
        return self.text[:15]


class Group(models.Model):
    title = models.CharField(max_length=512, blank=True)
    unique_id = models.CharField(max_length=10, blank=True)
    progress = models.IntegerField(default=0)
    approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    message_channel = models.OneToOneField(
        MessageChannel,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    batch = models.ForeignKey(
        Batch,
        on_delete=models.CASCADE,
    )
    supervisor = models.ForeignKey(
        'users.Teacher',
        on_delete=models.SET_NULL,
        related_name='supervisor_groups',
        null=True,
        blank=True,
    )
    reviewer = models.ForeignKey(
        'users.Teacher',
        on_delete=models.SET_NULL,
        related_name='review_groups',
        null=True,
        blank=True,
    )
    internal = models.ForeignKey(
        'users.Teacher',
        on_delete=models.SET_NULL,
        related_name='internal_groups',
        null=True,
        blank=True,
    )
    external = models.ForeignKey(
        'users.Teacher',
        on_delete=models.SET_NULL,
        related_name='external_groups',
        null=True,
        blank=True,
    )
    field = models.ForeignKey(
        ResearchField,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    class Meta:
        db_table = "tbl_group"
        default_related_name = 'groups'
        ordering = ['created_at']

    def save(self, **kwargs):
        if not self.unique_id:
            student = self.students.exclude(user__department='').first()
            if student is not None:
                department = student.user.department
            else:
                raise APIException('Student has not department')
            last_group = self.objects.filter(
                unique_id__startswith=department).last()
            if last_group:
                last_group_uid = last_group.unique_id[-3:]
                n = int(last_group_uid) + 1
                group_id = f'{n:03}'
            else:
                group_id = '001'
            self.unique_id = f'{department}_{self.batch.number}_{group_id}'
        return super().save(**kwargs)

    def __str__(self):
        return self.title


class Document(models.Model):
    class DocumentType(models.TextChoices):
        PROPOSAL = 'Proposal Report'
        PRE_DEFENSE_REPORT = 'Pre-Defense Report'
        DEFENSE_REPORT = 'Defense Report'

    created_at = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to=generate_upload_location)
    is_accepted = models.BooleanField(default=False)
    type = models.CharField(
        max_length=20,
        choices=DocumentType.choices,
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
    )

    class Meta:
        db_table = "tbl_document"
        default_related_name = 'documents'
        ordering = ['-created_at', ]

    def __str__(self):
        return self.filename

    @property
    def filename(self):
        return os.path.basename(self.file.name)


class Mark(models.Model):
    class MarkLimit(models.IntegerChoices):
        SUPERVISOR = 50
        INTERNAL = 30
        EXTERNAL = 20

    marks = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    comments = models.TextField(blank=True)
    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
    )
    student = models.ForeignKey(
        'users.Student',
        on_delete=models.CASCADE,
    )
    graded_by = models.ForeignKey(
        'users.Teacher',
        on_delete=models.CASCADE,
    )

    class Meta:
        db_table = "tbl_mark"
        default_related_name = 'marks'
        unique_together = ['student', 'graded_by']

    def __str__(self):
        return f'{self.student.user.username} - {self.graded_by.user.username} - {self.marks}'
