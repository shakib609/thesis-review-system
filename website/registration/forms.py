from django import forms
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.forms import UserCreationForm


class UserCreationFormExtended(UserCreationForm):
    is_teacher = forms.BooleanField(
        label=_('Teacher Status'),
        help_text=_('Designates whether this user should be treated as '
                    'a Teacher.'),
        required=False)

    def __init__(self, *args, **kwargs):
        super(UserCreationFormExtended, self).__init__(*args, **kwargs)

    def clean_username(self):
        username = self.cleaned_data.get("username").upper()
        return username
