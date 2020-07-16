from django.db import models
from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete

import os
from uuid import uuid4
from datetime import datetime

from ..registration.models import DepartmentType


def generate_upload_location(instance, filename):
    filename = filename + str(datetime.now())
    filename = uuid4().hex[:10] + '.pdf'
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
        limit_choices_to={"is_teacher": True, "is_external": True},
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
        documents_queryset = self.documents.filter(is_accepted=True)
        if documents_queryset.filter(document_type=Document.DocumentType.DEFENSE.value).exists():
            return 'Defense Done'
        elif documents_queryset.filter(document_type=Document.DocumentType.PRE_DEFENSE.value).exists():
            return 'Pre-Defense Done'
        elif documents_queryset.filter(document_type=Document.DocumentType.PROPOSAL.value).exists():
            return 'Proposal Done'
        else:
            return 'Pending Proposal Approval'

    def graded(self, user):
        return self.marks.filter(graded_by=user).exists()

    class Meta:
        ordering = ['id']

    def save(self, *args, **kwargs):
        if not self.md5hash:
            self.md5hash = uuid4().hex[:8]
        return super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.department}_{self.batch.number}_{self.id}'


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
    is_accepted = models.BooleanField(default=False)

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


class Notification(models.Model):
    content = models.TextField()
    is_viewed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    studentgroup = models.ForeignKey(
        StudentGroup,
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        'registration.User',
        on_delete=models.CASCADE,
    )

    class Meta:
        ordering = ['-created_at']
        default_related_name = 'notifications'

    def __str__(self):
        return f'Notification {self.content[:20]}'


@receiver(post_save, sender=Document)
def generate_notification_on_document_upload(sender, instance, **kwargs):
    studentgroup = instance.studentgroup
    content = f'A new Document({instance.document_type}) was uploaded to {studentgroup}'
    if studentgroup.approved:
        if studentgroup.teacher:
            Notification.objects.create(
                content=content,
                user=studentgroup.teacher,
                studentgroup=studentgroup,
            )
        if studentgroup.internal:
            Notification.objects.create(
                content=content,
                user=studentgroup.internal,
                studentgroup=studentgroup,
            )
        if studentgroup.external:
            Notification.objects.create(
                content=content,
                user=studentgroup.external,
                studentgroup=studentgroup,
            )


@receiver(post_save, sender=Comment)
def generate_notification_on_teacher_comment(sender, instance, **kwargs):
    studentgroup = instance.studentgroup
    content = f'There is a new comment in your group by {instance.user}'
    for student in studentgroup.students.all():
        Notification.objects.create(
            content=content,
            user=student,
            studentgroup=studentgroup,
        )


@receiver(post_delete, sender=Document)
def auto_delete_server_file_on_delete(sender, instance, **kwargs):
    if instance.file:
        if os.path.isfile(instance.file.path):
            os.remove(instance.file.path)
