from django import forms

from ..registration.models import User
from .models import StudentGroup


class StudentGroupForm(forms.ModelForm):
    teacher = forms.ModelChoiceField(
        queryset=User.objects.filter(is_teacher=True),
        required=False,
        empty_label='Select Teacher'
    )

    class Meta:
        model = StudentGroup
        fields = 'title', 'teacher'


class StudentGroupJoinForm(forms.ModelForm):
    md5hash = forms.CharField(
        max_length=10,
        label='Group Code')

    class Meta:
        model = StudentGroup
        fields = ('md5hash', )
