from rest_framework import serializers, exceptions
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate

from .models import User, Role, RoleType, Student, Teacher


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    roles = RoleSerializer(many=True)

    class Meta:
        model = User
        exclude = ['password']


class LoginSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    key = serializers.CharField(read_only=True)
    username = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Token
        fields = ['user', 'key', 'username', 'password']

    def create(self, validated_data):
        username = validated_data.pop('username')
        password = validated_data.pop('password')
        user = authenticate(username=username, password=password)
        if user is None:
            raise exceptions.AuthenticationFailed('Invalid Credentials')
        token = Token.objects.filter(user=user).first()
        if token:
            token.delete()
        return Token.objects.create(user=user)


class StudentSerializer(serializers.ModelSerializer):
    total_marks = serializers.IntegerField(read_only=True)

    class Meta:
        model = Student
        exclude = ['id', 'user', ]


class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        exclude = ['id', 'user', ]


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        exclude = ['roles', 'last_login', ]

    def _check_password(self, validated_data):
        if 'password' not in validated_data:
            raise exceptions.APIException(
                {'password': 'This field is required.'}
            )

    def create(self, validated_data):
        self._check_password(validated_data)
        password = validated_data['password']
        user = super().create(validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        user = super().update(instance, validated_data)
        if 'password' in validated_data:
            user.set_password(validated_data['password'])
            user.save()
        return user


class StudentCreateSerializer(UserRegistrationSerializer):
    student = StudentSerializer()

    def create(self, validated_data):
        student_validated_data = validated_data.pop('student', {})
        user = super().create(validated_data)
        user.roles.add(RoleType.STUDENT.value)
        Student.objects.create(user=user, **student_validated_data)
        return user

    def update(self, instance, validated_data):
        student_validated_data = validated_data.pop('student', {})
        user = super().update(instance, validated_data)
        # Updated related Student instance
        for attr, value in student_validated_data.items():
            setattr(user.student, attr, value)
        user.student.save()
        return user


class TeacherCreateSerializer(UserRegistrationSerializer):
    teacher = TeacherSerializer()

    def create(self, validated_data):
        teacher_validated_data = validated_data.pop('teacher', {})
        user = super().create(validated_data)
        user.roles.add(RoleType.TEACHER.value)
        Teacher.objects.create(user=user, **teacher_validated_data)
        return user

    def update(self, instance, validated_data):
        teacher_validated_data = validated_data.pop('teacher', {})
        user = super().update(instance, validated_data)
        # Updated related Teacher instance
        for attr, value in teacher_validated_data.items():
            setattr(user.teacher, attr, value)
        user.teacher.save()
        return user
