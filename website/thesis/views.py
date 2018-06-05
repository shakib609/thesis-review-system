from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import HttpResponse
from django.template.defaultfilters import date

import json

from .forms import (
    StudentGroupForm, StudentGroupJoinForm, DocumentUploadForm)
from .models import StudentGroup, Document, Comment
from .decorators import is_student, is_teacher


def return_json(data):
    return HttpResponse(json.dumps(data), content_type='application/json')


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
@require_POST
def create_comment(request, group_code):
    studentgroup = get_object_or_404(StudentGroup, md5hash=group_code)
    user = request.user
    if (user.studentgroup != studentgroup) or user.is_teacher is False:
        return return_json({'created': False})
    req = json.loads(request.body.decode('utf-8'))
    content = req.get('content')
    comment = Comment(content=content, user=user, studentgroup=studentgroup)
    try:
        comment.save()
        d = comment.created_at
        response = {
            'created': True,
            'created_at': date(d, 'd M Y') + ' at ' + date(d, 'H:i'),
        }
        return return_json(response)
    except:
        return return_json({'created': False})


@login_required
@is_student
def document_upload(request):
    if request.method == 'POST':
        form = DocumentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            document = Document(file=request.FILES['file'])
            document.studentgroup = request.user.studentgroup
            document.save()
            return redirect('thesis:group_home')
    else:
        form = DocumentUploadForm()
    studentgroup = request.user.studentgroup
    return render(request, 'thesis/document_upload.html', {
        'form': form,
        'studentgroup': studentgroup
    })


@login_required
@is_teacher
def groups_home(request):
    return render(request, 'thesis/groups_home.html')
