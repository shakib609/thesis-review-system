from django.db import models
from django.db.models import Value, Case, When, Sum, F
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

import os


def generate_propic_upload_location(instance, filename):
    _, extension = os.path.splitext(filename)
    return 'profile_pictures/{}/propic{}'.format(
        instance.username, extension)


def generate_cv_upload_location(instance, filename):
    _, extension = os.path.splitext(filename)
    return 'cvs/{}/cv{}'.format(
        instance.username, extension)


class DepartmentType(models.TextChoices):
    CSE = 'CSE'
    EEE = 'EEE'
    ETE = 'ETE'
    PHM = 'PHM'


class User(AbstractUser):
    full_name = models.CharField(max_length=180)
    email = models.EmailField(blank=True)
    phone_number = models.CharField(max_length=16, blank=True)

    department = models.CharField(
        max_length=3,
        choices=DepartmentType.choices,
        default=DepartmentType.CSE.value,
    )

    # Only for teachers
    designation = models.CharField(
        _('designation'),
        max_length=256,
        null=True,
        blank=True,
    )
    qualification = models.CharField(
        _('qualification'),
        max_length=512,
        null=True,
        blank=True,
    )
    profile_picture = models.ImageField(
        upload_to=generate_propic_upload_location,
        null=True,
        blank=True,
    )
    cv_document = models.FileField(
        upload_to=generate_cv_upload_location,
        null=True,
        blank=True,
    )
    is_teacher = models.BooleanField(
        _('teacher status'),
        help_text=_(
            'Designates whether this user should be treated as teacher.'
        ),
        default=False,
    )
    is_external = models.BooleanField(
        _('external teacher status'),
        help_text=_(
            'Designates whether this teacher should be treated as an external teacher.'
        ),
        default=False,
    )
    cgpa = models.DecimalField(
        null=True,
        blank=True,
        decimal_places=2,
        max_digits=5,
    )
    is_student = models.BooleanField(
        _('student status'),
        help_text=_(
            'Designates whether this user should be treated as student.'),
        default=False,
    )
    is_superuser = models.BooleanField(
        _('Admin'),
        help_text=_(
            'Designates whether this user should be treated as admin.'),
        default=False,
    )
    studentgroup = models.ForeignKey(
        'thesis.StudentGroup',
        related_name='students',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    def studentgroup_count_by_batch(self, batch):
        return self.studentgroups.filter(
            approved=True,
            batch=batch,
        ).count()

    def __str__(self):
        name = self.username
        if self.full_name:
            name += f' - {self.full_name}'
        return name


class Student(User):
    class Meta:
        proxy = True
        verbose_name = 'student'


class Teacher(User):
    class Meta:
        proxy = True


class Admin(User):
    class Meta:
        proxy = True


class Result(models.Model):
    total_marks = models.DecimalField(
        default=0,
        max_digits=6,
        decimal_places=2,
    )
    student = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={"is_student": True}
    )

    def __str__(self) -> str:
        return f'{self.student.username} Result'

    @property
    def grade(self):
        if self.total_marks < 40:
            return 'F'
        elif self.total_marks < 45:
            return 'D'
        elif self.total_marks < 50:
            return 'C'
        elif self.total_marks < 55:
            return 'C+'
        elif self.total_marks < 60:
            return 'B-'
        elif self.total_marks < 65:
            return 'B'
        elif self.total_marks < 70:
            return 'B+'
        elif self.total_marks < 75:
            return 'A-'
        elif self.total_marks < 80:
            return 'A'
        else:
            return 'A+'


class Mark(models.Model):
    mark = models.PositiveSmallIntegerField()
    remarks = models.TextField(blank=True)
    studentgroup = models.ForeignKey(
        'thesis.StudentGroup',
        on_delete=models.CASCADE,
    )
    graded_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'is_teacher': True},
        related_name='graded_by_marks',
    )
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'is_student': True},
        related_name='student_marks',
    )

    class Meta:
        default_related_name = 'marks'
        unique_together = ['studentgroup', 'graded_by', 'student']

    def clean(self):
        try:
            group = self.studentgroup
            if self.student not in group.students.all():
                raise ValidationError("Invalid Student")
            elif self.graded_by != group.teacher and self.graded_by != group.internal and self.graded_by != group.external:
                raise ValidationError("Invalid Teacher")
        except Exception:
            pass

    def __str__(self):
        return f'{self.student} - {self.graded_by} - {self.mark}'


@receiver(pre_save, sender=User)
def remove_studentgroup_if_empty(sender, instance, **kwargs):
    if instance.id:
        old_user = User.objects.get(pk=instance.id)
        if old_user.studentgroup:
            old_s = old_user.studentgroup
            if old_s.students.count() == 1:
                if old_s != instance.studentgroup:
                    old_s.delete()


@receiver(post_save, sender=User)
def create_result_on_student_creation(sender, instance, **kwargs):
    if instance.is_student and not Result.objects.filter(student=instance).exists():
        Result.objects.create(student=instance)


@receiver(post_save, sender=Mark)
def update_result_on_mark_edit(sender, instance, **kwargs):
    student = instance.student
    studentgroup = instance.studentgroup
    result = Result.objects.filter(student=student).first()
    if result:
        result_marks = student.student_marks.annotate(
            _processed_mark=Case(
                When(
                    graded_by=studentgroup.teacher,
                    then=F(
                        'mark') * (studentgroup.batch.supervisor_mark_percentage / 100)
                ),
                When(
                    graded_by=studentgroup.internal,
                    then=F(
                        'mark') * (studentgroup.batch.internal_mark_percentage / 100)
                ),
                When(
                    graded_by=studentgroup.external,
                    then=F(
                        'mark') * (studentgroup.batch.external_mark_percentage / 100)
                ),
                default=Value('mark'),
                output_field=models.DecimalField(),
            )
        ).aggregate(
            total_marks=Sum('_processed_mark')
        )
        print(result_marks)
        result.total_marks = result_marks['total_marks']
        result.save()
