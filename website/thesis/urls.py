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
        views.GroupHomeView.as_view(),
        name='group_home'),
    path(
        'group/create_join/',
        views.GroupCreateJoinView.as_view(),
        name='group_create_join'),
    path(
        'group/create/',
        views.GroupCreateView.as_view(),
        name='group_create'),
    path(
        'group/join/',
        views.GroupJoinView.as_view(),
        name='group_join'),
    path(
        'group/upload/',
        views.DocumentUploadView.as_view(),
        name='document_upload'),
    path(
        'groups/',
        views.GroupsHomeView.as_view(),
        name='groups_home'),
]
