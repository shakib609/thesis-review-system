from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import RedirectView
from django.views.generic import TemplateView, CreateView
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy

from .forms import StudentSignUpForm
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
    template_name = 'registration/register.html'
    form_class = StudentSignUpForm
    success_url = reverse_lazy('registration:login_redirect')
    http_method_names = ['get', 'post']

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect(self.get_success_url())
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        self.object = user = form.save()
        request = self.request
        login(request, user)
        return HttpResponseRedirect(self.get_success_url())
