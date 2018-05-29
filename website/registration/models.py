from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import pre_save

from ..thesis.models import StudentGroup
from .signals import remove_studentgroup_if_empty


class CutomUserManager(UserManager):
    def get_by_natural_key(self, username):
        case_insensitive_username_field = '{}__iexact'.format(
            self.model.USERNAME_FIELD)
        return self.get(**{case_insensitive_username_field: username})


class User(AbstractUser):
    first_name = models.CharField(_('first name'), max_length=30)
    last_name = models.CharField(_('last name'), max_length=150)
    email = models.EmailField(_('email address'))
    phone_number = models.CharField(_('phone number'), max_length=16)
    is_teacher = models.BooleanField(
        _('teacher status'),
        help_text=_(
            'Designates whether this user should be treated as teacher. '),
        default=False)
    studentgroup = models.ForeignKey(
        StudentGroup,
        related_name='students',
        on_delete=models.SET_NULL,
        null=True)
    objects = CutomUserManager()


# Signals
pre_save.connect(remove_studentgroup_if_empty, sender=User)
