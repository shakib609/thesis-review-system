from django.urls import path
from rest_framework.routers import SimpleRouter

from . import views

app_name = 'users'

router = SimpleRouter()
router.register('teachers', views.TeacherViewset)
router.register('students', views.StudentViewset)
router.register('roles', views.RoleViewset)

urlpatterns = router.urls + [
    path(
        'login/',
        views.LoginAPI.as_view(),
        name='login-api',
    ),
    path(
        'register/',
        views.RegistrationAPI.as_view(),
        name='registration-api',
    ),
]
