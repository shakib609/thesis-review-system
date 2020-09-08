from django import forms
from django.forms.widgets import DateTimeInput
from django.shortcuts import get_object_or_404
import magic

from ..registration.models import (
    Student, User,
    Mark,
)
from .models import (
    Logbook, StudentGroup,
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
    batch = forms.ModelChoiceField(
        queryset=Batch.objects.all(),
        empty_label=None,
    )
    first_choice = forms.ModelChoiceField(
        queryset=User.objects.filter(is_teacher=True),
        required=True,
        empty_label=None,
    )
    second_choice = forms.ModelChoiceField(
        queryset=User.objects.filter(is_teacher=True),
        required=False,
    )
    third_choice = forms.ModelChoiceField(
        queryset=User.objects.filter(is_teacher=True),
        required=False,
    )

    def __init__(self, user, *args, **kwargs) -> None:
        self.user = user
        return super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        first_choice = cleaned_data['first_choice']
        second_choice = cleaned_data.get('second_choice')
        third_choice = cleaned_data.get('third_choice')
        if second_choice is None and third_choice is not None:
            raise forms.ValidationError({
                'second_choice': 'Must Select a second choice'
            })
        if first_choice == second_choice or first_choice == third_choice or (second_choice is not None and third_choice is not None and second_choice == third_choice):
            raise forms.ValidationError({
                'first_choice': 'Choices must be different',
                'second_choice': 'Choices must be different',
                'third_choice': 'Choices must be different',
            })

    def save(self, commit=True):
        self.instance.department = self.user.department
        return super().save(commit=commit)

    class Meta:
        model = StudentGroup
        fields = 'title', 'batch', 'field', 'first_choice', 'second_choice', 'third_choice'


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
            if 'application/pdf' not in mime:
                raise forms.ValidationError(
                    {'file': 'Invalid Format! PDF Only!'})
            break
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
            student = form.cleaned_data.get('student_choice')
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
    student_choice = forms.ChoiceField(
        label="Student",
        required=True,
    )
    mark = forms.IntegerField(
        label='Mark(Out of 100)',
        max_value=100,
        min_value=0,
    )

    class Meta:
        model = Mark
        fields = [
            'student_choice',
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
                visible.field.widget.attrs['required'] = ''
        self.fields['student_choice'].choices = [
            (s.id, s) for s in studentgroup.students.all()
        ]

    def save(self, commit=True):
        student_id = self.cleaned_data.pop('student_choice')
        student = get_object_or_404(Student, pk=student_id)
        self.instance.graded_by = self.user
        self.instance.studentgroup = self.studentgroup
        self.instance.student = student
        self.instance.result = student.result
        return super().save(commit=commit)


class LogbookAdminForm(forms.ModelForm):
    class Meta:
        model = Logbook
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'studentgroup' in self.initial:
            print(self.initial)
            self.fields['students_present'].queryset = User.objects.filter(
                studentgroup_id=self.initial['studentgroup'],
            )


class LogbookCreateForm(forms.ModelForm):
    time = forms.DateTimeField(input_formats=['%Y/%m/%d %H:%M'])

    class Meta:
        model = Logbook
        exclude = [
            'id',
            'studentgroup',
            'approved',
        ]

    def __init__(self, *args, studentgroup, **kwargs):
        self.studentgroup = studentgroup
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'input'
            print(dir(visible.field.widget))
            if getattr(visible.field.widget, 'allow_multiple_selected', None):
                visible.field.widget.attrs['style'] = 'min-height: 75px;'
            if not getattr(visible.field.widget, 'input_type', None):
                visible.field.widget.attrs['style'] = 'min-height: 90px;'
        self.fields['time'].widget.attrs['id'] = 'date-time-input'
        self.fields['students_present'].choices = [
            (s.id, s) for s in studentgroup.students.all()
        ]

    def save(self, commit=True):
        # student_id = self.cleaned_data.pop('students_present')
        # student = get_object_or_404(Student, pk=student_id)
        self.instance.studentgroup = self.studentgroup
        return super().save(commit=commit)
