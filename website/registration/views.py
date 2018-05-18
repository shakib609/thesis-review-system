from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate

from .forms import StudentSignUpForm


def home(request):
    if request.user.is_authenticated:
        pass  # TODO: redirect by user role
    else:
        return render(request, 'registration/home.html')


def register(request):
    redirect_to = 'registration:register'
    if request.user.is_authenticated:
        return redirect(redirect_to)
    if request.method == 'POST':
        form = StudentSignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect(redirect_to)
    else:
        form = StudentSignUpForm()
    return render(request, 'registration/register.html', {'form': form})
