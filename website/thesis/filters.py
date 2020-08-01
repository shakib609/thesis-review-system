from django.contrib import admin
from django.utils.translation import gettext_lazy as _


class CgpaOrderingFilter(admin.SimpleListFilter):
    _ASC = 'Ascending'
    _DESC = 'Descending'
    title = _('CGPA')

    parameter_name = 'cgpa'

    def lookups(self, request, model_admin):
        return (
            (self._ASC, _(self._ASC.title())),
            (self._DESC, _(self._DESC.title())),
        )

    def queryset(self, request, queryset):
        return queryset
