from django.contrib import admin

from .models import (
    StudentGroup, Batch,  Document, ResearchField)


class DocumentInline(admin.StackedInline):
    model = Document
    extra = 0


class StudentGroupAdmin(admin.ModelAdmin):
    list_filter = ('batch', 'approved', )
    list_display = ('title', 'teacher', 'internal', 'external', 'approved',)
    inlines = [DocumentInline]


admin.site.register(Batch)
admin.site.register(ResearchField)
admin.site.register(StudentGroup, StudentGroupAdmin)
