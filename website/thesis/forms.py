from django import forms
from django.forms import formset_factory
import magic

from ..registration.models import (
    User,
    Mark,
)
from .models import (
    StudentGroup,
    Batch,
    Document,
    Comment,
    ResearchField,
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


class BaseMarkFormSet(forms.BaseFormSet):
    def clean(self):
        """Checks that no two mark has same student"""
        if any(self.errors):
            return
        students = set()
        for form in self.forms:
            student = form.cleaned_data.get('student')
            if student in students:
                raise forms.ValidationError(
                    "Students must be different for each form"
                )
            students.add(student)

    def save(self, commit=True):
        instances = []
        if self.is_valid():
            for form in self.forms:
                instances.append(form.save(commit=commit))
        return instances


class MarkForm(forms.ModelForm):
    class Meta:
        model = Mark
        fields = [
            'student',
            'mark',
            'remarks',
        ]

    def __init__(self, *args, user, studentgroup, **kwargs):
        self.user = user
        self.studentgroup = studentgroup
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'input'
            if visible.field.required:
                visible.field.widget.attrs['required'] = 'required'
            if visible.field.label == 'Student':
                visible.field.choices = [
                    (s.id, s) for s in studentgroup.students.all()
                ]

    def clean_mark(self):
        mark_limits = {
            'teacher': 50,
            'internal': 20,
            'external': 30,
        }
        mark = self.cleaned_data['mark']
        if self.user == self.studentgroup.teacher and mark > mark_limits['teacher']:
            raise forms.ValidationError(
                f'Mark is greater than limit({mark_limits["teacher"]})',
            )
        elif self.user == self.studentgroup.internal and mark > mark_limits['internal']:
            raise forms.ValidationError(
                f'Mark is greater than limit({mark_limits["internal"]})',
            )
        elif self.user == self.studentgroup.external and mark > mark_limits['external']:
            raise forms.ValidationError(
                f'Mark is greater than limit({mark_limits["external"]})',
            )
        return mark

    def save(self, commit=True):
        self.instance.graded_by = self.user
        self.instance.studentgroup = self.studentgroup
        return super().save(commit=commit)
