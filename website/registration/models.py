from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


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
