from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import CreateView, UpdateView, DeleteView, FormView, DetailView, TemplateView, ListView
from django.contrib import messages
from django.views.generic.base import View, TemplateResponseMixin
from django.forms.models import modelform_factory
from django.apps import apps
import uuid
from django.utils import timezone
from django.http import JsonResponse

from django.core.files import File

from .models import *
from management.models import CodeFile, SolutionEventType, Status, Verdict, lang_extension

from .forms import *


class OwnerMixin(object):
    def __init__(self):
        self.request = None

    def get_queryset(self):
        qs = super(OwnerMixin, self).get_queryset()
        return qs.filter(owner=self.request.user)


class OwnerEditMixin(object):
    def __init__(self):
        self.request = None

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super(OwnerEditMixin, self).form_valid(form)


class ChannelView(DetailView):
    model = Channel
    template_name = 'channel/channel.html'
    context_object_name = 'channel'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['subscribe_form'] = ChannelSubscribeForm
        context['delete_subscribe_form'] = ChannelDeleteSubscribeForm
        return context

    def get_object(self, queryset=None):
        if 'slug' in self.kwargs:
            return get_object_or_404(Channel, slug=self.kwargs['slug'])
        elif 'slug' not in self.kwargs and self.request.user.is_authenticated:
            return get_object_or_404(Channel, owner=self.request.user)

        raise Http404


class ChannelCreateView(TemplateView, LoginRequiredMixin):
    template_name = 'channel/channel_create.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['channel_form'] = ChannelForm
        if self.request.user.is_authenticated:
            if hasattr(self.request.user, 'channel'):
                context['channel_form'] = ChannelForm(instance=Channel.objects.get(owner=self.request.user))
        return context


class ChannelCreateFormHandle(FormView, OwnerEditMixin):
    template_name = 'channel/channel_create.html'
    model = Channel
    form_class = ChannelForm

    def form_valid(self, form: forms.ModelForm):
        form.instance.owner = self.request.user
        form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('my_channel', kwargs=self.kwargs)


class ChannelUpdateView(UpdateView, LoginRequiredMixin):
    model = Channel
    fields = ['title',
              'slug',
              'channel_description',
              'background_color',
              'preview_image',
              'background_image',
              'cover_image',
              'owner_full_name',
              'owner_interview',
              'owner_photo', ]
    template_name = 'channel/channel_update.html'

    def form_valid(self, form):
        return super().form_valid(form)

    def get_object(self, queryset=None):
        try:
            channel = Channel.objects.get(slug=self.kwargs['slug'])
            if channel.owner == self.request.user:
                return channel
            else:
                raise Http404
        except TypeError:
            raise Http404

    def get_success_url(self):
        messages.success(self.request, '?????????????????? ???????????? ?????????????? ??????????????????')
        return self.request.path_info

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['channel'] = get_object_or_404(Channel, slug=self.kwargs['slug'])
        return context


class ChannelSubscribersListView(ListView, LoginRequiredMixin):
    template_name = 'channel/channel_subscribers_list.html'
    model = User

    def get_queryset(self):
        channel = get_object_or_404(Channel, slug=self.kwargs['slug'])
        return channel.subscribers.all()

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['channel'] = get_object_or_404(Channel, slug=self.kwargs['slug'])
        return context


class ChannelSubscriberDetailView(DetailView):
    template_name = 'channel/channel_subscriber_detail.html'
    model = User

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['channel'] = get_object_or_404(Channel, slug=self.kwargs['slug'])
        return context


class ChannelSubscribeFormHandle(FormView):
    template_name = 'channel/channel.html'
    form_class = ChannelDeleteSubscribeForm

    def get_success_url(self):
        return reverse('channel', kwargs={'slug': self.kwargs['slug']})

    def form_valid(self, form):
        if not self.request.user.is_authenticated:
            raise Http404

        channel = get_object_or_404(Channel, slug=self.kwargs['slug'])
        channel.subscribers.add(self.request.user)
        channel.save()
        return super().form_valid(form)


class ChannelDeleteSubscribeFormHandle(FormView):
    template_name = 'channel/channel.html'
    form_class = ChannelDeleteSubscribeForm

    def get_success_url(self):
        kwargs = {'slug': self.kwargs['slug']}
        if self.request.user == Channel.objects.get(slug=self.kwargs['slug']).owner:
            return reverse('channel', kwargs=kwargs)
        else:
            return reverse('channel', kwargs=kwargs)

    def form_valid(self, form):
        if not self.request.user.is_authenticated:
            raise Http404
        channel = get_object_or_404(Channel, slug=self.kwargs['slug'])
        if 'username' not in self.kwargs:
            channel.subscribers.remove(self.request.user)
        else:
            try:
                channel.subscribers.remove(get_object_or_404(User, username=self.kwargs['username']))
            except ObjectDoesNotExist:
                raise Http404
        channel.save()
        return super().form_valid(form)


class ManageChannelSubscriber(DetailView, LoginRequiredMixin):
    template_name = 'channel/channel_subscriber_detail.html'
    model = User

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['channel'] = get_object_or_404(Channel, slug=self.kwargs['slug'])
        context['delete_subscriber_form'] = ChannelDeleteSubscribeForm
        return context

    def get_object(self, queryset=None):
        try:
            return get_object_or_404(User, username=self.kwargs['username'])
        except KeyError:
            raise Http404


class ChannelCoursesListView(ListView, LoginRequiredMixin):
    model = Course
    template_name = 'channel/channel_course_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['channel'] = get_object_or_404(Channel, slug=self.kwargs['slug'])
        return context

    def get_queryset(self):
        # courses = Course.objects.all()
        # return courses.filter(owner=self.request.user,
        #                       channel=Channel.objects.get(slug=self.kwargs['slug']))

        channel = get_object_or_404(Channel, slug=self.kwargs['slug'])
        if channel.owner == self.request.user:
            qs = Course.objects.all()
            return qs.filter(owner=self.request.user)

        raise Http404


class CourseDetail(DetailView):  # Main page of the course
    model = Course
    template_name = 'course/course.html'
    context_object_name = 'course'

    def get_object(self, queryset=None):
        return get_object_or_404(Course, slug=self.kwargs['slug'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['course_join_form'] = CourseJoinForm
        context['course_leave_form'] = CourseDeleteStudentForm
        context['is_subscribed'] = False

        obj = Course.objects.get(slug=self.kwargs.get('slug', None))
        if self.request.user.is_authenticated:
            sub_list = Student.objects.filter(
                course=obj,
                user=self.request.user,
            )
            if len(sub_list) > 0:
                context['is_subscribed'] = True
                context['student'] = Student.objects.get(
                    course=obj,
                    user=self.request.user,
                )

        return context


class CourseCreateView(TemplateView, LoginRequiredMixin):
    template_name = 'channel/channel_course_create.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['channel'] = get_object_or_404(Channel, slug=self.kwargs['slug'])
        context['course_create_form'] = CourseForm

        return context


class CourseCreateFormHandle(FormView, LoginRequiredMixin):
    template_name = 'channel/channel_course_create.html'
    form_class = CourseForm

    def form_valid(self, form):
        channel = get_object_or_404(Channel, slug=self.kwargs['slug'])
        if channel.owner == self.request.user:
            form.instance.owner = self.request.user
            form.instance.channel = channel
            if form.is_valid():
                form.save()
                messages.success(self.request, f'???????? {form.cleaned_data["title"]} ?????????????? ????????????')
                return super().form_valid(form=form)

            messages.error(self.request, '???????????? ?????? ???????????????????? ??????????')

        raise Http404

    def get_success_url(self):
        return reverse('channel_course_list_edit', kwargs=self.kwargs)


class CourseUpdateView(UpdateView, LoginRequiredMixin):
    model = Course
    template_name = 'course/course_update.html'
    fields = (
        'title',
        'slug',
        'description',
        'theme',
        'show_course_in_channel_page',
        'preview_picture',
        'main_picture',
    )

    def get_object(self, queryset=None):
        try:
            course = get_object_or_404(Course, slug=self.kwargs['slug'])
            if course.owner == self.request.user:
                return course
            raise Http404
        except TypeError:
            raise Http404

    def form_valid(self, form):
        form.save()
        messages.success(self.request, '???????????? ?? ?????????? ?????????????? ??????????????????')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course'] = get_object_or_404(Course, slug=self.kwargs['slug'])
        return context

    def get_success_url(self):
        return self.request.path_info


class CourseDescriptionBlockUpdateView(TemplateView, TemplateResponseMixin, View):
    course = None
    template_name = 'course/course_update_description_blocks.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course'] = get_object_or_404(Course, slug=self.kwargs['slug'])
        return context

    def dispatch(self, request, *args, **kwargs):
        self.course = get_object_or_404(Course, slug=self.kwargs['slug'])
        return super(CourseDescriptionBlockUpdateView, self).dispatch(request=request)

    def get_formset(self, *args):
        return CourseDescriptionBlockFormSet(
            *args,
            instance=self.course,
        )

    def get(self, request, *args, **kwargs):
        if self.request.user != Course.objects.get(slug=self.kwargs.get('slug', None)).owner:
            raise Http404
        formset = self.get_formset()
        return self.render_to_response({'course': self.course, 'formset': formset})

    def post(self, request, *args, **kwargs):
        formset = self.get_formset(request.POST, request.FILES)
        if formset.is_valid():
            formset.save()
            messages.success(request, '???????????? ?????????????? ??????????????????')
            return HttpResponseRedirect(reverse('update_course_description', kwargs={'slug': self.kwargs['slug']}))
        messages.error(request, '???????????? ?????? ???????????????????? ????????????')
        return self.render_to_response({'course': self.course, 'formset': formset})


class CourseStudentsListView(ListView):
    model = Student
    template_name = 'course/course_students_list.html'

    def dispatch(self, request, *args, **kwargs):
        if self.request.user != Course.objects.get(slug=self.kwargs.get('slug', None)).owner:
            raise Http404
        return super(CourseStudentsListView, self).dispatch(request)

    def get_queryset(self):
        qs = Student.objects.all()
        return qs.filter(course=get_object_or_404(Course, slug=self.kwargs['slug']))

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course'] = get_object_or_404(Course, slug=self.kwargs.get('slug'))
        return context


class CourseStudentDetailView(DetailView):
    model = Student
    template_name = 'course/course_student_detail.html'
    context_object_name = 'student'

    def get_object(self, queryset=None):
        return Student.objects.get(
            course=get_object_or_404(Course, slug=self.kwargs.get('slug', None)),
            user=get_object_or_404(User, username=self.kwargs.get('username', None))
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course'] = get_object_or_404(Course, slug=self.kwargs.get('slug'))
        context['delete_student_form'] = CourseDeleteStudentForm
        return context


class CourseJoinFormHandle(FormView):
    form_class = CourseJoinForm
    template_name = 'course/course.html'

    def form_valid(self, form):
        if not self.request.user.is_authenticated:
            raise Http404
        course = get_object_or_404(Course, slug=self.kwargs.get('slug', None))
        user = self.request.user
        new_student = Student.objects.create(
            course=course,
            user=user,
            cur_module=1,
        )
        new_student.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('course', kwargs=self.kwargs)


class CourseDeleteStudentFormHandle(FormView):
    form_class = CourseDeleteStudentForm
    template_name = 'course/course_student_detail.html'

    def get_success_url(self):
        if self.request.user == Course.objects.get(slug=self.kwargs.get('slug', None)).owner:
            return reverse('course_students_list', kwargs={'slug': self.kwargs.get('slug', None)})
        else:
            return reverse('course', kwargs={'slug': self.kwargs.get('slug', None)})

    def form_valid(self, form):
        student = Student.objects.get(user=User.objects.get(username=self.kwargs.get('username', None)),
                                      course=Course.objects.get(slug=self.kwargs.get('slug', None)))
        student.delete()
        return super().form_valid(form)


class CourseModuleList(ListView):
    model = Module
    template_name = 'course/course_module_list.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course'] = get_object_or_404(
            Course, slug=self.kwargs.get('slug', None)
        )
        return context

    def get_queryset(self):
        qs = Module.objects.filter(
            course=get_object_or_404(Course, slug=self.kwargs.get('slug', None))
        )
        return qs


class CourseModuleCreateView(TemplateView):
    template_name = 'course/course_module_create.html'

    def get_context_data(self, **kwargs):
        context = super(CourseModuleCreateView, self).get_context_data(**kwargs)
        context['course'] = get_object_or_404(
            Course, slug=self.kwargs.get('slug', None)
        )
        context['form'] = ModuleForm
        return context


class CourseModuleCreateFormHandle(FormView):
    template_name = 'course/course_module_create.html'
    form_class = ModuleForm

    def form_valid(self, form):
        if form.is_valid():
            course = Course.objects.get(slug=self.kwargs.get('slug', None))
            if self.request.user == course.owner:
                form.instance.owner = self.request.user
                form.instance.course = course
                form.save()
                messages.success(self.request, '???????????? ????????????')
            else:
                raise Http404
        else:
            messages.error(self.request, '???????????? ?????? ???????????????? ????????????')

        return super().form_valid(form)

    def get_success_url(self):
        return reverse('module_list', kwargs=self.kwargs)


class CourseModuleUpdate(UpdateView):
    model = Module
    template_name = 'course/course_module_update.html'
    fields = (
        'title',
        'description',
    )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course'] = get_object_or_404(
            Course, slug=self.kwargs.get('slug', None)
        )
        return context

    def get_object(self, queryset=None):
        return Module.objects.get(
            course=get_object_or_404(Course, slug=self.kwargs.get('slug', None)),
            order=self.kwargs.get('order', None)
        )

    def form_valid(self, form):
        messages.success(self.request, '???????????? ?? ???????????? ?????????????? ??????????????????')
        return super().form_valid(form)

    def get_success_url(self):
        return self.request.path_info


class ContentCreateUpdateView(TemplateView, TemplateResponseMixin, View):
    course = None
    module = None
    model = None
    obj = None
    template_name = 'module/module_content_create_update.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course'] = Course.objects.get(slug=self.kwargs['slug'])
        return context

    @staticmethod
    def get_model(model_name):
        if model_name in ['puretext',
                          # 'pdf',
                          'latex',
                          'codelisting',
                          'picture',
                          'videolink', ]:
            response = apps.get_model(app_label='courses', model_name=model_name)
            return response
        else:
            raise Http404

    @staticmethod
    def get_form(model, *args, **kwargs):
        form = modelform_factory(model=model,
                                 exclude=[
                                     'owner',
                                     'order',
                                     'created',
                                     'updated',
                                 ])
        return form(*args, **kwargs)

    def dispatch(self, request, slug, order, model_name, id=None, *args, **kwargs):
        self.course = Course.objects.get(slug=slug)
        self.module = get_object_or_404(Module, course=self.course, order=order)
        self.model = ContentCreateUpdateView.get_model(model_name)
        print(self.model.objects.all())
        if 'id' in self.kwargs:
            self.obj = self.model.objects.get(id=self.kwargs['id'] - 1)
        return super(ContentCreateUpdateView, self).dispatch(request, slug, order, model_name, id)

    def get(self, request, *args, **kwargs):
        form = ContentCreateUpdateView.get_form(self.model, instance=self.obj)
        return self.render_to_response({'form': form, 'object': self.obj, 'course': self.course})

    def post(self, request, slug, order, model_name, id=None, *args, **kwargs):
        form = ContentCreateUpdateView.get_form(self.model,
                                                instance=self.obj,
                                                data=request.POST,
                                                files=request.FILES)

        if form.is_valid():
            obj = form.save(commit=False)
            obj.owner = self.request.user
            obj.save()

            if not id:
                if self.model == LaTeX:
                    obj.text = obj.file.read().decode('utf-8')
                    obj.save()
                Content.objects.create(module=self.module, item=obj)

            messages.success(self.request, '?????????????? ????????????????')
            return redirect('course_module_content_list', self.course.slug, self.module.order)

        return self.render_to_response({'form': form, 'object': self.obj, 'course': self.course})


class ContentDeleteView(View):
    def post(self, request, slug, order, id):
        content = get_object_or_404(
            Content,
            id=id,
            module__course__owner=self.request.user,
        )
        module = content.module
        course = module.course
        content.item.delete()
        content.delete()
        return redirect('course_module_content_list', course.slug, module.order)


class CourseModuleContentListView(TemplateView, LoginRequiredMixin):
    template_name = 'module/module_content_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course'] = get_object_or_404(
            Course,
            slug=self.kwargs.get('slug', None)
        )
        if context['course'].owner != self.request.user:
            raise Http404
        context['module'] = get_object_or_404(
            Module,
            course=context['course'],
            order=self.kwargs.get('order', None)
        )
        qs = Content.objects.all()
        context['object_list'] = qs.filter(module=context['module'])
        return context


class CourseTaskList(ListView):
    model = CourseTask
    template_name = 'course/course_task_list.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course'] = Course.objects.get(slug=self.kwargs.get('slug', None))
        return context

    def get_queryset(self):
        qs = self.model.objects.all()
        return qs.filter(course=Course.objects.get(slug=self.kwargs.get('slug', None)))


class CourseTaskCreateView(TemplateView):
    template_name = 'task/task_create.html'

    # noinspection DuplicatedCode
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course'] = Course.objects.get(slug=self.kwargs.get('slug', None))
        context['course_task_form'] = CourseTaskForm
        return context


class CourseTaskCreateFormHandle(FormView):
    template_name = 'task/task_create.html'
    form_class = CourseTaskForm

    def form_valid(self, form):
        if form.is_valid():
            form.save(commit=False)
            form.instance.course = Course.objects.get(slug=self.kwargs.get('slug', None))
            new_code_file = CodeFile.objects.create(
                file=form.cleaned_data['solution_file_raw'],
                language=form.cleaned_data['solution_file_lang'],
                code=form.cleaned_data['solution_file_raw'].read().decode('utf-8'),
                file_name=str(uuid.uuid4()) + form.cleaned_data['solution_file_raw'].name,
            )
            new_code_file.save()

            form.instance.solution_file = new_code_file
            form.save()
            task_validate_solution = CourseSolution.objects.create(
                author=self.request.user,
                code_file=new_code_file,
                task=form.instance,
                node=1,
                event_type=SolutionEventType.AUTHOR_TASK_VALIDATION,
                course=form.instance.course,
                course_task=form.instance,
            )
            task_validate_solution.save()
            form.instance.last_validate_solution = task_validate_solution
            form.save()
            messages.success(self.request, '???????????? ??????????????????')

        return super().form_valid(form)

    def get_success_url(self):
        return reverse('course_task_list', kwargs=self.kwargs)


class CourseTaskUpdateView(UpdateView):
    template_name = 'task/task_update.html'
    model = CourseTask
    fields = (
        'title',
        'task_description',
        'input_description',
        'output_description',
        'input_example',
        'output_example',
        'time_limit_seconds',
        'answer_type',
        'grading_system',
        'solution_file_raw',
        'solution_file_lang',
        'show_in_task_list',
        'difficulty',
    )

    def get_object(self, queryset=None):
        return get_object_or_404(CourseTask, id=self.kwargs.get('id', None))

    def form_valid(self, form):
        if form.is_valid():
            code_file = CodeFile.objects.get(task=form.instance)
            code_file.file = form.cleaned_data['solution_file_raw']
            code_file.language = form.cleaned_data['solution_file_lang']
            code_file.code = form.cleaned_data['solution_file_raw'].read().decode('utf-8')
            code_file.save()
            form.save()

            c_f = code_file
            c_f.pk = None
            c_f.save()

            task_validate_solution = CourseSolution.objects.create(
                author=self.request.user,
                code_file=c_f,
                task=form.instance,
                course=form.instance.course,
                course_task=form.instance,
                node=1,
                event_type=SolutionEventType.AUTHOR_TASK_VALIDATION,
            )
            task_validate_solution.save()

            form.instance.solution_file = code_file
            form.instance.last_validate_solution = task_validate_solution
            form.save()

            messages.success(self.request, '???????????? ??????????????????')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course'] = get_object_or_404(
            Course, slug=self.kwargs.get('slug', None)
        )
        return context

    def get_success_url(self):
        return self.request.path_info


class CourseTaskTestView(TemplateView, TemplateResponseMixin, View):
    task = None
    course = None
    template_name = 'task/task_tests_create_update.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course'] = get_object_or_404(Course, slug=self.kwargs['slug'])
        context['task'] = get_object_or_404(CourseTask,
                                            id=self.kwargs.get('id', None))
        return context

    def dispatch(self, request, *args, **kwargs):
        self.task = get_object_or_404(CourseTask,
                                      id=self.kwargs.get('id', None))
        self.course = get_object_or_404(Course,
                                        slug=self.kwargs.get('slug', None))
        return super(CourseTaskTestView, self).dispatch(request=request)

    def get_formset(self, *args):
        formset = CourseTaskTestFormSet(
            *args,
            instance=self.task,
        )
        for form in formset:
            form.fields['content'].label = '???????????????????? ??????????:'
            form.fields['DELETE'].label = '?????????????? ???????? ????????'

        return formset

    def get(self, request, *args, **kwargs):
        if self.request.user != Course.objects.get(slug=self.kwargs.get('slug', None)).owner:
            raise Http404
        formset = self.get_formset()
        return self.render_to_response({'course': self.course, 'task': self.task, 'formset': formset})

    def post(self, request, *args, **kwargs):
        formset = self.get_formset(request.POST, request.FILES)
        task = get_object_or_404(CourseTask, id=self.kwargs.get('id', None))
        for form in formset:
            form.instance.task = task
        if formset.is_valid():
            formset.save()
            messages.success(request, '?????????? ??????????????????')

            c_f = task.solution_file
            c_f.pk = None
            c_f.save()

            if len(formset) > 0:
                task_validate_solution = CourseSolution.objects.create(
                    author=self.request.user,
                    code_file=c_f,
                    course=task.course,
                    course_task=task,
                    task=task,
                    node=1,
                    event_type=SolutionEventType.AUTHOR_TASK_VALIDATION,
                )
                task_validate_solution.save()
                if task.last_validate_solution:
                    task.last_validate_solution = task_validate_solution
                else:
                    task.last_validate_solution = task_validate_solution
                task.save()

            return HttpResponseRedirect(reverse('course_task_tests', kwargs=self.kwargs))
        messages.error(request, '???????????? ?????? ???????????????????? ????????????')
        return self.render_to_response({'course': self.course, 'task': self.task, 'formset': formset})


class ContestListView(ListView):
    template_name = 'contest/contest_list_edit.html'
    model = Contest

    def get_queryset(self):
        qs = Contest.objects.all()
        course = Course.objects.get(slug=self.kwargs['slug'])
        if course.owner != self.request.user:
            raise Http404
        return qs.filter(course=Course.objects.get(slug=self.kwargs['slug']))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ContestForm
        context['course'] = get_object_or_404(
            Course, slug=self.kwargs.get('slug', None)
        )
        return context


class ContestCreateView(TemplateView, LoginRequiredMixin):
    template_name = 'contest/contest_create.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ContestForm
        context['course'] = get_object_or_404(
            Course, slug=self.kwargs.get('slug', None)
        )
        return context


class ContestCreateFormHandle(FormView):
    form_class = ContestForm
    template_name = 'contest/contest_create.html'

    def form_valid(self, form):
        if not self.request.user.is_authenticated:
            raise Http404
        if form.is_valid():
            form.instance.course = get_object_or_404(
                Course, slug=self.kwargs.get('slug', None)
            )
            form.save()
            messages.success(self.request, '?????????????? ????????????')
        else:
            messages.error(self.request, '?????????????????? ???????????? ?????? ???????????????? ????????????????')
        return super(ContestCreateFormHandle, self).form_valid(form)

    def get_success_url(self):
        return reverse('contest_list_edit', kwargs=self.kwargs)


class ContestUpdateView(UpdateView, LoginRequiredMixin):
    model = Contest
    template_name = 'contest/contest_update.html'
    form_class = ContestForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course'] = get_object_or_404(
            Course, slug=self.kwargs.get('slug', None)
        )
        return context

    def get_object(self, queryset=None):
        # course = Course.objects.get(self.kwargs['slug'])
        # if course.owner != self.request.user:
        #     raise Http404

        return get_object_or_404(
            Contest, id=self.kwargs.get('id', None)
        )

    def form_valid(self, form):
        if form.is_valid():
            form.save()
            messages.success(self.request, '?????????????? ?????????????? ????????????????')
        else:
            messages.error(self.request, '?????????????????? ???????????? ?????? ???????????????????? ????????????????')
        return super().form_valid(form)

    def get_success_url(self):
        return self.request.path_info


class ContestTaskListEditView(TemplateView, LoginRequiredMixin):
    template_name = 'contest/contest_task_choice.html'

    # noinspection DuplicatedCode
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if not self.request.user.is_authenticated:
            raise Http404
        context['contest'] = get_object_or_404(
            Contest, id=self.kwargs.get('id', None)
        )
        context['course'] = get_object_or_404(
            Course, slug=self.kwargs.get('slug', None)
        )
        context['form'] = ContestTaskChoiceForm(instance=Contest.objects.get(id=self.kwargs['id']))
        context['form'].fields['tasks'].queryset = CourseTask.objects.filter(
            course=context['course'],
        )
        return context


class ContestTaskListFormHandle(FormView):
    form_class = ContestTaskChoiceForm
    template_name = 'contest/contest_task_choice.html'

    def dispatch(self, request, *args, **kwargs):
        if request.POST.get('tasks') is None:
            messages.error(self.request, '???? ???????????????????????? ?????????? ???????? ???????? ???? ???????? ????????????!')
            return HttpResponseRedirect(reverse('contest_edit_tasks', kwargs=self.kwargs))
        return super().dispatch(request, **kwargs)

    def form_valid(self, form):
        contest = get_object_or_404(
            Contest,
            id=self.kwargs.get('id', None)
        )

        contest.tasks.remove(*contest.tasks.all())
        for task in form.cleaned_data['tasks']:
            contest.tasks.add(task)

        contest.save()
        messages.success(self.request, '???????????? ?????????? ????????????????')
        return super(ContestTaskListFormHandle, self).form_valid(form)

    def get_success_url(self):
        return reverse('contest_edit_tasks', kwargs=self.kwargs)


class ContestSolutionsListView(ListView):
    model = ContestSolution
    template_name = 'contest/contest_solutions.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if not self.request.user.is_authenticated:
            raise Http404
        context['course'] = get_object_or_404(
            Course, slug=self.kwargs.get('slug', None)
        )
        context['contest'] = get_object_or_404(
            Contest, id=self.kwargs.get('id', None)
        )
        return context

    def get_queryset(self):
        qs = ContestSolution.objects.all()
        contest = get_object_or_404(
            Contest,
            id=self.kwargs.get('id', None)
        )
        return qs.filter(participant__contest=contest)


class ContestSolutionDetailView(DetailView):
    model = ContestSolution
    template_name = 'contest/contest_solution_detail.html'
    context_object_name = 'solution'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if not self.request.user.is_authenticated:
            raise Http404
        context['contest'] = get_object_or_404(
            Contest, id=self.kwargs.get('id', None)
        )
        context['course'] = get_object_or_404(
            Course, slug=self.kwargs.get('slug', None)
        )

        context['action_rejudge_form'] = ContestActionSolutionRejudge
        context['action_delete_participant_form'] = ContestActionDeleteParticipant
        return context

    def get_object(self, queryset=None):
        return get_object_or_404(
            ContestSolution,
            id=self.kwargs.get('solution_id', None)
        )


class ContestActionSolutionRejudgeFormHandle(FormView):
    template_name = 'contest/contest_solution_detail.html'
    form_class = ContestActionSolutionRejudge

    def form_valid(self, form):
        messages.success(self.request, '?????????????? ???????? ???????????????????? ???? ????????????????????????')
        solution = get_object_or_404(
            ContestSolution,
            id=self.kwargs.get('solution_id', None)
        )
        solution.status = Status.WAIT_FOR_CHECK
        solution.verdict = Verdict.EMPTY_VERDICT
        solution.verdict_text = '?????????????? ???? ??????????????????'
        solution.save()
        return super().form_valid(form=form)

    def get_success_url(self):
        return reverse('contest_solution_detail', kwargs=self.kwargs)


class ContestActionDeleteParticipantFormHandle(FormView):
    template_name = 'contest/contest_solution_detail.html'
    form_class = ContestActionDeleteParticipant

    def form_valid(self, form):
        reason = form.cleaned_data['reason']
        solution = get_object_or_404(
            ContestSolution,
            id=self.kwargs.get('solution_id', None)
        )
        solution.participant.deleted = True
        solution.participant.delete_reason = reason
        solution.participant.save()
        return super().form_valid(form=form)

    def get_success_url(self):
        return reverse('contest_solutions_list', kwargs={
            'slug': self.kwargs['slug'],
            'id': self.kwargs['id'],
        })


class ContestParticipantRegistration(TemplateView):
    template_name = 'contest/contest_participant_registration.html'

    def dispatch(self, request, *args, **kwargs):
        contest = Contest.objects.get(id=self.kwargs.get('id', None))
        if self.request.user.is_authenticated:

            if ContestParticipant.objects.filter(
                    user=self.request.user,
                    contest=Contest.objects.get(id=self.kwargs.get('id', None))
            ).count() > 0:
                if contest.status == ContestStatus.WAIT_FOR_START:
                    return HttpResponseRedirect(
                        reverse('contest_wait_room', kwargs=self.kwargs)
                    )
                else:
                    return HttpResponseRedirect(
                        reverse('contest_participant_task_list', kwargs=self.kwargs)
                    )

        return super(ContestParticipantRegistration, self).dispatch(request, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['contest'] = get_object_or_404(
            Contest, id=self.kwargs.get('id', None)
        )
        context['form'] = ContestParticipantRegistrationForm
        context['already_participant'] = False

        if self.request.user.is_authenticated:
            if ContestParticipant.objects.filter(
                    contest=context['contest'],
                    user=self.request.user,
            ).count() > 0:
                context['already_participant'] = True
        return context


class ContestParticipantRegistrationFormHandle(FormView):
    form_class = ContestParticipantRegistrationForm
    template_name = 'contest/contest_participant_registration.html'

    def form_valid(self, form):
        participant = ContestParticipant.objects.create(
            contest=Contest.objects.get(id=self.kwargs['id'], ),
            user=self.request.user,
        )
        participant.save()
        return super().form_valid(form=form)

    def get_success_url(self):
        return reverse('contest_participant_task_list', kwargs=self.kwargs)


class ContestParticipantMixin(TemplateView):
    object_list = None
    # object = None
    template_name = ''

    def dispatch(self, request, *args, **kwargs):
        try:
            if self.get_participant() is not None:
                if self.get_participant().deleted:
                    return HttpResponseRedirect(
                        reverse('contest_participant_deleted', kwargs=self.kwargs)
                    )
        except ObjectDoesNotExist:
            pass
        # if self.get_contest().status == ContestStatus.WAIT_FOR_START:
        #     if self.request.path_info != reverse('contest_wait_room', kwargs=self.kwargs):
        #         return HttpResponseRedirect(
        #             reverse('contest_wait_room', kwargs=self.kwargs)
        #         )
        return super().dispatch(request=request, **kwargs)

    def get_contest(self):
        return get_object_or_404(
            Contest, id=self.kwargs.get('id', None)
        )

    def get_contest_status(self):
        return self.get_contest().status

    def get_participant(self):
        try:
            return ContestParticipant.objects.get(
                contest=self.get_contest(),
                user=self.request.user
            )
        except:
            return None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['contest'] = self.get_contest()
        try:
            context['participant'] = self.get_participant()
            c = context['contest']
            p = context['participant']

            class TableTaskElem:
                def __init__(self):
                    self.try_count = 0
                    self.all_try_count = None

            a = [TableTaskElem() for _ in range(c.tasks.all().count())]
            for i, t in enumerate(c.tasks.all()):

                s = set()

                sol = ContestSolution.objects.filter(
                    task=t.id,
                    verdict=Verdict.CORRECT_SOLUTION,
                )

                for par in sol:
                    s.add(par.participant.user.username)

                a[i].all_try_count = len(s)
                print()
                if ContestSolution.objects.filter(
                        participant=p,
                        task_id=t.id,
                ).count() > 0:
                    a[i].try_count = -1
                    if ContestSolution.objects.filter(
                            participant=p,
                            verdict=Verdict.CORRECT_SOLUTION,
                        task_id=t.id,
                    ).count() > 0:

                        a[i].try_count = 1
            context['table_task'] = a
            for x in a:
                print(x)
        except ObjectDoesNotExist:
            context['participant'] = None
        return context


class ContestParticipantWaitRoom(ContestParticipantMixin):
    template_name = 'contest/contest_participant_wait_room.html'


class ContestParticipantTaskListView(ListView, ContestParticipantMixin):
    model = CourseTask
    template_name = 'contest/contest_participant_task_list.html'

    def get_queryset(self):
        return self.get_contest().tasks.all()


class ContestParticipantTaskDetailView(DetailView, ContestParticipantMixin):
    model = CourseTask
    template_name = 'contest/contest_participant_task_detail.html'
    context_object_name = 'task'

    def get_object(self, queryset=None):
        return get_object_or_404(
            CourseTask,
            id=self.kwargs.get('task_id', None)
        )

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().get(request, *args, **kwargs)


class ContestParticipantSendSolutionFileView(ContestParticipantMixin):
    template_name = 'contest/contest_participant_send_solution.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ContestSolutionSendSolutionForm
        # print(dir(context['form']))
        # print(dir(context['form'].declared_fields['task']))
        context['form'].declared_fields['task'].queryset = self.get_contest().tasks.all()
        # context['form'].fields['task'].queryset = self.get_contest().tasks.all()
        return context


class ContestParticipantSendCodeView(ContestParticipantMixin):
    template_name = 'contest/contest_participant_send_code.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ContestSolutionSendCodeForm
        context['form'].declared_fields['task'].queryset = self.get_contest().tasks.all()
        return context


class ContestParticipantSolutionSendSolutionFileFormHandle(FormView, ContestParticipantMixin):
    template_name = 'contest/contest_participant_send_solution.html'
    form_class = ContestSolutionSendSolutionForm

    # noinspection DuplicatedCode
    def form_valid(self, form):
        print('\n\n\n\n')

        if form.is_valid():
            code_file = CodeFile.objects.create(
                file=form.cleaned_data['file'],
                language=form.cleaned_data['language'],
                code=form.cleaned_data['file'].read().decode('utf-8'),
                file_name=form.cleaned_data['file'].name,
            )
            print(form.cleaned_data['file'].read().decode('utf-8'), )
            code_file.save()
            solution = ContestSolution.objects.create(
                participant=self.get_participant(),
                author=self.get_participant().user,
                code_file=code_file,
                task=form.cleaned_data['task'],
            )
            solution.save()
            p = self.get_participant()
            p.penalty += (datetime.datetime.now(
                datetime.timezone.utc) - self.get_contest().start_time).seconds // 60
            p.save()
            messages.success(self.request, '???????? ?????????????? ???????????????????? ???? ????????????????')
        else:
            messages.error(self.request, '?????? ???????????????? ?????????????? ?????????????????? ????????????')

        return super(ContestParticipantSolutionSendSolutionFileFormHandle, self).form_valid(form=form)

    def get_success_url(self):
        return reverse('contest_participant_solution_list', kwargs=self.kwargs)


class ContestParticipantSolutionSendCodeFormHandle(FormView, ContestParticipantMixin):
    template_name = 'contest/contest_participant_send_code.html'
    form_class = ContestSolutionSendCodeForm

    # noinspection DuplicatedCode
    def form_valid(self, form):
        if form.is_valid():
            file_name = f'{str(uuid.uuid4())}.{lang_extension[form.cleaned_data["language"]]}'
            file = open(f'media/raw_code/{file_name}', 'w')
            file.write(form.cleaned_data['code'])
            file.close()
            f = File(file=file)
            f.open('r')
            code_file = CodeFile.objects.create(
                file=f,
                language=form.cleaned_data['language'],
                code=form.cleaned_data['code'],
                file_name=file_name,
            )
            f.close()
            code_file.save()
            solution = ContestSolution.objects.create(
                participant=self.get_participant(),
                author=self.get_participant().user,
                code_file=code_file,
                task=form.cleaned_data['task'],
            )
            solution.save()
            p = self.get_participant()
            p.penalty += (datetime.datetime.now(
                datetime.timezone.utc) - self.get_contest().start_time).seconds // 60
            p.save()
            messages.success(self.request, '?????? ?????? ?????????????????? ???? ????????????????')
        else:
            messages.error(self.request, '?????? ???????????????? ???????? ?????????????????? ????????????')
        return super(ContestParticipantSolutionSendCodeFormHandle, self).form_valid(form=form)

    def get_success_url(self):
        return reverse('contest_participant_solution_list', kwargs=self.kwargs)


class ContestParticipantSolutionListView(ListView, ContestParticipantMixin):
    model = ContestSolution
    template_name = 'contest/contest_participant_solution_list.html'

    def get_queryset(self):
        qs = ContestSolution.objects.all()
        print(qs)
        return qs.filter(
            participant=self.get_participant(),
            participant__contest=self.get_contest(),
        )

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        return super().get(request, *args, **kwargs)


class ContestParticipantSolutionDetailView(DetailView, ContestParticipantMixin):
    model = ContestSolution
    template_name = 'contest/contest_participant_solution_detail.html'
    context_object_name = 'solution'

    def get_object(self, queryset=None):
        s = get_object_or_404(
            ContestSolution,
            id=self.kwargs.get('solution_id', None),
        )
        if s.participant.user != self.request.user:
            raise Http404
        return s

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().get(request, *args, **kwargs)


class ContestParticipantScoreboardView(ContestParticipantMixin):
    template_name = 'contest/contest_participant_scoreboard.html'

    class TableElement:
        def __init__(self):
            self.is_solved = None
            self.try_count = None
            self.points = None

    class User:
        def __init__(self):
            self.username = None
            self.stats: ContestParticipantScoreboardView.TableElement = None
            self.task_solved = None
            self.points = 0
            self.type = 0
            self.penalty = 0

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        participants = ContestParticipant.objects.filter(
            contest=self.get_contest(),
        )
        tasks = self.get_contest().tasks.all()
        context['tasks'] = tasks
        table = []
        for participant in participants:
            user = self.User()
            user.username = participant.user.username
            stats = [self.TableElement() for _ in range(len(tasks))]
            solved_cnt = 0
            points = 0
            for i in range(len(tasks)):
                solutions = ContestSolution.objects.filter(
                    participant=participant,
                    task=tasks[i],
                )
                stats[i].try_count = len(solutions)
                stats[i].points = max([s.points for s in solutions] + [0])
                print([s.points for s in solutions])
                points += stats[i].points
                stats[i].is_solved = True if Verdict.CORRECT_SOLUTION in [s.verdict for s in solutions] else False
                if stats[i].is_solved:
                    solved_cnt += 1
            user.stats = stats
            user.task_solved = solved_cnt
            user.points = points
            user.penalty = participant.penalty
            if context['contest'].status == ContestStatus.FINISHED:
                user.type = 0
            table.append(user)
        table.sort(key=lambda x: x.task_solved, reverse=True)
        context['table'] = table
        print(table[0].points)
        return context


class ContestParticipantDeleteView(TemplateView):
    template_name = 'contest/contest_participant_deleted.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['participant'] = ContestParticipant.objects.get(
            contest=Contest.objects.get(id=self.kwargs['id']),
            user=self.request.user,
        )
        return context


def contest_condition_update_view(request, id):
    contest = Contest.objects.get(id=id)
    now_time = timezone.now() + datetime.timedelta(hours=3)
    start = contest.start_time + datetime.timedelta(hours=3)
    finish = contest.start_time + contest.duration + datetime.timedelta(hours=3)
    data = {
        'contest_status': 'wait_for_start',
        'alert_action': 0,
        'alert_message': None,
        'timer': None,
    }
    if now_time < start:
        if contest.status == ContestStatus.WAIT_FOR_START:
            pass
        else:
            contest.status = ContestStatus.WAIT_FOR_START
    if start <= now_time <= finish:
        if contest.status == ContestStatus.ACTIVE:
            data['timer'] = str(finish - now_time).split('.')[0]
        else:
            contest.status = ContestStatus.ACTIVE
            data['contest_status'] = 'active'
            data['alert_action'] = 1
            data['alert_message'] = '???????????????????????? ????????????????'

    if finish < now_time:
        if contest.status == ContestStatus.FINISHED:
            pass
        else:
            contest.status = ContestStatus.FINISHED
            data['contest_status'] = 'finished'
            data['alert_action'] = 2
            data['alert_message'] = '???????????????????????? ??????????????????????'
            data['timer'] = '?????????? ??????????'

    contest.save()
    return JsonResponse(data, status=200)


def update_contest_solutions(request, id):
    class TableElement:
        def __init__(self):
            self.color = None
            self.percent = None
            self.verdict_text = None
            self.value = None
            self.status = None

    color = (
        '#FFFF00',
        '#EEFF00',
        '#DDFF00',
        '#CCFF00',
        '#BBFF00',
        '#AAFF00',
        '#99FF00',
        '#88FF00',
        '#77FF00',
        '#66FF00',
        '#55FF00',
        '#44FF00',
        '#33FF00',
        '#22FF00',
        '#11FF00',
        '#00FF00',
        '#00FF11',
    )

    contest = Contest.objects.get(id=id)
    user = request.user
    solutions = ContestSolution.objects.filter(
        participant__user=user,
        participant__contest=contest,
    )
    task = None
    n = len(solutions)
    if n > 0:
        task = solutions[0].task
    test_count = task.tests.count()
    table = [[0, 0, 0, 0, 0] for _ in range(n)]
    for i, s in enumerate(solutions):
        cur_test = s.cur_test
        t_c = s.task.tests.count()
        percent = f'{int((cur_test / t_c) * 100)}'
        table[i][1] = percent
        cur_color = color[(len(color) - 1) * int(percent) // 100]
        table[i][2] = s.verdict_text
        table[i][4] = s.status
        if s.status == Status.QUEUED:
            table[i][3] = '?? ??????????????'
        if s.status == Status.IN_PROGRESS:
            table[i][3] = f'<div class="progress" style="width: 120px">\
                                <div class="progress-bar" role="progressbar" style="width: {table[i][1]}%; background-color: {cur_color}"\
                                     aria-valuenow="75" aria-valuemin="0" aria-valuemax="100"></div>\
                            </div>'
        elif s.status == Status.WAIT_FOR_CHECK:
            table[i][3] = f'<div class="spinner-border" role="status" style="width: 20px; height: 20px">\
                                <span class="sr-only"></span>\
                            </div>'
        elif s.status == Status.CHECK_FAILED:
            table[i][3] = f'<i class="bi bi-x-square" style="color: #ff5945"></i>'
        elif s.status == Status.CHECK_SUCCESS:
            table[i][3] = f'<i class="bi bi-check-square" style="color: #56ff20"></i>'

    return JsonResponse(data={'table': table}, status=200)


class ContestParticipantDescriptionView(ContestParticipantMixin):
    template_name = 'contest/contest_participant_description.html'


# Here starts views which are handle user's interface requests


class CourseListView(ListView):
    model = Course
    template_name = 'course/course_student_list.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['channel'] = get_object_or_404(
            Channel,
            slug=self.kwargs.get('slug', None),
        )
        return context

    def get_queryset(self):
        qs = Course.objects.all()
        channel = get_object_or_404(
            Channel,
            slug=self.kwargs.get('slug', None),
        )
        return qs.filter(channel=channel)


class CourseModuleDetailView(DetailView):
    model = Module
    template_name = 'module/module.html'
    context_object_name = 'module'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course'] = get_object_or_404(
            Course,
            slug=self.kwargs.get('slug', None)
        )

        m = get_object_or_404(
            Module,
            course=context['course'],
            order=self.kwargs.get('order', None),
        )
        if self.request.user.is_authenticated:
            if Student.objects.filter(
                    user=self.request.user,
                    course=context['course']
            ).count() > 0:
                s = Student.objects.get(
                    user=self.request.user,
                    course=context['course'],
                )
                s.cur_module = self.kwargs.get('order', None)
                s.save()
                context['student'] = s
        context['prev_module'] = None if Module.objects.filter(course=
                                                               context['course'],
                                                               order=
                                                               m.order - 1).count() == 0 else Module.objects.get(
            course=
            context['course'], order=m.order - 1)
        context['next_module'] = None if Module.objects.filter(course=
                                                               context['course'],
                                                               order=
                                                               m.order + 1).count() == 0 else Module.objects.get(
            course=
            context['course'], order=m.order + 1)
        return context

    def get_object(self, queryset=None):
        slug = self.kwargs.get('slug', None)
        order = self.kwargs.get('order', None)
        return get_object_or_404(
            Module,
            course=Course.objects.get(slug=slug),
            order=order,
        )


class CourseTaskListView(ListView):
    model = CourseTask
    template_name = 'course/course_student_task_list.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course'] = get_object_or_404(Course, slug=self.kwargs.get('slug', None))
        return context

    def get_queryset(self):
        qs = CourseTask.objects.all()
        return qs.filter(course=get_object_or_404(Course, slug=self.kwargs.get('slug', None)))


class CourseTaskDetailView(DetailView):
    model = CourseTask
    template_name = 'course/course_student_task_detail.html'
    context_object_name = 'task'

    # noinspection DuplicatedCode
    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course'] = get_object_or_404(Course, slug=self.kwargs.get('slug', None))
        context['solutions'] = None
        context['form'] = CourseTaskSendSolutionForm
        if self.request.user.is_authenticated:
            if Student.objects.filter(
                    user=self.request.user,
                    course=context['course']
            ).count() > 0:
                context['is_student'] = True
            context['solutions'] = CourseSolution.objects.filter(
                course_task=get_object_or_404(CourseTask, id=self.kwargs.get('task_id', None)),
                author=self.request.user,
            )
        return context

    def get_object(self, queryset=None):
        return get_object_or_404(CourseTask, id=self.kwargs.get('task_id'))


class CourseSolutionDetailView(DetailView):
    model = CourseSolution
    template_name = 'course/course_student_solution_detail.html'
    context_object_name = 'current_solution'

    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return HttpResponseRedirect(
                reverse('course_student_task_detail', kwargs={
                    'slug': self.kwargs.get('slug'),
                    'task_id': self.kwargs.get('task_id'),
                })
            )
        return super(CourseSolutionDetailView, self).dispatch(self.request, **kwargs)

    # noinspection DuplicatedCode
    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course'] = get_object_or_404(Course, slug=self.kwargs.get('slug', None))
        context['solutions'] = None
        context['form'] = CourseTaskSendSolutionForm
        if self.request.user.is_authenticated:
            if Student.objects.filter(
                    user=self.request.user,
                    course=context['course']
            ).count() > 0:
                context['is_student'] = True
            context['solutions'] = CourseSolution.objects.filter(
                course_task=get_object_or_404(CourseTask, id=self.kwargs.get('task_id', None)),
                author=self.request.user,
            )
        context['task'] = get_object_or_404(CourseTask, id=self.kwargs.get('task_id', None))
        return context

    def get_object(self, queryset=None):
        return get_object_or_404(CourseSolution, id=self.kwargs.get('solution_id'))


class CourseTaskSendSolutionFormHandle(FormView):
    form_class = CourseTaskSendSolutionForm
    template_name = 'course/course_student_task_detail.html'

    def form_valid(self, form):

        if not self.request.user.is_authenticated:
            raise Http404

        if form.is_valid():
            cd = form.cleaned_data
            file, code, code_file = None, None, None
            if cd['code'] and not cd['file']:
                code = cd['code']
                file_name = f'{str(uuid.uuid4())}.{lang_extension[form.cleaned_data["language"]]}'
                file__ = open(f'media/raw_code/{file_name}', 'w')
                file__.write(code)
                file__.close()
                file = File(file=file__)
                file.open('r')
                code_file = CodeFile.objects.create(
                    file=file,
                    language=cd['language'],
                    code=code,
                    file_name=file_name,
                )
                file.close()
                code_file.save()

            if cd['file'] and not cd['code']:
                file = cd['file']
                code = file.read().decode('utf-8')
                code_file = CodeFile.objects.create(
                    file=file,
                    language=cd['language'],
                    code=code,
                    file_name=file.name,
                )

            if code_file:
                code_file.save()

                task = get_object_or_404(CourseTask, id=self.kwargs.get('task_id'))
                solution = CourseSolution.objects.create(
                    course=get_object_or_404(Course, slug=self.kwargs.get('slug')),
                    course_task=task,
                    code_file=code_file,
                    task=task,
                    author=self.request.user,
                )
                solution.save()

                messages.success(self.request, '?????????????? ???????????????????? ???? ????????????????')

            else:
                messages.warning(self.request, '???????????????????? ???????????????? ?????? ?????? ???????????????????? ????????')

        else:
            messages.error(self.request, '???????????? ?????? ???????????????? ??????????????')
        return super().form_valid(form=form)

    def get_success_url(self):
        return reverse('course_student_task_detail', kwargs=self.kwargs)


class ContestStudentListView(ListView):
    model = Contest
    template_name = 'contest/contest_participant_list.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course'] = get_object_or_404(Course, slug=self.kwargs.get('slug', None))
        return context

    def get_queryset(self):
        qs = Contest.objects.all()
        return qs.filter(course=get_object_or_404(Course, slug=self.kwargs.get('slug', None)))


class ChannelListViewMain(ListView):
    model = Channel
    template_name = 'channel/channel_list.html'


class CourseListViewMain(ListView):
    model = Course
    template_name = 'course/course_list.html'


class ContestListViewMain(ListView):
    model = Contest
    template_name = 'contest/contest_list.html'
