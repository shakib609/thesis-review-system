from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _

from .models import User
from .forms import UserCreationFormExtended


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
            'profile_picture',
            'phone_number',
            'cv_document')
    }),
    (_('Permissions'), {
        'fields': ('is_staff', 'is_teacher')
    }),
    (_('Important dates'), {
        'fields': ('last_login', 'date_joined')
    }),
)

UserAdmin.list_display = ('username', 'is_teacher', 'full_name',)

UserAdmin.list_filter = ('is_teacher', 'is_superuser', 'is_active')

admin.site.unregister(Group)
admin.site.register(User, UserAdmin)
