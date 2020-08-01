from django.contrib import admin
from django.db.models import Count
from django.utils.translation import gettext_lazy as _


class ResultReadinessFilter(admin.SimpleListFilter):
    _READY = 'READY'
    _UNREADY = 'UNREADY'
    title = _('Result Readiness')

    parameter_name = 'ready'

    def lookups(self, request, model_admin):
        return (
            (self._READY, _(self._READY.title())),
            (self._UNREADY, _(self._UNREADY.title())),
        )

    def queryset(self, request, queryset):
        annotated_queryset = queryset.annotate(marks_count=Count('marks'))
        options = {}
        if self.value() == self._READY:
            options.update({'marks_count': 3})
        elif self.value() == self._UNREADY:
            options.update({'marks_count__lt': 3})
        return annotated_queryset.filter(**options)
