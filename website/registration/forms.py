from django import forms
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.forms import UserCreationForm
from django.utils.safestring import mark_safe
from django.contrib.auth import password_validation

from .models import User


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


class StudentSignUpForm(UserCreationForm):
    username = forms.CharField(
        max_length=8,
        label=_('Matric Number'),
        help_text=_('Required. Enter your Matric Number or ID.'))
    first_name = forms.CharField(
        max_length=30,
        label=_('First Name'),
        help_text=_('Required. Enter your first name.'))
    last_name = forms.CharField(
        max_length=30,
        label=_('Last Name'),
        help_text=_('Required. Enter your last name.'))
    email = forms.EmailField(
        max_length=254,
        label=_('E-mail'),
        help_text='Required. Enter a valid email address.')
    phone_number = forms.CharField(
        max_length=16,
        label=_('Phone Number'),
        help_text='Required. Enter your 11 digit phone number.')
    password1 = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput,
        help_text=mark_safe(
            password_validation.password_validators_help_text_html()),
    )

    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'email',
            'phone_number',
            'username',
            'password1',
            'password2',
        )

    def clean_username(self):
        username = self.cleaned_data.get("username").upper()
        return username
