from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse_lazy
from django.forms import formset_factory
from django.views.generic import (
    CreateView, DetailView,
    FormView,
    ListView,
    TemplateView,
    UpdateView,
    RedirectView,
)
from django.conf import settings
from django.db.models import Count
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.auth.decorators import login_required

import json

from .forms import (
    CommentCreateForm,
    DocumentUploadForm, LogbookCreateForm,
    MarkForm,
    BaseMarkFormSet,
    StudentGroupForm,
    StudentGroupJoinForm,
)
from .mixins import (
    StudentGroupContextMixin, UserHasGroupAccessMixin, UserIsStudentMixin,
    UserIsTeacherMixin)
from .models import Batch, Comment, Document, Logbook, StudentGroup, Notification
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

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()
        return form_class(user=self.request.user, **self.get_form_kwargs())

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
        if studentgroup.status != 'Pending':
            messages.error(
                self.request,
                "The Group has already been approved by admin. You can not join this group.",
                extra_tags='is-danger',
            )
            return HttpResponseRedirect('/group/join/')
        batch = studentgroup.batch
        students_count = studentgroup.students.all().count()
        if students_count >= batch.max_students_per_group:
            messages.error(
                self.request,
                'The Group has already reached maximum capacity',
                extra_tags='is-danger'
            )
            return HttpResponseRedirect('/group/join/')
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
    context_object_name = 'proposal_documents'

    def filter_by_document_type(self, document_type):
        return self.studentgroup.documents.filter(
            document_type=document_type,
        ).order_by(
            '-is_accepted', '-upload_time',
        )

    def get_queryset(self):
        return self.filter_by_document_type(Document.DocumentType.PROPOSAL.value)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = self.studentgroup.comments.order_by(
            '-created_at')
        context['pre_defense_documents'] = self.filter_by_document_type(
            Document.DocumentType.PRE_DEFENSE.value)
        context['defense_documents'] = self.filter_by_document_type(
            Document.DocumentType.DEFENSE.value)
        context['logbooks'] = self.studentgroup.logbooks.all().order_by('-time')
        return context

    def get(self, request, *args, **kwargs):
        notifications = Notification.objects.filter(
            user=request.user,
            studentgroup=self.studentgroup,
            is_viewed=False,
        )
        for notification in notifications:
            notification.is_viewed = True
        Notification.objects.bulk_update(notifications, ['is_viewed'])
        response = super().get(request, *args, **kwargs)
        return response


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


class LogbookCreateView(
        LoginRequiredMixin, UserIsStudentMixin, UserHasGroupAccessMixin,
        StudentGroupContextMixin, CreateView):
    model = Logbook
    template_name = 'thesis/logbook_upload.html'
    form_class = LogbookCreateForm
    success_url = reverse_lazy('thesis:document_list')
    http_method_names = ['get', 'post']

    def get_form(self, *args, **kwargs):
        return self.form_class(
            studentgroup=self.studentgroup,
            **self.get_form_kwargs(),
        )

    def form_valid(self, form):
        messages.success(
            self.request,
            'Logbook Created Successfully!',
            extra_tags='is-success',
        )
        return super().form_valid(form)


class LogbookDetailView(
        LoginRequiredMixin, UserHasGroupAccessMixin, StudentGroupContextMixin,
        DetailView):
    model = Logbook
    context_object_name = 'logbook'
    template_name = 'thesis/logbook_details.html'


class LogbookApprovedToggleView(
        LoginRequiredMixin,
        UserIsTeacherMixin,
        StudentGroupContextMixin,
        RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        logbook = get_object_or_404(
            Logbook,
            studentgroup=self.studentgroup,
            id=self.kwargs['logbook_id'],
        )
        logbook.approved = not logbook.approved
        logbook.save()
        if logbook.approved:
            messages.success(
                self.request,
                f'Logbook {logbook.id} has been approved',
                extra_tags='is-success',
            )
        else:
            messages.error(
                self.request,
                f'Logbook #{logbook.id} has been disapproved',
                extra_tags='is-danger',
            )
        return reverse_lazy(
            'thesis:group_detail',
            args=(self.studentgroup.md5hash,),
        )


class DocumentAcceptedToggleView(
        LoginRequiredMixin,
        UserIsTeacherMixin,
        StudentGroupContextMixin,
        RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        document = get_object_or_404(
            Document,
            studentgroup=self.studentgroup,
            id=self.kwargs['document_id'],
        )
        document.is_accepted = not document.is_accepted
        document.save()
        if document.is_accepted:
            messages.success(
                self.request, 'Document has been approved', extra_tags='is-success')
        else:
            messages.error(
                self.request, 'Document has been disapproved', extra_tags='is-danger')
        return reverse_lazy('thesis:group_detail', args=(self.studentgroup.md5hash,))


class GroupInviteView(
        LoginRequiredMixin, UserIsStudentMixin, UserHasGroupAccessMixin,
        StudentGroupContextMixin, TemplateView):
    http_method_names = ['get']
    template_name = "thesis/group_invite.html"


class BaseGroupListView(LoginRequiredMixin, UserIsTeacherMixin, ListView):
    template_name = "thesis/group_list.html"
    http_method_names = ['get']
    context_object_name = 'groups'

    def get_context_data(self, *args, object_list=None, **kwargs):
        context_data = super().get_context_data(
            *args, object_list=object_list, **kwargs)
        batch_number = self.kwargs.get('batch_number', '')
        context_data['batches'] = Batch.objects.all()
        context_data['batch_number'] = int(
            batch_number) if batch_number else ''
        return context_data

    def get_studentgroups(self, studentgroup_related_name):
        user = self.request.user
        queryset = getattr(user, studentgroup_related_name).filter(
            approved=True).order_by('id')
        batch_number = self.kwargs.get('batch_number', '')
        if batch_number:
            return queryset.filter(batch__number=batch_number)
        return queryset


class GroupListView(BaseGroupListView):
    def get_queryset(self):
        return self.get_studentgroups('studentgroups')


class InternalGroupListView(BaseGroupListView):
    def get_queryset(self):
        return self.get_studentgroups('internal_studentgroups')


class ExternalGroupListView(BaseGroupListView):
    def get_queryset(self):
        return self.get_studentgroups('external_studentgroups')


class NotificationListView(LoginRequiredMixin, ListView):
    template_name = "thesis/notification_list.html"
    http_method_names = ['get']
    context_object_name = 'notifications'

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user, is_viewed=False).order_by('-created_at')


class GroupUpdateView(
        LoginRequiredMixin, UserIsStudentMixin, UserHasGroupAccessMixin,
        UpdateView):
    model = StudentGroup
    template_name = "thesis/group_update.html"
    http_method_names = ['get', 'post']
    form_class = StudentGroupForm
    success_url = reverse_lazy('thesis:document_list')

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()
        return form_class(user=self.request.user, **self.get_form_kwargs())

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
    return JsonResponse(data, safe=False,)


@login_required
def grade_students(request, group_code):
    studentgroup = get_object_or_404(StudentGroup, md5hash=group_code)
    user = request.user
    students = studentgroup.students.all().order_by('username')
    students_count = students.count()
    MarkFormSet = formset_factory(
        MarkForm,
        extra=students_count,
        min_num=students_count,
        max_num=students_count,
        validate_min=True,
        validate_max=True,
        formset=BaseMarkFormSet,
    )
    formset_initial = {
        "form_kwargs": {
            'user': user,
            'studentgroup': studentgroup,
        },
        "initial": [{"student_choice": student.id} for student in students],
    }
    if request.method == 'POST':
        formset = MarkFormSet(request.POST, **formset_initial)
        if formset.is_valid():
            formset.save()
            messages.success(
                request,
                'Grades have been submitted successfully.',
                extra_tags='is-success')
            return redirect(
                reverse_lazy(
                    'thesis:group_detail',
                    args=(group_code,),
                ),
            )
        else:
            return render(
                request,
                'thesis/create-mark.html',
                context={
                    'studentgroup': studentgroup,
                    'user': user,
                    'formset': formset,
                },
            )
    return render(
        request,
        'thesis/create-mark.html',
        context={
            'studentgroup': studentgroup,
            'user': user,
            'formset': MarkFormSet(**formset_initial)
        },
    )
