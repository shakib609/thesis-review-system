from django.contrib import admin
from django.db.models import Max

from .models import (
    StudentGroup, Batch,  Document, ResearchField)


class DocumentInline(admin.StackedInline):
    model = Document
    extra = 0

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj) -> bool:
        return False


class StudentGroupAdmin(admin.ModelAdmin):
    list_filter = ('batch', 'approved',)
    list_display = (
        'title',
        'teacher',
        'internal',
        'external',
        'approved',
        'cgpa',
    )
    list_selected_related = ('batch', 'students')
    search_fields = ('title',)
    inlines = [DocumentInline]
    readonly_fields = ('first_choice', 'second_choice', 'third_choice',)
    fieldsets = (
        (None, {
            "fields": (
                'title',
                'field',
                'batch',
                'department',
                'teacher',
                'internal',
                'external',
                'first_choice',
                'second_choice',
                'third_choice',
                'approved',
            ),
        }),
    )

    def get_ordering(self, request):
        return ['-_cgpa']

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(_cgpa=Max('students__cgpa')).order_by('-_cgpa')

    def cgpa(self, obj):
        return '{:.2f}'.format(obj._cgpa)
    cgpa.admin_order_field = '_cgpa'


admin.site.register(Batch)
admin.site.register(ResearchField)
admin.site.register(StudentGroup, StudentGroupAdmin)
