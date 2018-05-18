from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate

from .forms import StudentSignUpForm


def register(request):
    if request.method == 'POST':
        form = StudentSignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('registration:register')
    else:
        form = StudentSignUpForm()
    return render(request, 'trs/register.html', {'form': form})
