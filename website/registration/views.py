from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import (
    TemplateView,
    CreateView,
    RedirectView,
    UpdateView,
    ListView,
    DetailView
)
from django.http import HttpResponseRedirect, Http404
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Count
from django.shortcuts import get_object_or_404

from .forms import (
    StudentSignUpForm, UserUpdateForm, TeacherUpdateForm)
from .models import User


class LoginRedirectView(LoginRequiredMixin, RedirectView):
    http_method_names = ['get']

    def get_redirect_url(self, *args, **kwargs):
        request = self.request
        if request.user.is_teacher:
            return reverse_lazy('thesis:group_list')
        if request.user.studentgroup:
            return reverse_lazy('thesis:document_list')
        return reverse_lazy('thesis:group_create_join')


class AboutView(TemplateView):
    http_method_names = ['get']
    template_name = 'registration/about.html'


class UserCreateView(CreateView):
    model = User
    template_name = 'registration/user_create.html'
    form_class = StudentSignUpForm
    success_url = reverse_lazy('registration:login_redirect')
    http_method_names = ['get', 'post']

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect(self.get_success_url())
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        messages.success(
            self.request,
            'User Created Successfully!',
            extra_tags='is-success')
        return response


class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = "registration/user_update.html"
    http_method_names = ['get', 'post']
    success_url = reverse_lazy('registration:login_redirect')

    def get_form_class(self):
        if self.request.user.is_teacher:
            return TeacherUpdateForm
        else:
            return UserUpdateForm

    def get_object(self, *args, **kwargs):
        return self.request.user

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            'Update Successful!',
            extra_tags='is-success')
        return response


class UserDeleteView(LoginRequiredMixin, TemplateView):
    template_name = "registration/user_delete.html"
    http_method_names = ['get', 'post']

    def post(self, request, *args, **kwargs):
        user = self.request.user
        user.delete()
        messages.success(
            request,
            'Account deleted successfully!',
            extra_tags='is-success')
        return HttpResponseRedirect(reverse_lazy('registration:login'))


class TeachersListView(LoginRequiredMixin, ListView):
    template_name = 'registration/teacher_list.html'
    context_object_name = 'teachers'

    def get_queryset(self):
        queryset = User.objects.annotate(
            group_count=Count('studentgroups')).filter(
                is_teacher=True).order_by('-group_count', 'full_name')
        return queryset


class TeacherDetailView(LoginRequiredMixin, DetailView):
    context_object_name = 'teacher'
    template_name = 'registration/teacher_detail.html'

    def get_object(self, queryset=None):
        username = self.kwargs.get('username')
        if username is not None:
            obj = get_object_or_404(User, username=username, is_teacher=True)
            return obj
        else:
            raise Http404("No Teachers found matching the query")
