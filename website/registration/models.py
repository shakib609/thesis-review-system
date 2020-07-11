from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import pre_save

import os

from .signals import remove_studentgroup_if_empty


def generate_propic_upload_location(instance, filename):
    _, extension = os.path.splitext(filename)
    return 'profile_pictures/{}/propic{}'.format(
        instance.username, extension)


def generate_cv_upload_location(instance, filename):
    _, extension = os.path.splitext(filename)
    return 'cvs/{}/cv{}'.format(
        instance.username, extension)


class CutomUserManager(UserManager):
    pass


class DepartmentType(models.TextChoices):
    CSE = 'CSE'
    EEE = 'EEE'
    ETE = 'ETE'
    PHM = 'PHM'


class User(AbstractUser):
    objects = CutomUserManager()

    full_name = models.CharField(max_length=180)
    email = models.EmailField(blank=True)
    phone_number = models.CharField(max_length=16, blank=True)

    department = models.CharField(
        max_length=3,
        choices=DepartmentType.choices,
        default=DepartmentType.CSE.value,
    )

    # Only for teachers
    designation = models.CharField(
        _('designation'), max_length=256,
        null=True, blank=True)
    qualification = models.CharField(
        _('qualification'), max_length=512, null=True, blank=True)
    profile_picture = models.ImageField(
        upload_to=generate_propic_upload_location,
        null=True, blank=True)
    cv_document = models.FileField(
        upload_to=generate_cv_upload_location,
        null=True, blank=True)
    is_teacher = models.BooleanField(
        _('teacher status'),
        help_text=_(
            'Designates whether this user should be treated as teacher.'
        ),
        default=False,
    )
    is_student = models.BooleanField(
        _('student status'),
        help_text=_(
            'Designates whether this user should be treated as student.'),
        default=False,
    )
    studentgroup = models.ForeignKey(
        'thesis.StudentGroup',
        related_name='students',
        on_delete=models.SET_NULL,
        null=True)
    
    def __str__(self):
        if self.full_name:
            return f'{self.full_name} - {self.username}'
        return self.username


class Student(User):
    class Meta:
        proxy = True


class Teacher(User):
    class Meta:
        proxy = True


class Admin(User):
    class Meta:
        proxy = True


# Signals
pre_save.connect(remove_studentgroup_if_empty, sender=User)
