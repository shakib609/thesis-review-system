from django.urls import path

from . import views


app_name = 'thesis'

urlpatterns = [
    path(
        '',
        views.account_redirect,
        name='account_redirect'),
    path(
        'group/',
        views.group_home,
        name='group_home'),
    path(
        'group/create_join/',
        views.group_create_join,
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
        'groups/',
        views.groups_home,
        name='groups_home'),
]
