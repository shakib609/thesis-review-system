from django.contrib import admin
from django.db.models import Max
from django.contrib.admin.views.main import ChangeList

from .filters import CgpaOrderingFilter
from .models import (
    StudentGroup, Batch,  Document, ResearchField)


class DocumentInline(admin.StackedInline):
    model = Document
    extra = 0

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj) -> bool:
        return False


class StudentGroupChangeList(ChangeList):
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        existing_ordering = [
            order for order in queryset.query.order_by
        ]

        print(existing_ordering)
        queryset = queryset.order_by()
        query_param = request.GET.get('cgpa')
        if query_param == 'Ascending':
            return queryset.order_by('_cgpa', *existing_ordering)
        elif query_param == 'Descending':
            return queryset.order_by('-_cgpa', *existing_ordering)
        return queryset


class StudentGroupAdmin(admin.ModelAdmin):
    list_filter = ('batch', 'approved', CgpaOrderingFilter, 'field',)
    list_display = (
        'title',
        'approved',
        'teacher',
        'internal',
        'external',
        'max_cgpa',
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

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            _cgpa=Max('students__cgpa'),
        )

    def get_changelist(self, request, **kwargs):
        return StudentGroupChangeList


admin.site.register(Batch)
admin.site.register(ResearchField)
admin.site.register(StudentGroup, StudentGroupAdmin)
