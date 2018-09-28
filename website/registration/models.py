from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import pre_save

import os

from ..thesis.models import StudentGroup
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
    def get_by_natural_key(self, username):
        case_insensitive_username_field = '{}__iexact'.format(
            self.model.USERNAME_FIELD)
        return self.get(**{case_insensitive_username_field: username})


class User(AbstractUser):
    full_name = models.CharField(_('full name'), max_length=180)
    email = models.EmailField(_('email address'))
    phone_number = models.CharField(_('phone number'), max_length=16)
    profile_picture = models.ImageField(
        upload_to=generate_propic_upload_location,
        null=True, blank=True)
    cv_document = models.FileField(
        upload_to=generate_cv_upload_location,
        null=True, blank=True)
    is_teacher = models.BooleanField(
        _('teacher status'),
        help_text=_(
            'Designates whether this user should be treated as teacher.'),
        default=False)
    studentgroup = models.ForeignKey(
        StudentGroup,
        related_name='students',
        on_delete=models.SET_NULL,
        null=True)
    objects = CutomUserManager()

    def get_full_name(self):
        return self.full_name


# Signals
pre_save.connect(remove_studentgroup_if_empty, sender=User)
