from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from .forms import StudentGroupForm
from .decorators import is_teacher, is_student


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
