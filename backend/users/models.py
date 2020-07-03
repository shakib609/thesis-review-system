from django.db import models
from django.core.mail import send_mail
from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractBaseUser

from thesis.models import ThesisGroup
from users.utils import (
    generate_cv_upload_location,
    generate_propic_upload_location,
)


class Role(models.Model):
    class RoleType(models.IntegerChoices):
        ADMIN = 1
        STUDENT = 2
        TEACHER = 3
        REVIEWER = 4
        INTERNAL = 5
        EXTERNAL = 6

    id = models.PositiveSmallIntegerField(
        primary_key=True,
        choices=RoleType.choices,
    )

    def __str__(self):
        for k, v in self.RoleType.choices:
            if k == self.id:
                return v
        return 'Unknown Role'


class User(AbstractBaseUser):
    class DepartmentType(models.TextChoices):
        CSE = 'CSE'
        EEE = 'EEE'
        ETE = 'ETE'
        PHM = 'PHM'

    username = models.CharField(
        max_length=16,
        primary_key=True,
        validators=[
            RegexValidator(r'^[A-Z\d_]+$'),
        ]
    )
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=32, blank=True)
    last_name = models.CharField(max_length=32, blank=True)
    phone_number = models.CharField(max_length=16, blank=True)
    profile_picture = models.ImageField(
        upload_to=generate_propic_upload_location,
        blank=True,
    )
    cv_document = models.FileField(
        upload_to=generate_cv_upload_location,
        blank=True,
    )
    department = models.CharField(
        max_length=3,
        blank=True,
        choices=DepartmentType.choices
    )
    roles = models.ManyToManyField(
        Role,
        related_name='users',
    )

    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'.strip()

    def email_user(self, subject, message, from_email=None, **kwargs):
        send_mail(subject, message, from_email, [self.email], **kwargs)

    def __str__(self):
        return self.username


class Student(models.Model):
    total_marks = models.PositiveIntegerField(default=0)
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
    )
    thesis_group = models.ForeignKey(
        ThesisGroup,
        on_delete=models.SET_NULL,
        null=True,
    )

    class Meta:
        default_related_name = 'students'

    def __str__(self):
        return f'Student {self.user.username}'


class Teacher(models.Model):
    designation = models.CharField(
        max_length=256,
        null=True,
        blank=True,
    )
    qualification = models.CharField(
        max_length=512,
        null=True,
        blank=True,
    )
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return f'Teacher - {self.user.username}'
