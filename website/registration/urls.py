from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView

from .views import (
    UserCreateView,
    AboutView,
    LoginRedirectView,
    UserUpdateView,
    UserDeleteView,
    TeachersListView
)

app_name = 'registration'

urlpatterns = [
    path('', LoginView.as_view(redirect_authenticated_user=True), name='login'),
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
    path('register/', UserCreateView.as_view(), name='register'),
    path('about/', AboutView.as_view(), name='about'),
    path('redirect/', LoginRedirectView.as_view(), name='login_redirect'),
    path('account/', UserUpdateView.as_view(), name='user_update'),
    path('delete/', UserDeleteView.as_view(), name='user_delete'),
    path('teachers/', TeachersListView.as_view(), name='teacher_list'),
]
