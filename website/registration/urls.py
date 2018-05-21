from django.urls import path
from django.contrib.auth.views import login, logout

from .views import register

app_name = 'registration'

urlpatterns = [
    path('', login, name='login'),
    path('register/', register, name='register'),
    path('logout/', logout, {'next_page': '/'}, name='logout'),
]
