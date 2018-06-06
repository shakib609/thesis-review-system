from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect


class UserStatusTestMixin(UserPassesTestMixin):
    def handle_no_permission(self):
        if self.raise_exception:
            raise PermissionDenied(self.get_permission_denied_message())
        return redirect('thesis:account_redirect')


class UserIsTeacherMixin(UserStatusTestMixin):
    def test_func(self):
        return self.request.user.is_teacher


class UserIsStudentMixin(UserStatusTestMixin):
    def test_func(self):
        return not self.request.user.is_teacher


class UserHasGroupMixin(UserStatusTestMixin):
    def test_func(self):
        return bool(self.request.user.studentgroup)
