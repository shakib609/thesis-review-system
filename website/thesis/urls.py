from django.urls import path

from . import views


app_name = 'thesis'

urlpatterns = [
    path(
        'group/create/',
        views.create_studentgroup,
        name='create_studentgroup')
]
