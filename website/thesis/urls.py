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
        'create/field/<field_id>/teachers/',
        views.get_teachers_list_by_field_json,
        name='get_teachers'
    ),
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
        'update/',
        views.GroupUpdateView.as_view(),
        name='group_update'),
    path(
        'list/',
        views.GroupListView.as_view(),
        name='group_list'),
    path(
        'list/<int:batch_number>/',
        views.GroupListView.as_view(),
        name='group_list_batch'),
    path(
        'notifications/',
        views.NotificationListView.as_view(),
        name='user_notifications'),
    path(
        '<group_code>/',
        views.DocumentListView.as_view(),
        name='group_detail'),
    path(
        'comment/create/',
        views.CommentCreateView.as_view(),
        name='comment_create'
    ),
    path(
        '<group_code>/comment/create/',
        views.CommentCreateView.as_view(),
        name='comment_create_teacher'
    ),
    path(
        '<group_code>/approve/',
        views.StudentGroupApproveView.as_view(),
        name='group_approve'
    ),
    path(
        '<group_code>/update_progress/',
        views.StudentGroupProgressUpdateView.as_view(),
        name='progress_update'
    ),
]
