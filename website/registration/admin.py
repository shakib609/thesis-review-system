from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _

from .filters import ResultReadinessFilter
from .forms import (
    UserCreationFormExtended,
    AdminTeacherChangeForm,
    AdminTeacherCreateForm,
)
from .models import User, Student, Teacher, Admin, Result, Mark


class CustomUserAdmin(UserAdmin):
    add_form = UserCreationFormExtended
    list_display = ('username', 'full_name', 'email',)
    list_filter = ('is_active',)
    add_fieldsets = (
        (
            'User Info',
            {
                'classes': ('wide', ),
                'fields': (
                    'username',
                    'email',
                    'phone_number',
                    'password1',
                    'password2',
                )
            }
        ),
        (
            'Permissions',
            {
                'classes': ('wide', ),
                'fields': ('is_teacher', 'is_superuser', )
            },
        )
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
            )
        }),
        (_('Permissions'), {
            'fields': ('is_teacher', 'is_superuser',)
        }),
    )


class ResultInline(admin.TabularInline):
    model = Result


class MarkInline(admin.StackedInline):
    model = Mark
    extra = 0
    fields = ['student', 'mark', 'graded_by', 'remarks', ]
    fk_name = 'student'
    readonly_fields = ['graded_by', 'remarks', ]


class MarkInlineResult(MarkInline):
    fk_name = 'result'
    fields = ['mark', 'graded_by', 'remarks', ]


class ResultAdmin(admin.ModelAdmin):
    list_display = ['student', 'total_marks', 'grade', ]
    search_fields = ['student__username', 'student']
    change_list_template = 'admin/result_change_list.html'
    list_filter = [
        ResultReadinessFilter,
        'student__department',
        'student__studentgroup__batch',
    ]
    inlines = [MarkInlineResult]

    def get_queryset(self, request):
        return Result.objects.exclude(
            student__studentgroup=None,
        ).order_by('student__username')

    def has_add_permission(self, request) -> bool:
        return False

    # def has_delete_permission(self, request, obj=None) -> bool:
    #     return False


class StudentAdmin(UserAdmin):
    list_display = ('username', 'full_name', 'email', 'phone_number', 'cgpa',)
    list_filter = ('is_active', 'department', 'studentgroup__batch',)
    search_fields = ('username', 'full_name')
    change_list_template = 'admin/student_change_list.html'
    inlines = [MarkInline, ResultInline]
    raw_id_fields = ['studentgroup']
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
                    'department',
                    'profile_picture',
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
                'department',
                'profile_picture',
            )
        }),
        (_('Thesis/Project Group'), {
            'fields': (
                'studentgroup',
            )
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
    form = AdminTeacherChangeForm
    add_form = AdminTeacherCreateForm
    list_display = ('username', 'full_name', 'email', 'designation',)
    list_filter = ('is_external', 'department',)
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
                    'department',
                    'profile_picture',
                    'cv_document',
                    'designation',
                    'qualification',
                )
            }
        ),
        (
            'Permission',
            {
                'classes': ('wide', ),
                'fields': (
                    'is_external',
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
                'department',
                'designation',
                'qualification',
                'cv_document',
            )
        }),
        (
            'Permission',
            {
                'classes': ('wide', ),
                'fields': (
                    'is_external',
                    'is_superuser',
                )
            }
        ),
    )

    def get_queryset(self, request):
        return User.objects.filter(is_teacher=True)

    def save_model(self, request, obj, form, change):
        obj.is_teacher = True
        return super().save_model(request, obj, form, change)


class AdminAdmin(UserAdmin):
    list_display = ('username',)
    search_fields = ('username', 'full_name')
    list_filter = ('is_active', )
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
            )
        }),
    )

    def get_queryset(self, request):
        return User.objects.filter(is_superuser=True)

    def save_model(self, request, obj, form, change):
        obj.is_superuser = True
        obj.is_staff = True
        return super().save_model(request, obj, form, change)


admin.site.unregister(Group)
admin.site.register(User, CustomUserAdmin)
admin.site.register(Admin, AdminAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(Teacher, TeacherAdmin)
admin.site.register(Result, ResultAdmin)
