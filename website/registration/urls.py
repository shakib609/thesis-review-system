from django.urls import path
from django.contrib.auth.views import login, logout

from .views import (
    UserCreateView,
    AboutView,
    LoginRedirectView,
    UserUpdateView,
    UserDeleteView,
)

app_name = 'registration'

urlpatterns = [
    path('', login, {'redirect_authenticated_user': True}, name='login'),
    path('register/', UserCreateView.as_view(), name='register'),
    path('logout/', logout, {'next_page': '/'}, name='logout'),
    path('about/', AboutView.as_view(), name='about'),
    path('redirect/', LoginRedirectView.as_view(), name='login_redirect'),
    path('account/', UserUpdateView.as_view(), name='user_update'),
    path('delete/', UserDeleteView.as_view(), name='user_delete'),
]
