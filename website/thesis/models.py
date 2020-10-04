from venv import create
from django.db import models
from django.conf import settings
from django.core import validators
from django.dispatch import receiver
from django.core.exceptions import ValidationError
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
    max_students_per_group = models.PositiveSmallIntegerField(default=2, validators=[
        validators.MinValueValidator(1),
    ])
    supervisor_mark_percentage = models.PositiveIntegerField(default=50, validators=[
        validators.MaxValueValidator(100),
        validators.MinValueValidator(0),
    ])
    internal_mark_percentage = models.PositiveIntegerField(default=30, validators=[
        validators.MaxValueValidator(100),
        validators.MinValueValidator(0),
    ])
    external_mark_percentage = models.PositiveIntegerField(default=20, validators=[
        validators.MaxValueValidator(100),
        validators.MinValueValidator(0),
    ])

    def clean(self):
        if sum([self.supervisor_mark_percentage, self.internal_mark_percentage, self.external_mark_percentage]) != 100:
            error_message = 'Sum of these must be 100'
            raise ValidationError({
                "supervisor_mark_percentage": error_message,
                "internal_mark_percentage": error_message,
                "external_mark_percentage": error_message,
            })

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
        verbose_name='Supervisor',
    )
    internal = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        default=None,
        related_name='internal_studentgroups',
        on_delete=models.SET_DEFAULT,
        limit_choices_to={"is_teacher": True},
        verbose_name='Reviewer',
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
    first_choice = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        related_name='first_choice_studentgroups',
        on_delete=models.SET_NULL,
        limit_choices_to={"is_teacher": True}
    )
    second_choice = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        related_name='second_choice_studentgroups',
        on_delete=models.SET_NULL,
        limit_choices_to={"is_teacher": True}
    )
    third_choice = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        related_name='third_choice_studentgroups',
        on_delete=models.SET_NULL,
        limit_choices_to={"is_teacher": True}
    )
    title = models.CharField(max_length=256)
    department = models.CharField(
        max_length=3,
        choices=DepartmentType.choices,
    )
    md5hash = models.CharField(max_length=10, null=True)
    progress = models.IntegerField(default=0)
    student_list = models.CharField(
        max_length=64,
        blank=True,
        validators=[
            validators.RegexValidator(
                r'(([A-Z]{1,2}\d{6})+)(,\s*([A-Z]{1,2}\d{6})+)*',
            ),
        ],
    )
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
    def max_cgpa(self):
        student = self.students.all().order_by('-cgpa').first()
        if student:
            return student.cgpa
        return 0

    @property
    def status(self):
        documents_queryset = self.documents.filter(is_accepted=True)
        if not self.approved:
            return 'Pending Admin Approval'
        elif documents_queryset.filter(document_type=Document.DocumentType.DEFENSE.value).exists():
            return 'Defense Done'
        elif documents_queryset.filter(document_type=Document.DocumentType.PRE_DEFENSE.value).exists():
            return 'Pre-Defense Done'
        elif documents_queryset.filter(document_type=Document.DocumentType.PROPOSAL.value).exists():
            return 'Proposal Done'
        else:
            return 'Supervisor Approved'

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


class Logbook(models.Model):
    class MeetingType(models.TextChoices):
        ON_SITE = "On-Site"
        ONLINE = "Online"

    studentgroup = models.ForeignKey(
        StudentGroup,
        on_delete=models.CASCADE,
        related_name='logbooks',
    )
    time = models.DateTimeField()
    meeting_type = models.CharField(
        max_length=7,
        choices=MeetingType.choices,
    )
    students_present = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        limit_choices_to={"is_student": True},
    )
    suggestions = models.TextField()
    topic_discussed = models.TextField()
    work_done_after_last_meeting = models.TextField()
    approved = models.BooleanField(default=False)

    class Meta:
        default_related_name = 'logbooks'

    def __str__(self) -> str:
        return f'{self.studentgroup} - {self.time}'


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
def generate_notification_on_document_upload(sender, instance, created, **kwargs):
    studentgroup = instance.studentgroup
    if created:
        content = f'A new Document({instance.document_type}) was uploaded to {studentgroup}'
        if studentgroup.approved:
            if studentgroup.teacher:
                Notification.objects.create(
                    content=content,
                    user=studentgroup.teacher,
                    studentgroup=studentgroup,
                )
            # if studentgroup.internal:
            #     Notification.objects.create(
            #         content=content,
            #         user=studentgroup.internal,
            #         studentgroup=studentgroup,
            #     )
            # if studentgroup.external:
            #     Notification.objects.create(
            #         content=content,
            #         user=studentgroup.external,
            #         studentgroup=studentgroup,
            #     )
    else:
        if instance.is_accepted:
            content = f'Your {instance.filename}({instance.document_type}) document was approved.'
        else:
            content = f'Your {instance.filename}({instance.document_type}) document was disapproved.'
        for student in studentgroup.students.all():
            Notification.objects.create(
                content=content,
                user=student,
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


@receiver(post_save, sender=Logbook)
def generate_notification_on_logbook_submission(sender, instance, created, **kwargs):
    if created:
        studentgroup = instance.studentgroup
        content = f'A new Log book(#{instance.id}) has been uploaded in {studentgroup}'
        if studentgroup.teacher:
            Notification.objects.create(
                content=content,
                user=studentgroup.teacher,
                studentgroup=studentgroup,
            )


@receiver(post_delete, sender=Document)
def auto_delete_server_file_on_delete(sender, instance, **kwargs):
    if instance.file:
        if os.path.isfile(instance.file.path):
            os.remove(instance.file.path)
