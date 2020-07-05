from django.db import models
from django.core.mail import send_mail
from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

from users.utils import (
    generate_cv_upload_location,
    generate_propic_upload_location,
)


class RoleType(models.IntegerChoices):
    ADMIN = 1
    STUDENT = 2
    TEACHER = 3
    REVIEWER = 4
    INTERNAL = 5
    EXTERNAL = 6


class Role(models.Model):
    name = models.CharField(max_length=16)

    class Meta:
        db_table = 'tbl_role'

    def __str__(self):
        return self.name


class UserManager(BaseUserManager):

    def _create_user(self, username, email, password, **extra_fields):
        """
        Create and save a user with the given username, email, and password.
        """
        if not username:
            raise ValueError('The given username must be set')
        email = self.normalize_email(email)
        username = self.model.normalize_username(username)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        user = self._create_user(
            username,
            email=email,
            password=password,
            **extra_fields,
        )
        user.roles.add(RoleType.ADMIN.value)
        return user


class User(AbstractBaseUser):
    class DepartmentType(models.TextChoices):
        CSE = 'CSE'
        EEE = 'EEE'
        ETE = 'ETE'
        PHM = 'PHM'

    username = models.CharField(
        max_length=16,
        primary_key=True,
        validators=[
            RegexValidator(r'^[A-Z\d_]+$'),
        ]
    )
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=32, blank=True)
    last_name = models.CharField(max_length=32, blank=True)
    phone_number = models.CharField(max_length=16, blank=True)
    profile_picture = models.ImageField(
        upload_to=generate_propic_upload_location,
        blank=True,
    )
    cv_document = models.FileField(
        upload_to=generate_cv_upload_location,
        blank=True,
    )
    department = models.CharField(
        max_length=3,
        blank=True,
        choices=DepartmentType.choices
    )
    roles = models.ManyToManyField(
        Role,
        related_name='users',
    )

    objects = UserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        db_table = 'tbl_user'

    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'.strip()

    def email_user(self, subject, message, from_email=None, **kwargs):
        send_mail(subject, message, from_email, [self.email], **kwargs)

    def __str__(self):
        return self.username


class Student(models.Model):
    total_marks = models.PositiveIntegerField(default=0)
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='student',
    )
    group = models.ForeignKey(
        'groups.Group',
        on_delete=models.SET_NULL,
        null=True,
    )

    class Meta:
        db_table = 'tbl_student'
        default_related_name = 'students'

    def __str__(self):
        return f'Student - {self.user.username}'


class Teacher(models.Model):
    designation = models.CharField(
        max_length=256,
        null=True,
        blank=True,
    )
    qualification = models.CharField(
        max_length=512,
        null=True,
        blank=True,
    )
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='teacher',
    )

    class Meta:
        db_table = 'tbl_teacher'
        default_related_name = 'teachers'

    def __str__(self):
        return f'Teacher - {self.user.username}'


class Notification(models.Model):
    text = models.TextField()
    is_viewed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    group = models.ForeignKey(
        'groups.Group',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    class Meta:
        db_table = "tbl_notification"
        default_related_name = 'notifications'
        ordering = ['-created_at']

    def __str__(self):
        return self.text[:15]
