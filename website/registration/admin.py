from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _

from .models import User, Student, Teacher, Admin
from .forms import UserCreationFormExtended, TeacherCreateForm


UserAdmin.add_form = UserCreationFormExtended

UserAdmin.add_fieldsets = (('User Info', {
    'classes': ('wide', ),
    'fields': (
        'username',
        'email',
        'phone_number',
        'password1',
        'password2',
    )
}), ('Permissions', {
    'classes': ('wide', ),
    'fields': ('is_teacher', )
}))

UserAdmin.fieldsets = fieldsets = (
    (None, {
        'fields': ('username', 'password')
    }),
    (_('Personal info'), {
        'fields': (
            'full_name',
            'email',
            'phone_number',
            'profile_picture',
            'cv_document',
            'qualification',
            'designation',)
    }),
    (_('Permissions'), {
        'fields': ('is_teacher', 'is_student', 'is_staff', 'is_superuser',)
    }),
    (_('Important dates'), {
        'fields': ('last_login', 'date_joined')
    }),
)

UserAdmin.list_display = ('username', 'is_teacher', 'full_name',)

UserAdmin.list_filter = ('is_teacher', 'is_superuser', 'is_active')


class StudentAdmin(UserAdmin):
    list_display = ('username', 'full_name', 'email', 'phone_number',)
    list_filter = ('is_active', 'department', )
    search_fields = ('username', 'full_name')
    add_fieldsets = (
        (
            'Student Info',
            {
                'classes': ('wide', ),
                'fields': (
                    'username',
                    'email',
                    'full_name',
                    'phone_number',
                    'password1',
                    'password2',
                    'profile_picture',
                    'cv_document',
                )
            }
        ),
    )
    fieldsets = (
        (None, {
            'fields': ('username', 'password')
        }),
        (_('Personal info'), {
            'fields': (
                'full_name',
                'email',
                'phone_number',
                'profile_picture',
                'cv_document',
            )
        }),
        (_('Important dates'), {
            'fields': ('last_login', 'date_joined')
        }),
    )

    def get_queryset(self, request):
        return User.objects.filter(
            is_teacher=False,
            is_superuser=False,
            is_staff=False,
        )

    def save_model(self, request, obj, form, change):
        obj.is_student = True
        return super().save_model(request, obj, form, change)


class TeacherAdmin(UserAdmin):
    list_display = ('username', 'full_name', 'email', 'designation',)
    list_filter = ('is_superuser', 'department',)
    search_fields = ('username', 'full_name')
    add_fieldsets = (
        (
            'Teacher Info',
            {
                'classes': ('wide', ),
                'fields': (
                    'username',
                    'email',
                    'full_name',
                    'phone_number',
                    'password1',
                    'password2',
                    'profile_picture',
                    'cv_document',
                    'designation',
                    'qualification',
                )
            }
        ),
    )
    fieldsets = (
        (None, {
            'fields': ('username', 'password')
        }),
        (_('Personal info'), {
            'fields': (
                'full_name',
                'email',
                'phone_number',
                'profile_picture',
                'cv_document',
                'designation',
                'qualification',
            )
        }),
        (_('Important dates'), {
            'fields': ('last_login', 'date_joined')
        }),
    )

    def get_queryset(self, request):
        return User.objects.filter(is_teacher=True)

    def save_model(self, request, obj, form, change):
        obj.is_teacher = True
        return super().save_model(request, obj, form, change)


class AdminAdmin(UserAdmin):
    list_display = ('username',)
    search_fields = ('username', 'full_name')
    add_fieldsets = (
        (
            'Admin Info',
            {
                'classes': ('wide', ),
                'fields': (
                    'username',
                    'email',
                    'password1',
                    'password2',
                )
            }
        ),
    )
    fieldsets = (
        (None, {
            'fields': ('username', 'password')
        }),
        (_('Personal info'), {
            'fields': (
                'full_name',
                'email',
                'phone_number',
                'profile_picture',
            )
        }),
        (_('Important dates'), {
            'fields': ('last_login', 'date_joined')
        }),
    )

    def get_queryset(self, request):
        return User.objects.filter(is_superuser=True)

    def save_model(self, request, obj, form, change):
        obj.is_superuser = True
        obj.is_staff = True
        return super().save_model(request, obj, form, change)


admin.site.unregister(Group)
# admin.site.register(User, UserAdmin)
admin.site.register(Admin, AdminAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(Teacher, TeacherAdmin)
