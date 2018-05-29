from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from .forms import StudentGroupForm, StudentGroupJoinForm
from .models import StudentGroup
from .decorators import is_student


@login_required
@is_student
def group_page(request):
    return render(request, 'thesis/group_page.html')


@login_required
@is_student
def create_studentgroup(request):
    if request.method == 'POST':
        form = StudentGroupForm(data=request.POST)
        if form.is_valid():
            s = form.save()
            u = request.user
            u.studentgroup = s
            u.save()
            return redirect('/')
    else:
        form = StudentGroupForm()
    return render(request, 'thesis/create_studentgroup.html', {'form': form})


@login_required
@is_student
def join_studentgroup(request):
    if request.method == 'POST':
        form = StudentGroupJoinForm(data=request.POST)
        if form.is_valid():
            md5hash = form.cleaned_data.get('md5hash')
            u = request.user
            s = StudentGroup.objects.get(md5hash=md5hash)
            u.studentgroup = s
            u.save()
            return redirect('/')
    else:
        form = StudentGroupJoinForm()
    return render(request, 'thesis/join_studentgroup.html', {'form': form})
