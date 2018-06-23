from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import (
    TemplateView,
    CreateView,
    RedirectView,
    UpdateView,
)
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.contrib import messages

from .forms import StudentSignUpForm, UserUpdateForm
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
        messages.success(self.request, 'User Created Successfully!')
        return response


class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = "registration/user_update.html"
    http_method_names = ['get', 'post']
    form_class = UserUpdateForm
    success_url = reverse_lazy('registration:login_redirect')

    def get_object(self, *args, **kwargs):
        return self.request.user

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Update Successful!')
        return response


class UserDeleteView(LoginRequiredMixin, TemplateView):
    template_name = "registration/user_delete.html"
    http_method_names = ['get', 'post']

    def post(self, request, *args, **kwargs):
        user = self.request.user
        user.delete()
        messages.success(request, 'Account deleted successfully!')
        return HttpResponseRedirect(reverse_lazy('registration:login'))
