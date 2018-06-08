from django.urls import path

from . import views


app_name = 'thesis'

urlpatterns = [
    path(
        'documents/',
        views.DocumentListView.as_view(),
        name='document_list'),
    path(
        'create_join/',
        views.GroupCreateJoinView.as_view(),
        name='group_create_join'),
    path(
        'create/',
        views.GroupCreateView.as_view(),
        name='group_create'),
    path(
        'join/',
        views.GroupJoinView.as_view(),
        name='group_join'),
    path(
        'upload/',
        views.DocumentUploadView.as_view(),
        name='document_upload'),
    path(
        'invite/',
        views.GroupInviteView.as_view(),
        name='group_invite'),
    path(
        'list/',
        views.GroupListView.as_view(),
        name='group_list'),
    path(
        '<group_code>/',
        views.DocumentListView.as_view(),
        name='group_detail'),
]
