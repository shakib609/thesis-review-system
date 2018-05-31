from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from .forms import StudentGroupForm, StudentGroupJoinForm
from .models import StudentGroup
from .decorators import is_student, is_teacher


@login_required
def account_redirect(request):
    if request.user.is_teacher:
        return redirect('thesis:groups_home')
    if request.user.studentgroup:
        return redirect('thesis:group_home')
    return redirect('thesis:group_create_join')


@login_required
@is_student
def group_create_join(request):
    return render(request, 'thesis/group_create_join.html')


@login_required
@is_student
def group_create(request):
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
    return render(request, 'thesis/group_create.html', {'form': form})


@login_required
@is_student
def group_join(request):
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
    return render(request, 'thesis/group_join.html', {'form': form})


@login_required
@is_student
def group_home(request):
    studentgroup = request.user.studentgroup
    return render(
        request, 'thesis/group_home.html', {'studentgroup': studentgroup})


@login_required
@is_teacher
def groups_home(request):
    return render(request, 'thesis/groups_home.html')
