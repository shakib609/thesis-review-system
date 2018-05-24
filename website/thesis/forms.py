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
