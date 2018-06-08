from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect, get_object_or_404
from django.utils.functional import cached_property

from .models import StudentGroup


class UserStatusTestMixin(UserPassesTestMixin):

    def handle_no_permission(self):
        if self.raise_exception:
            raise PermissionDenied(self.get_permission_denied_message())
        return redirect('registration:login_redirect')


class UserIsTeacherMixin(UserStatusTestMixin):
    """
    Mixin to check whether the User is a Teacher or not.
    """
    def test_func(self):
        return self.request.user.is_teacher


class UserIsStudentMixin(UserStatusTestMixin):
    """
    Mixin to check whether the User is a student or not.
    """

    def test_func(self):
        return not self.request.user.is_teacher


class UserHasGroupAccessMixin(UserStatusTestMixin):
    """
    Mixin to check whether the User has a group assigned or not.
    """

    def test_func(self):
        if self.request.user.is_teacher:
            return True
        else:
            return bool(self.request.user.studentgroup)


class StudentGroupContextMixin:
    """
    Mixin to add studentgroup to the context
    Must be used with UserHasGroupAccessMixin
    """

    @cached_property
    def studentgroup(self):
        user = self.request.user
        studentgroup = user.studentgroup
        if user.is_teacher:
            group_code = self.kwargs.get('group_code')
            studentgroup = get_object_or_404(StudentGroup, md5hash=group_code)
        return studentgroup

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['studentgroup'] = self.studentgroup
        return context
