from rest_framework import generics, viewsets
from rest_framework import serializers
from rest_framework.permissions import AllowAny

from users.models import Role, RoleType, User
from .permissions import (
    AdminOrOwnerUserOnly,
    AnonCreateAndUpdateOwnerOrAdminUserOnly,
    IsAdminOrReadOnly,
)
from .serializers import (
    LoginSerializer,
    RoleSerializer,
    TeacherCreateSerializer,
    StudentCreateSerializer,
)


class TeacherViewset(viewsets.ModelViewSet):
    serializer_class = TeacherCreateSerializer
    lookup_field = 'username'
    queryset = User.objects.filter(
        roles__id__in=[
            RoleType.TEACHER.value,
            RoleType.REVIEWER.value,
            RoleType.INTERNAL.value,
            RoleType.EXTERNAL.value,
        ]
    )
    # permission_classes = [AdminOrOwnerUserOnly]


class StudentViewset(viewsets.ModelViewSet):
    serializer_class = StudentCreateSerializer
    lookup_field = 'username'
    queryset = User.objects.filter(roles__id=RoleType.STUDENT.value)


class RoleViewset(viewsets.ReadOnlyModelViewSet):
    serializer_class = RoleSerializer
    queryset = Role.objects.all()
    # permission_classes = [IsAdminOrReadOnly]


class LoginAPI(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer


class RegistrationAPI(generics.CreateAPIView):
    serializer_class = StudentCreateSerializer
    # permission_classes = [AnonCreateAndUpdateOwnerOrAdminUserOnly]
