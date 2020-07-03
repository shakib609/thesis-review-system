from django.db import models
from django.conf import settings

import os

from thesis.utils import generate_upload_location


class ResearchField(models.Model):
    name = models.CharField(max_length=256)
    teachers = models.ManyToManyField(
        'users.Teacher',
        related_name='fields',
        blank=True,
        limit_choices_to={'is_teacher': True},
    )

    class Meta:
        default_related_name = 'research_fields'
        ordering = ['name']

    def __str__(self):
        return self.name


class Batch(models.Model):
    number = models.PositiveIntegerField()
    max_groups_limit = models.PositiveSmallIntegerField(default=5)
    min_groups_limit = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return self.number


class ThesisGroup(models.Model):
    title = models.CharField(max_length=512, blank=True)
    unique_id = models.CharField(max_length=10, blank=True)
    progress = models.IntegerField(default=0)
    approved = models.BooleanField(default=False)
    batch = models.ForeignKey(
        Batch,
        on_delete=models.CASCADE,
    )
    supervisor = models.ForeignKey(
        'users.Teacher',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    reviewer = models.ForeignKey(
        'users.Teacher',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    internal = models.ForeignKey(
        'users.Teacher',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    external = models.ForeignKey(
        'users.Teacher',
        on_delete=models.SET_NULL,
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
        default_related_name = 'thesis_groups'

    def save(self, **kwargs):
        if not self.unique_id:
            student = self.students.exclude(user__department='').first()
            if student is not None:
                department = student.user.department
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

    thesis_group = models.ForeignKey(
        ThesisGroup,
        on_delete=models.CASCADE,
    )
    upload_time = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to=generate_upload_location)
    type = models.CharField(
        max_length=20,
        choices=DocumentType.choices,
    )

    class Meta:
        default_related_name = 'documents'
        ordering = ['-upload_time', ]

    def __str__(self):
        return self.filename

    @property
    def filename(self):
        return os.path.basename(self.file.name)


class Grade(models.Model):
    marks = models.PositiveSmallIntegerField(default=0)
    thesis_group = models.ForeignKey(
        ThesisGroup,
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

    def __str__(self):
        return f'{self.student.user.username} - {self.graded_by.user.username} - {self.marks}'


class Notification(models.Model):
    text = models.TextField()
    is_viewed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    group = models.ForeignKey(
        ThesisGroup,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    class Meta:
        default_related_name = 'notifications'
        ordering = ['-created_at']

    def __str__(self):
        return self.text[:15]


class Message(models.Model):
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    created_for = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
    )

    class Meta:
        default_related_name = 'messages'
        ordering = ['-created_at']

    def __str__(self):
        return self.text[:15]
