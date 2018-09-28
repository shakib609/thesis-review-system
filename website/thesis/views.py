from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView, FormView, ListView, TemplateView, UpdateView)
from django.conf import settings
from django.db.models import Count
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.auth.decorators import login_required

import json

from .forms import (
    CommentCreateForm, DocumentUploadForm, StudentGroupForm,
    StudentGroupJoinForm)
from .mixins import (
    StudentGroupContextMixin, UserHasGroupAccessMixin, UserIsStudentMixin,
    UserIsTeacherMixin)
from .models import Comment, Document, StudentGroup
from ..registration.models import User


class GroupCreateJoinView(
        LoginRequiredMixin, UserIsStudentMixin, TemplateView):
    http_method_names = ['get']
    template_name = 'thesis/group_create_join.html'


class GroupCreateView(LoginRequiredMixin, UserIsStudentMixin, CreateView):
    model = StudentGroup
    form_class = StudentGroupForm
    success_url = reverse_lazy('thesis:document_list')
    template_name = 'thesis/group_create.html'
    http_method_names = ['get', 'post']

    def form_valid(self, form):
        self.object = studentgroup = form.save()
        user = self.request.user
        user.studentgroup = studentgroup
        user.save()
        messages.success(
            self.request,
            'Created Group Successfully!',
            extra_tags='is-success')
        return HttpResponseRedirect(self.get_success_url())


class GroupJoinView(LoginRequiredMixin, UserIsStudentMixin, FormView):
    model = StudentGroup
    form_class = StudentGroupJoinForm
    success_url = reverse_lazy('thesis:document_list')
    template_name = 'thesis/group_join.html'
    http_method_names = ['get', 'post']

    def form_valid(self, form):
        md5hash = form.cleaned_data.get('md5hash')
        studentgroup = get_object_or_404(StudentGroup, md5hash=md5hash)
        user = self.request.user
        user.studentgroup = studentgroup
        user.save()
        messages.success(
            self.request,
            'You joined the Group successfully!',
            extra_tags='is-success')
        return HttpResponseRedirect(self.get_success_url())


class DocumentListView(
        LoginRequiredMixin, UserHasGroupAccessMixin,
        StudentGroupContextMixin, ListView):
    template_name = 'thesis/document_list.html'
    http_method_names = ['get']
    context_object_name = 'documents'

    def get_queryset(self):
        queryset = self.studentgroup.documents.all()
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = self.studentgroup.comments.order_by(
            '-created_at')
        return context


class DocumentUploadView(
        LoginRequiredMixin, UserIsStudentMixin, UserHasGroupAccessMixin,
        StudentGroupContextMixin, CreateView):
    model = Document
    template_name = 'thesis/document_upload.html'
    form_class = DocumentUploadForm
    success_url = reverse_lazy('thesis:document_list')
    http_method_names = ['get', 'post']

    def form_valid(self, form):
        self.object = document = form.save(commit=False)
        document.studentgroup = self.studentgroup
        document.save()
        messages.success(
            self.request,
            'Document Uploaded successfully!',
            extra_tags='is-success')
        return HttpResponseRedirect(self.get_success_url())


class GroupInviteView(
        LoginRequiredMixin, UserIsStudentMixin, UserHasGroupAccessMixin,
        StudentGroupContextMixin, TemplateView):
    http_method_names = ['get']
    template_name = "thesis/group_invite.html"


class GroupListView(LoginRequiredMixin, UserIsTeacherMixin, ListView):
    template_name = "thesis/group_list.html"
    http_method_names = ['get']
    context_object_name = 'groups'

    def get_queryset(self):
        user = self.request.user
        queryset = user.studentgroups.order_by('title')
        return queryset


class GroupUpdateView(
        LoginRequiredMixin, UserIsStudentMixin, UserHasGroupAccessMixin,
        UpdateView):
    model = StudentGroup
    template_name = "thesis/group_update.html"
    http_method_names = ['get', 'post']
    form_class = StudentGroupForm
    success_url = reverse_lazy('thesis:document_list')

    def get_object(self, *args, **kwargs):
        return self.request.user.studentgroup

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            'Group Updated Successfully!',
            extra_tags='is-success')
        return response


class CommentCreateView(
        LoginRequiredMixin, UserHasGroupAccessMixin, StudentGroupContextMixin,
        CreateView):
    model = Comment
    http_method_names = ['post']
    form_class = CommentCreateForm
    success_url = reverse_lazy('thesis:document_list')

    def get_success_url(self, *args, **kwargs):
        if self.request.user.is_teacher:
            return reverse_lazy(
                'thesis:group_detail',
                kwargs={'group_code': self.studentgroup.md5hash})
        return self.success_url

    def form_valid(self, form):
        self.object = comment = form.save(commit=False)
        comment.user = self.request.user
        comment.studentgroup = self.studentgroup
        comment.save()
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        messages.error(
            self.request,
            'Comment can not be empty.',
            extra_tags='is-danger'
        )
        return HttpResponseRedirect(self.get_success_url())


class StudentGroupApproveView(
        LoginRequiredMixin, UserIsTeacherMixin, StudentGroupContextMixin,
        TemplateView):
    http_method_names = ['get', 'post']
    template_name = 'thesis/group_approve.html'

    def post(self, request, *args, **kwargs):
        if self.studentgroup.approved:
            self.studentgroup.approved = False
            if self.studentgroup.progress == 100:
                self.studentgroup.progress = 90
            messages.success(
                request,
                'The StudentGroups Proposal has been disapproved!',
                extra_tags='is-success')
        else:
            self.studentgroup.approved = True
            self.studentgroup.progress = 100
            messages.success(
                request,
                'The StudentGroups Proposal has been approved!',
                extra_tags='is-success')
        self.studentgroup.save()
        return HttpResponseRedirect(
            reverse_lazy(
                'thesis:group_detail',
                kwargs={'group_code': self.studentgroup.md5hash}))


class StudentGroupProgressUpdateView(
        LoginRequiredMixin, UserIsTeacherMixin, StudentGroupContextMixin,
        TemplateView):
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        data = json.loads(str(request.body.decode('utf-8')))
        progress_value = int(data.get('progress_value'))
        if progress_value > 100:
            progress_value = 100
        elif progress_value < 0:
            progress_value = 0
        self.studentgroup.progress = progress_value
        self.studentgroup.save()
        return JsonResponse({'progress_value': progress_value})


@login_required
def get_teachers_list_by_field_json(request, field_id):
    available_teachers = User.objects.values(
        'id', 'username', 'full_name',
        group_count=Count('studentgroups')).filter(
        fields__id=field_id,
        group_count__lt=settings.MAXIMUM_GROUPS_UNDER_TEACHER
    )

    data = json.dumps(list(available_teachers), cls=DjangoJSONEncoder)
    return JsonResponse(
        data,
        safe=False)
