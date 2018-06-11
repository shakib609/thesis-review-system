from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect, JsonResponse
from django.views.generic import (
    CreateView,
    TemplateView,
    FormView,
    ListView,
    UpdateView,
)

from .mixins import (
    UserIsStudentMixin,
    UserIsTeacherMixin,
    UserHasGroupAccessMixin,
    StudentGroupContextMixin,
)
from .forms import (
    StudentGroupForm,
    StudentGroupJoinForm,
    DocumentUploadForm,
    CommentCreateForm,
)
from .models import StudentGroup, Document, Comment


class GroupCreateJoinView(LoginRequiredMixin, UserIsStudentMixin,
                          TemplateView):
    http_method_names = ['get']
    template_name = 'thesis/group_create_join.html'


class GroupCreateView(LoginRequiredMixin, UserIsStudentMixin,
                      CreateView):
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
        messages.success(self.request, 'Created Group Successfully!')
        return HttpResponseRedirect(self.get_success_url())


class GroupJoinView(LoginRequiredMixin, UserIsStudentMixin,
                    FormView):
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
        messages.success(self.request, 'You joined the Group successfully!')
        return HttpResponseRedirect(self.get_success_url())


class DocumentListView(LoginRequiredMixin, UserHasGroupAccessMixin,
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


class DocumentUploadView(LoginRequiredMixin, UserIsStudentMixin,
                         UserHasGroupAccessMixin, StudentGroupContextMixin,
                         CreateView):
    model = Document
    template_name = 'thesis/document_upload.html'
    form_class = DocumentUploadForm
    success_url = reverse_lazy('thesis:document_list')
    http_method_names = ['get', 'post']

    def form_valid(self, form):
        self.object = document = form.save(commit=False)
        document.studentgroup = self.studentgroup
        document.save()
        messages.success(self.request, 'Document Uploaded successfully!')
        return HttpResponseRedirect(self.get_success_url())


class GroupInviteView(LoginRequiredMixin, UserIsStudentMixin,
                      UserHasGroupAccessMixin, StudentGroupContextMixin,
                      TemplateView):
    http_method_names = ['get']
    template_name = "thesis/group_invite.html"


class GroupListView(LoginRequiredMixin, UserIsTeacherMixin,
                    ListView):
    template_name = "thesis/group_list.html"
    http_method_names = ['get']
    context_object_name = 'groups'

    def get_queryset(self):
        user = self.request.user
        queryset = user.studentgroups.order_by('title')
        return queryset


class GroupUpdateView(LoginRequiredMixin, UserIsStudentMixin,
                      UserHasGroupAccessMixin, UpdateView):
    model = StudentGroup
    template_name = "thesis/group_update.html"
    http_method_names = ['get', 'post']
    form_class = StudentGroupForm
    success_url = reverse_lazy('thesis:document_list')

    def get_object(self, *args, **kwargs):
        return self.request.user.studentgroup

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Group Updated Successfully!')
        return response


class CommentCreateView(LoginRequiredMixin, UserHasGroupAccessMixin,
                        StudentGroupContextMixin, CreateView):
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
        return JsonResponse(
            {'success': False, 'errors': form.errors}
        )
