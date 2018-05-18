from django.urls import path
from django.contrib.auth.views import login, logout

from .views import register

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', login, name='login'),
    path('logout/', logout, name='logout'),
]
