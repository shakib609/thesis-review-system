from django.contrib import admin

from .models import (
    StudentGroup, Document, ResearchField)


admin.site.register(StudentGroup)
admin.site.register(Document)
admin.site.register(ResearchField)
