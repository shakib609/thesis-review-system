from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView

from .views import (
    UserCreateView,
    AboutView,
    LoginRedirectView,
    UserUpdateView,
    UserDeleteView,
    TeachersListView,
    TeacherDetailView,
    StudentDetailView,
    change_password,
    ReportPDFView,
)

app_name = 'registration'

urlpatterns = [
    path(
        '',
        LoginView.as_view(redirect_authenticated_user=True),
        name='login'),
    path(
        'logout/',
        LogoutView.as_view(next_page='/'),
        name='logout'),
    path(
        'register/',
        UserCreateView.as_view(),
        name='register'),
    path(
        'about/',
        AboutView.as_view(),
        name='about'),
    path(
        'redirect/',
        LoginRedirectView.as_view(),
        name='login_redirect'),
    path(
        'account/',
        UserUpdateView.as_view(),
        name='user_update'),
    path(
        'account/change-password/',
        change_password,
        name='change_password'),
    path(
        'delete/',
        UserDeleteView.as_view(),
        name='user_delete'),
    path(
        'teachers/',
        TeachersListView.as_view(),
        name='teacher_list'),
    path(
        'teachers/department/<str:department_name>/',
        TeachersListView.as_view(),
        name='teacher_list_department'),
    path(
        'teachers/<username>/',
        TeacherDetailView.as_view(),
        name='teacher_detail'),
    path(
        'students/<username>/',
        StudentDetailView.as_view(),
        name='student_detail'),
    path(
        'reports/<str:department>/<int:batch_id>/',
        ReportPDFView.as_view(),
        name='report_pdf'),
]
