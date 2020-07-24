from django import forms
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError

import re

from .models import User
from ..thesis.models import ResearchField


class UserCreationFormExtended(UserCreationForm):
    is_teacher = forms.BooleanField(
        label=_('Teacher Status'),
        help_text=_('Designates whether this user should be treated as '
                    'a Teacher.'),
        required=False)

    def clean_username(self):
        return self.cleaned_data.get("username")


class TeacherCreateForm(UserCreationForm):
    full_name = forms.CharField(max_length=180)
    designation = forms.CharField(max_length=256, required=False)
    qualification = forms.CharField(max_length=512, required=False)


class StudentSignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = (
            'username',
            'department',
            'full_name',
            'email',
            'phone_number',
            'cgpa',
            'password1',
            'password2',
        )

    def clean_username(self):
        regex = re.compile(r'\w+[0-9]{6}')
        username = self.cleaned_data.get("username").upper()
        m = regex.match(username)
        if not m:
            raise ValidationError('Invalid ID')
        return username


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = (
            'full_name',
            'email',
            'phone_number',
            'username',
            'profile_picture',
            'cgpa',
        )


class TeacherUpdateForm(forms.ModelForm):
    research_fields = forms.ModelMultipleChoiceField(
        queryset=ResearchField.objects.all(),
        widget=forms.widgets.CheckboxSelectMultiple,
        required=False,
    )

    class Meta:
        model = User
        fields = (
            'full_name',
            'profile_picture',
            'email',
            'phone_number',
            'username',
            'designation',
            'qualification',
            'cv_document',
        )

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance')
        if instance:
            kwargs.update(initial={
                'research_fields': [field.id for field in instance.fields.all()]
            })
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super().save(commit=False)
        research_fields = self.cleaned_data.get('research_fields')
        instance.fields.clear()
        instance.fields.add(*research_fields)
        if commit:
            instance.save()
        return instance
