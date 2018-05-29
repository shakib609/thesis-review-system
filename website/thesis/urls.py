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
        views.group_create_join,
        name='group_create_join'),
    path(
        'group/create/',
        views.create_studentgroup,
        name='create_studentgroup'),
    path(
        'group/join/',
        views.join_studentgroup,
        name='join_studentgroup'),
]
