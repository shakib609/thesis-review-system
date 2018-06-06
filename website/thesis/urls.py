from django.urls import path

from . import views


app_name = 'thesis'

urlpatterns = [
    path(
        '',
        views.AccountRedirectView.as_view(),
        name='account_redirect'),
    path(
        'group/',
        views.group_home,
        name='group_home'),
    path(
        'group/create_join/',
        views.GroupCreateJoinView.as_view(),
        name='group_create_join'),
    path(
        'group/create/',
        views.group_create,
        name='group_create'),
    path(
        'group/join/',
        views.group_join,
        name='group_join'),
    path(
        'group/upload/',
        views.DocumentUploadView.as_view(),
        name='document_upload'),
    path(
        'groups/',
        views.groups_home,
        name='groups_home'),
]
