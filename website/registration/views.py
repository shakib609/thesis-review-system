from django.shortcuts import redirect
from django.contrib.auth import login
from django.views.generic import TemplateView, CreateView
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy

from .forms import StudentSignUpForm
from .models import User


class AboutView(TemplateView):
    template_name = 'registration/about.html'


class UserCreateView(CreateView):
    model = User
    template_name = 'registration/register.html'
    form_class = StudentSignUpForm
    success_url = reverse_lazy('thesis:account_redirect')

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('registration:login')
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        self.object = user = form.save()
        request = self.request
        login(request, user)
        return HttpResponseRedirect(self.get_success_url())
