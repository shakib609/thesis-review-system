from django import forms
import magic

from ..registration.models import User
from .models import (
    StudentGroup,
    Batch,
    Document,
    Comment,
    ResearchField
)


class StudentGroupForm(forms.ModelForm):
    field = forms.ModelChoiceField(
        queryset=ResearchField.objects.all(),
        required=True,
        empty_label=None,
    )
    teacher = forms.ModelChoiceField(
        queryset=User.objects.filter(is_teacher=True),
        required=False,
        empty_label=None,
    )
    batch = forms.ModelChoiceField(
        queryset=Batch.objects.all(),
        empty_label=None,
    )

    class Meta:
        model = StudentGroup
        fields = 'title', 'batch', 'field', 'teacher'


class StudentGroupJoinForm(forms.ModelForm):
    md5hash = forms.CharField(
        max_length=10,
        label='Group Code')

    class Meta:
        model = StudentGroup
        fields = ('md5hash', )

    def clean_md5hash(self):
        md5hash = self.cleaned_data.get('md5hash')
        if md5hash:
            g = StudentGroup.objects.filter(md5hash=md5hash).count()
            if g == 0:
                raise forms.ValidationError(
                    'The group with this code does not exist.'
                )
        return md5hash


class DocumentUploadForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ('file', 'document_type', )

    def clean_file(self):
        f = self.cleaned_data.get('file')
        for chunk in f.chunks():
            mime = magic.from_buffer(
                chunk, mime=True)
            break
        if 'application/pdf' not in mime:
            raise forms.ValidationError({'file': 'Invalid Format! PDF Only!'})
        return f


class CommentCreateForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
